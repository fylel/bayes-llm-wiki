"""LLM 呼叫與執行紀錄（RunLog）。

- LLM：包一層 aisuite，統一 chat() / json() 介面；json() 會自動擷取並解析 JSON，失敗就重試。
- RunLog：記錄每個節點（node）每一次嘗試的結果，最後可輸出成 run_log.json / run_log.md，
  用來回答「哪個節點最常出錯」。
"""
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path


class RunLog:
    def __init__(self):
        self.events = []
        self.t0 = time.time()

    def add(self, node, status, detail="", **extra):
        ev = {"t": round(time.time() - self.t0, 1), "node": node,
              "status": status, "detail": str(detail)[:500]}
        ev.update(extra)
        self.events.append(ev)
        mark = {"ok": "✓", "fail": "✗", "retry": "↻", "info": "·", "flag": "⚑"}.get(status, "·")
        print(f"[{ev['t']:>6}s] {mark} {node:<16} {ev['detail'][:110]}")

    # ---- 統計 ----
    def fail_counts(self):
        c = Counter(e["node"] for e in self.events if e["status"] in ("fail", "retry"))
        return c.most_common()

    def node_totals(self):
        tot = defaultdict(lambda: {"ok": 0, "fail": 0})
        for e in self.events:
            if e["status"] == "ok":
                tot[e["node"]]["ok"] += 1
            elif e["status"] in ("fail", "retry"):
                tot[e["node"]]["fail"] += 1
        return dict(tot)

    def save(self, out_dir, name="run_log"):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{name}.json").write_text(json.dumps(self.events, ensure_ascii=False, indent=1), encoding="utf-8")
        lines = [f"# 執行紀錄：{name}", "", "## 各節點成功／失敗次數", "",
                 "| 節點 | 成功 | 失敗或重試 | 失敗率 |", "|---|---|---|---|"]
        for node, v in sorted(self.node_totals().items(), key=lambda kv: -kv[1]["fail"]):
            n = v["ok"] + v["fail"]
            lines.append(f"| {node} | {v['ok']} | {v['fail']} | {v['fail'] / n:.0%} |")
        lines += ["", "## 逐步紀錄", "", "| 時間(s) | 節點 | 狀態 | 說明 |", "|---|---|---|---|"]
        for e in self.events:
            d = e["detail"].replace("|", "／").replace("\n", " ")
            lines.append(f"| {e['t']} | {e['node']} | {e['status']} | {d[:200]} |")
        (out / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
        return out / f"{name}.md"


def extract_json(text):
    """從 LLM 回覆中擷取第一個完整 JSON 物件（容忍 ```json 包裝與前後廢話）。"""
    text = re.sub(r"```(?:json)?", "", text)
    start = text.find("{")
    if start < 0:
        raise ValueError("回覆中找不到 JSON")
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("JSON 不完整（可能被截斷）")


class LLM:
    """provider / model 用法與課堂 Demo07（aisuite）相同。mock 傳入物件時改用假模型離線測試。"""

    def __init__(self, provider="groq", model="openai/gpt-oss-120b",
                 temperature=0.3, log=None, mock=None, max_tokens=8192):
        self.provider, self.model, self.temperature = provider, model, temperature
        self.max_tokens = max_tokens
        self.log = log or RunLog()
        self.mock = mock
        self.calls = 0
        if mock is None:
            import aisuite as ai
            self.client = ai.Client()

    def chat(self, system, user, tag=""):
        self.calls += 1
        if self.mock is not None:
            return self.mock.reply(system, user, tag)
        attempt = 0
        while attempt < 4:
            try:
                kw = {"temperature": self.temperature, "max_tokens": self.max_tokens}
                if "gpt-oss" in self.model:  # 推理模型：降低思考量，把 token 留給正文，避免輸出被截斷
                    kw["reasoning_effort"] = "low"
                r = self.client.chat.completions.create(
                    model=f"{self.provider}:{self.model}",
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}], **kw)
                return r.choices[0].message.content
            except Exception as e:  # 免費額度常見 rate limit，等一下再試
                msg = str(e)
                # 用 HTTP 狀態碼判斷，不能只比對子字串（限流訊息裡的 "Requested 2400" 也含有 "400"）
                m = re.search(r"Error code: (\d{3})", msg)
                code = int(m.group(1)) if m else None
                if code in (400, 401, 403, 404) or "model_not_found" in msg or "decommissioned" in msg:
                    raise RuntimeError(f"模型或金鑰設定錯誤，重試沒有用，請檢查 PROVIDER / MODEL / 金鑰：{e}") from e
                # 照 Groq 建議的時間等待，格式如 1h2m3.4s、14m13.2s、7.5s、520ms
                hint = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m(?!s))?([\d.]+)(ms|s)", msg)
                wait = ((int(hint.group(1) or 0) * 3600 + int(hint.group(2) or 0) * 60
                         + float(hint.group(3)) / (1000 if hint.group(4) == "ms" else 1) + 1)
                        if hint else 10 * (attempt + 1))
                if code == 413:
                    self.log.add(tag or "llm", "info", f"單次請求過大，停止：{msg[:200]}")
                    raise RuntimeError(f"單次請求超過每分鐘 token 上限，重試沒有用：{msg[:400]}") from e
                if "tokens per day" in msg:  # 每日額度會逐步回補：等待時間合理就等，不算重試次數
                    if not hint or wait > 3600:
                        self.log.add(tag or "llm", "info", f"每日額度用完，停止：{msg[:200]}")
                        raise RuntimeError(f"已用完每日 token 額度：{msg[:400]}") from e
                    self.log.add(tag or "llm", "info", f"每日額度用完，等待回補 {wait / 60:.1f} 分鐘")
                    time.sleep(wait)
                    continue
                # 限流等待記為 info：這是額度問題，不算節點本身出錯
                self.log.add(tag or "llm", "info", f"API 限流或錯誤，{wait:.0f}s 後重試：{msg[:300]}")
                time.sleep(wait)
                attempt += 1
        raise RuntimeError("LLM API 連續失敗")

    def json(self, system, user, tag="", retries=2):
        """要求 JSON 輸出；解析失敗時把錯誤丟回給模型重試，並記錄到 RunLog。"""
        msg = user
        for attempt in range(retries + 1):
            raw = self.chat(system + "\n\n只輸出一個 JSON 物件，不要任何其他文字。", msg, tag)
            try:
                return extract_json(raw)
            except Exception as e:
                if "Invalid \\escape" in str(e):  # LaTeX 反斜線沒跳脫（如 \mid、\sum）：本地補成 \\ 再解析，省一次 API 呼叫
                    try:
                        # 同一份輸出裡的 \frac、\neq、\theta 也沒跳脫，會被誤當成 \f、\n、\t：後面接英文字母就視為 LaTeX
                        fixed = extract_json(re.sub(r'(?<!\\)\\(?![\\"/]|u[0-9a-fA-F]{4}|[bfnrt](?![a-zA-Z]))', r"\\\\", raw))
                        self.log.add(tag, "info", f"JSON 有未跳脫的反斜線，已在本地修復：{e}")
                        return fixed
                    except Exception:
                        pass
                self.log.add(tag, "retry", f"JSON 解析失敗（第 {attempt + 1} 次）：{e}")
                hint = "內容太長被截斷了，請把每個欄位寫得更精簡（每頁 400 字內）。" if "截斷" in str(e) else ""
                msg = user + f"\n\n上一次的輸出無法解析成 JSON（{e}）。{hint}請只輸出合法 JSON。"
        raise ValueError(f"{tag}: 多次無法取得合法 JSON")
