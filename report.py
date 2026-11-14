"""繳交用的輔助函式：畫流程圖、比較兩次執行、產生繳交說明草稿。"""
import base64
from pathlib import Path

import pandas as pd

from slide_graph import GRAPH_MERMAID, check_record


def show_graph(mermaid=GRAPH_MERMAID):
    """用 mermaid.ink 把流程圖轉成圖片顯示（Colab 的 Markdown 不支援 mermaid）。"""
    from IPython.display import Image, display
    code = base64.urlsafe_b64encode(mermaid.encode("utf-8")).decode("ascii")
    display(Image(url=f"https://mermaid.ink/img/{code}?bgColor=white&width=900"))


def compare_runs(logs, calls=None):
    """logs = {"v1": RunLog, "v2": RunLog}，calls = {"v1": LLM 呼叫數, ...} → 各節點失敗次數對照表。"""
    rows = {}
    for name, log in logs.items():
        for node, v in log.node_totals().items():
            rows.setdefault(node, {})[f"{name} 失敗"] = v["fail"]
            rows[node][f"{name} 總次數"] = v["ok"] + v["fail"]
        if calls:
            rows.setdefault("（LLM 呼叫數）", {})[f"{name} 總次數"] = calls[name]
    df = pd.DataFrame(rows).T.fillna(0).astype(int)
    fail_cols = [c for c in df.columns if c.endswith("失敗")]
    return df.sort_values(fail_cols[0], ascending=False) if fail_cols else df


def make_submission(out_dir, wiki, results, logs, cfg, ingest_records):
    """把 1~5 項自動整理好；第 6 項（反思）留下你的實際數據與待填的問題。"""
    out = Path(out_dir)
    calls = {k: r.get("llm_calls") for k, r in results.items() if r.get("llm_calls") is not None}
    df = compare_runs(logs, calls or None)
    table = "\n".join(["| 節點 | " + " | ".join(df.columns) + " |", "|---" * (len(df.columns) + 1) + "|"]
                      + [f"| {i} | " + " | ".join(str(v) for v in row) + " |" for i, row in df.iterrows()])
    v1, v2 = logs.get("v1"), logs.get("v2")
    worst = v1.fail_counts()[:3] if v1 else []
    ref = out / "reflection.md"  # 反思寫在 reflection.md，重新產生繳交說明時不會被覆蓋
    reflection = ref.read_text(encoding="utf-8").strip() if ref.exists() else f"""第一次執行（v1）被擋下最多次的節點：{worst}

- 哪一個節點最常出錯？〔依上面的數字寫，並舉一個實際被擋下的例子〕
- 發現問題後，把檢查往前移到哪一個步驟？〔例如：數字檢查從 check_slide 移到 draft 之前的 compute_facts；頁面名稱檢查從 slide 階段移到 check_plan〕
- 有沒有因此修改 workflow / graph？為什麼？〔比較 v1 與 v2 的失敗次數與 LLM 呼叫數〕"""
    disc = "\n".join(f"- **{r['source']}**：建議頁面 {[p['name'] for p in r['discussion'].get('proposed_pages', [])]}；"
                     f"我的回饋：{r['notes'] or '（照建議）'}；寫入 {r['written']}" for r in ingest_records)
    pages = "\n".join(f"- `{n}`：{wiki.title_and_summary(n)[0]}" for n in wiki.names())
    final = results.get("v2") or results.get("v1")
    md = f"""# 用 LLM Wiki 做一份教學 HTML 簡報 —— 貝氏統計入門

## 1. LLM Wiki 主題與簡短介紹
主題：**{cfg.topic}**。目標讀者是{cfg.audience}。
Wiki 由 LLM 依「先討論、後生成」的方式，從 {len(wiki.raw_names())} 篇原始資料整理出 {len(wiki.names())} 個互相連結的知識頁；
每頁都有一句話摘要（進 index.md）、公式、`[[連結]]` 與「來源」段落，所有變更記錄在 log.md。

頁面：
{pages}

## 2. LLM Wiki 連結或成果
- wiki.html（單頁瀏覽版，左側目錄可跳頁）：〔貼上連結〕
- 原始 Markdown（wiki/pages、index.md、log.md）：〔貼上 GitHub 連結〕

ingest 時的討論與我的回饋（節錄自 log.md）：
{disc}

## 3. 教學 HTML 簡報連結
〔貼上 slides.html 連結〕（← → 翻頁，N 顯示講者備註；每張頁尾列出依據的 Wiki 頁面，可點回 wiki.html 對照）

## 4. loop / graph 設計
見 notebook 中的流程圖。文字版：

取得資料 → ingest.discuss（先討論）→ 人工回饋 → ingest.generate（後生成）→ 規則檢查（不過重生一次）→ 更新 index/log →（下一篇）→ lint
→ plan 大綱 ⇄ check_plan → compute_facts → 每張：retrieve → draft ⇄ check_slide（規則 → 數字 → LLM 審稿，最多 {cfg.max_slide_attempts} 版）→ deck_review → render_html

- **重複執行的步驟**：ingest 對每篇資料各跑一次；retrieve→draft→check 對每張投影片各跑一次，且 draft⇄check 最多 {cfg.max_slide_attempts} 輪；plan⇄check_plan 最多 {cfg.max_plan_attempts} 輪。
- **需要檢查或重新生成的地方**：ingest 後（來源段落／標題）、lint（斷連結、頁面間矛盾、觀念錯誤）、check_plan（引用頁面是否存在、張數、範例是否都有用到）、check_slide（格式、數字、是否有 Wiki 依據、初學者是否看得懂）、deck_review（順序、重複）。
- **為什麼這樣設計**：便宜的規則檢查放前面、昂貴的 LLM 審稿放後面，規則沒過就不呼叫 LLM 審稿；數字一律交給 Python 計算，不信任 LLM 的算術；每張投影片都綁定 Wiki 頁面，讓簡報內容可以追溯回 Wiki。

## 5. 實際執行結果與檢查紀錄
設定：每版 {cfg.n_slides[0]}–{cfg.n_slides[1]} 張內容頁、retrieve 額外補 {cfg.k_extra} 頁、每張最多 {cfg.max_slide_attempts} 版；v1 由 LLM 自己算範例數字，v2 先由 Python 算好（compute_facts）。
各節點失敗次數（第一次執行 v1 vs 調整後 v2，完整逐步紀錄見 run_log_v1.md、run_log_v2.md）：

{table}

以下為 v2（最終版 slides.html）每張投影片的檢查紀錄（「第N版」指同一張投影片的第 N 次生成）：

{check_record(final) if final else ""}

## 6. 反思
{reflection}
"""
    p = out / "繳交說明.md"
    p.write_text(md, encoding="utf-8")
    return p
