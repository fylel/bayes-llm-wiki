"""LLM Wiki：資料取得、先討論後生成的 ingest、lint、搜尋與匯出。

Wiki 結構（仿 Karpathy 的 LLM Wiki 構想）：
    wiki/
      raw/          原始資料（不修改，只讀）
      pages/        LLM 維護的知識頁（Markdown，頁面間用 [[page-name]] 互連）
      index.md      所有頁面的目錄＋一句話摘要（查詢時先讀這裡）
      log.md        每次 ingest / lint 的時間序紀錄
"""
import datetime as dt
import html
import json
import re
from pathlib import Path

import requests

# 預設 6 篇來源（作業要求至少 5 篇），皆為英文維基百科條目，可自行替換或加入 PDF 文字。
DEFAULT_SOURCES = [
    {"name": "bayes_theorem", "title": "Bayes' theorem"},
    {"name": "base_rate_fallacy", "title": "Base rate fallacy"},
    {"name": "bayesian_inference", "title": "Bayesian inference"},
    {"name": "prior_probability", "title": "Prior probability"},
    {"name": "conjugate_prior", "title": "Conjugate prior"},
    {"name": "credible_interval", "title": "Credible interval"},
]

WIKI_STYLE = """你是一位統計學助教，負責維護一份「貝氏統計入門」的 LLM Wiki。
寫作規則：
1. 一律使用台灣習慣的繁體中文；專有名詞第一次出現寫「中文（英文）」，例如 後驗分佈（posterior distribution）。
2. 每頁開頭是 `# 標題`，接著一句話摘要（會被放進 index），再分段說明。
3. 公式用 LaTeX，行內用 $...$，獨立公式用 $$...$$。
4. 頁面之間用 [[page-name]] 互相連結，page-name 只能用小寫英文與連字號。
5. 每頁最後要有 `## 來源` 段落，列出依據的原始資料名稱（raw 檔名）。
6. 只寫原始資料支持的內容；原始資料沒寫的不要自己補數字。
7. 每頁精簡，600 字以內，寫給初學者看。"""


# 模型偶爾混用大陸用語；輸出前統一成台灣用語（公式不轉換）
TW_TERMS = {"似然": "概似", "分布": "分佈", "信息": "資訊"}


def to_tw(text):
    for a, b in TW_TERMS.items():
        text = text.replace(a, b)
    return text


# ------------------------------------------------------------------ 取得資料
def fetch_wikipedia(title, lang="en", max_chars=8000):
    """用 MediaWiki API 取純文字內容（不需爬 HTML）。"""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {"action": "query", "prop": "extracts", "explaintext": 1,
              "titles": title, "format": "json", "redirects": 1}
    import time
    for attempt in range(5):  # 維基百科連續請求太快會回 429，等一下再試
        r = requests.get(url, params=params, timeout=30,
                         headers={"User-Agent": "llm-wiki-homework/1.0 (course assignment)"})
        if r.status_code != 429:
            break
        wait = int(r.headers.get("Retry-After", 10 * (attempt + 1)))
        print(f"  維基百科限流（429），{wait} 秒後重試…")
        time.sleep(wait)
    r.raise_for_status()
    time.sleep(2)
    page = next(iter(r.json()["query"]["pages"].values()))
    text = page.get("extract", "")
    # 去掉參考文獻等尾段，減少雜訊
    text = re.split(r"\n== (See also|References|Further reading|External links|Notes) ==", text)[0]
    return text[:max_chars]


# ------------------------------------------------------------------ Wiki 儲存
class Wiki:
    LINK = re.compile(r"\[\[([a-z0-9\-]+)\]\]")

    def __init__(self, root="wiki"):
        self.root = Path(root)
        self.raw = self.root / "raw"
        self.pages = self.root / "pages"
        for p in (self.raw, self.pages):
            p.mkdir(parents=True, exist_ok=True)
        if not (self.root / "log.md").exists():
            (self.root / "log.md").write_text("# Wiki 變更紀錄\n", encoding="utf-8")

    # 原始資料
    def save_raw(self, name, text, meta=""):
        (self.raw / f"{name}.txt").write_text(f"{meta}\n\n{text}" if meta else text, encoding="utf-8")

    def read_raw(self, name):
        return (self.raw / f"{name}.txt").read_text(encoding="utf-8")

    def raw_names(self):
        return sorted(p.stem for p in self.raw.glob("*.txt"))

    # 知識頁
    def names(self):
        return sorted(p.stem for p in self.pages.glob("*.md"))

    def read(self, name):
        p = self.pages / f"{name}.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def write(self, name, content):
        name = re.sub(r"[^a-z0-9\-]", "-", name.lower()).strip("-")
        (self.pages / f"{name}.md").write_text(content.strip() + "\n", encoding="utf-8")
        return name

    def title_and_summary(self, name):
        lines = [l.strip() for l in self.read(name).splitlines() if l.strip()]
        title = next((l.lstrip("# ") for l in lines if l.startswith("# ")), name)
        summary = next((l for l in lines if not l.startswith("#") and not l.startswith("$$")), "")
        return title, summary[:120]

    def rebuild_index(self):
        rows = ["# 貝氏統計入門 Wiki 目錄", "", "| 頁面 | 標題 | 摘要 |", "|---|---|---|"]
        for n in self.names():
            t, s = self.title_and_summary(n)
            rows.append(f"| [[{n}]] | {t} | {s.replace('|', '／')} |")
        (self.root / "index.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    def index_text(self):
        p = self.root / "index.md"
        return p.read_text(encoding="utf-8") if p.exists() else "（目前沒有頁面）"

    def append_log(self, kind, text):
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.root / "log.md", "a", encoding="utf-8") as f:
            f.write(f"\n## [{stamp}] {kind}\n{text.strip()}\n")

    def links_of(self, name):
        return set(self.LINK.findall(self.read(name)))

    # 簡單關鍵字檢索：英文字詞＋中文雙字詞，Wiki 只有十幾頁，不需要向量資料庫
    @staticmethod
    def _tokens(text):
        text = text.lower()
        toks = re.findall(r"[a-z]{3,}", text)
        han = re.findall(r"[一-鿿]+", text)
        for h in han:
            toks += [h[i:i + 2] for i in range(len(h) - 1)]
        return toks

    def search(self, query, k=3):
        q = set(self._tokens(query))
        scored = []
        for n in self.names():
            body = self.read(n)
            toks = self._tokens(body)
            if not toks:
                continue
            title = self.title_and_summary(n)[0]
            score = sum(t in q for t in toks) / (len(toks) ** 0.5)
            score += 3 * sum(t in q for t in self._tokens(title + " " + n.replace("-", " ")))
            scored.append((score, n))
        return [n for s, n in sorted(scored, reverse=True)[:k] if s > 0]


# ------------------------------------------------------------------ Ingest：先討論、後生成
def discuss(llm, wiki, source_name, text):
    """第一階段：只討論、不寫檔。產出重點、與既有頁面的關係、建議新增／更新哪些頁。"""
    user = f"""目前 Wiki 目錄：
{wiki.index_text()}

新的原始資料（{source_name}）：
\"\"\"{text}\"\"\"

請先「討論」這份資料，不要寫頁面。回傳 JSON：
{{"summary": "這份資料在講什麼（3 句內）",
  "key_points": ["對初學者最重要的 3~6 個重點"],
  "conflicts": ["與既有頁面矛盾或重複之處，沒有就空陣列"],
  "proposed_pages": [{{"name": "page-name", "action": "create 或 update", "reason": "為什麼"}}],
  "questions": ["想問使用者的 1~2 個問題，例如要強調什麼、範例要用什麼情境"]}}"""
    return llm.json(WIKI_STYLE, user, tag="ingest.discuss")


def generate_pages(llm, wiki, source_name, text, discussion, user_notes):
    """第二階段：依討論結果＋使用者回饋，產生／合併頁面。"""
    existing = {p["name"]: wiki.read(p["name"]) for p in discussion.get("proposed_pages", [])
                if wiki.read(p["name"])}
    qs = "\n".join(f"{i}. {q}" for i, q in enumerate(discussion.get("questions", []), 1)) or "（無）"
    user = f"""原始資料（{source_name}）：
\"\"\"{text}\"\"\"

先前的討論結果：
{json.dumps(discussion, ensure_ascii=False, indent=1)}

討論時向使用者提出的問題（使用者回覆中的編號對應這裡）：
{qs}

使用者對討論的回饋：{user_notes or "（沒有特別意見，照討論結果進行）"}
使用者回饋的優先順序高於討論建議，寫出的頁面必須確實落實回饋中同意或要求的每一項。

需要更新的既有頁面全文（請在原內容上合併，不要刪掉其他來源的內容）：
{json.dumps(existing, ensure_ascii=False, indent=1) if existing else "（無）"}

目前所有頁面名稱：{wiki.names()}

請依照寫作規則產生頁面，回傳 JSON：
{{"pages": [{{"name": "page-name", "content": "完整 Markdown 內容"}}],
  "log": "一句話說明這次改了什麼"}}"""
    out = llm.json(WIKI_STYLE, user, tag="ingest.generate")
    written = [wiki.write(p["name"], p["content"]) for p in out.get("pages", []) if p.get("content")]
    return written, out.get("log", "")


def check_pages(wiki, names, source_name):
    """ingest 後立即做的規則檢查（不靠 LLM）：有沒有來源段落、有沒有引用本次資料、連結是否存在。"""
    problems = []
    all_names = set(wiki.names())
    for n in names:
        body = wiki.read(n)
        if "## 來源" not in body:
            problems.append(f"{n}: 缺少『## 來源』段落")
        elif source_name not in body.split("## 來源")[-1]:
            problems.append(f"{n}: 來源段落沒有列出 {source_name}")
        if not body.startswith("# "):
            problems.append(f"{n}: 第一行不是 `# 標題`")
    return problems


def _ingest_dir(wiki):
    p = wiki.root / "ingest"
    p.mkdir(exist_ok=True)
    return p


def discuss_step(llm, wiki, source_name, text):
    """先討論：結果存成 wiki/ingest/<name>.discuss.json，讓人看完再回覆；已存在就直接讀取，
    確保後生成用的是使用者看過的那一份討論，而不是重新呼叫一次的另一份。"""
    p = _ingest_dir(wiki) / f"{source_name}.discuss.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    d = discuss(llm, wiki, source_name, text)
    llm.log.add("ingest.discuss", "ok", f"{source_name}: 建議頁面 {[p['name'] for p in d.get('proposed_pages', [])]}")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    return d


def show_discussion(d):
    print("\n── 討論結果 ──")
    print("摘要：", d.get("summary"))
    for kp in d.get("key_points", []):
        print("  •", kp)
    for c in d.get("conflicts", []):
        print("  ⚠ 衝突／重複：", c)
    for p in d.get("proposed_pages", []):
        print(f"  → {p['action']:<6} [[{p['name']}]]：{p.get('reason', '')}")
    for q in d.get("questions", []):
        print("  ？", q)


def ingest(llm, wiki, source_name, text, interactive=True, notes=None):
    """完整 ingest 流程：discuss →（人）回饋 → generate → 規則檢查 →（不過就重生一次）→ 更新 index/log。
    完成的紀錄存成 wiki/ingest/<name>.json；重新執行時直接讀取，不會重打 API 或覆蓋先前的回饋。"""
    log = llm.log
    rec_path = _ingest_dir(wiki) / f"{source_name}.json"
    if rec_path.exists():
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        show_discussion(rec["discussion"])
        print(f"\n我的回饋：{rec['notes'] or '（照建議）'}\n→ 寫入 {rec['written']}"
              + (f"；待修 {rec['problems']}" if rec["problems"] else "") + "（已完成，讀取紀錄）")
        return rec
    d = discuss_step(llm, wiki, source_name, text)
    show_discussion(d)
    if notes is None:
        notes = input("\n你的回饋（直接 Enter 表示照建議進行）：") if interactive else ""

    written, msg = generate_pages(llm, wiki, source_name, text, d, notes)
    problems = check_pages(wiki, written, source_name)
    if problems:
        log.add("ingest.generate", "fail", "; ".join(problems))
        written, msg = generate_pages(llm, wiki, source_name, text, d,
                                      (notes or "") + "\n上次輸出有以下問題，請修正：" + "; ".join(problems))
        problems = check_pages(wiki, written, source_name)
    log.add("ingest.generate", "fail" if problems else "ok",
            f"{source_name}: 寫入 {written}" + (f"；仍有問題 {problems}" if problems else ""))
    wiki.rebuild_index()
    wiki.append_log(f"ingest | {source_name}",
                    f"- 使用者回饋：{notes or '（無）'}\n- 寫入頁面：{', '.join(written)}\n- 說明：{msg}"
                    + (f"\n- 待修：{problems}" if problems else ""))
    rec = {"source": source_name, "discussion": d, "notes": notes, "written": written, "problems": problems}
    rec_path.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return rec


# ------------------------------------------------------------------ Lint：整份 Wiki 健康檢查
def lint(llm, wiki, fix=True, batch_chars=4500):
    log = llm.log
    done = wiki.root / "lint.json"  # 已完成就讀取紀錄，避免分天執行時重複檢查、重複修改 Wiki
    if done.exists():
        rep = json.loads(done.read_text(encoding="utf-8"))
        print(f"（已完成，讀取紀錄）斷連結 {len(rep['broken'])} 個；孤兒頁 {rep['orphans']}；LLM 發現 {len(rep['issues'])} 個問題並已修正")
        return rep
    names = set(wiki.names())
    broken, orphans = [], []
    inbound = {n: 0 for n in names}
    for n in names:
        for l in wiki.links_of(n):
            if l in names:
                inbound[l] += 1
            else:
                broken.append(f"{n} → [[{l}]]")
    orphans = [n for n, c in inbound.items() if c == 0]
    log.add("lint.rules", "fail" if broken else "ok", f"斷掉的連結 {len(broken)} 個；孤兒頁 {orphans}")

    # Groq 免費額度單次請求上限 8000 token（中文約 0.8 token/字元），整份 Wiki 一次送會超過：
    # 分批送檢，每批附上 index.md（所有頁面的標題＋摘要），跨批次的矛盾仍可比對
    batches, cur, size = [], [], 0
    for n in sorted(names):
        body = wiki.read(n)[:1500]
        if cur and size + len(body) > batch_chars:
            batches.append(cur)
            cur, size = [], 0
        cur.append((n, body))
        size += len(body)
    batches.append(cur)
    issues = []
    for k, batch in enumerate(batches, 1):
        corpus = "\n\n".join(f"=== {n} ===\n{body}" for n, body in batch)
        rep = llm.json(WIKI_STYLE, f"""以下是 Wiki 的第 {k}/{len(batches)} 批頁面全文，另附整份 Wiki 的目錄摘要供比對。請檢查：
1. 頁面之間（含與目錄中其他頁面摘要）有沒有互相矛盾的敘述或公式
2. 有沒有明顯錯誤的統計觀念（例如把信賴區間與可信區間的意義混為一談）
3. 斷掉的連結：{broken}
只回報本批頁面的問題。回傳 JSON：{{"issues": [{{"page": "page-name", "problem": "...", "fix": "具體怎麼改"}}]}}

整份 Wiki 目錄：
{wiki.index_text()}

本批頁面全文：
{corpus}""", tag="lint.llm")
        issues += rep.get("issues", [])
    log.add("lint.llm", "fail" if issues else "ok", f"發現 {len(issues)} 個問題：{[i['page'] for i in issues]}")

    if fix and (issues or broken):
        for page in sorted({i["page"] for i in issues if i.get("page") in names}):
            todo = [i for i in issues if i["page"] == page]
            out = llm.json(WIKI_STYLE, f"""請修正這一頁，回傳 JSON {{"content": "修正後完整 Markdown"}}。
問題：{json.dumps(todo, ensure_ascii=False)}
可用的頁面名稱（連結只能指向這些）：{sorted(names)}
原內容：
{wiki.read(page)}""", tag="lint.fix")
            wiki.write(page, out["content"])
            log.add("lint.fix", "ok", f"已修正 {page}")
        wiki.rebuild_index()
    wiki.append_log("lint", f"- 斷連結：{broken}\n- 孤兒頁：{orphans}\n- LLM 檢查問題："
                    + "; ".join(f"{i['page']}: {i['problem']}" for i in issues))
    rep = {"broken": broken, "orphans": orphans, "issues": issues}
    done.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return rep


# ------------------------------------------------------------------ 匯出 Wiki 成單一 HTML（方便繳交）
def export_html(wiki, path):
    import markdown  # pip install markdown
    sections, nav = [], []
    for n in wiki.names():
        body = wiki.LINK.sub(lambda m: f"[{m.group(1)}](#{m.group(1)})", to_tw(wiki.read(n)))
        # \( \) 寫法會被 markdown 吃掉反斜線，先轉成 $ $；再保護 LaTeX 不被 markdown 轉義
        body = re.sub(r"\\\((.+?)\\\)", lambda m: f"${m.group(1)}$", body)
        maths = []
        body = re.sub(r"\$\$.+?\$\$|\$[^$\n]+?\$",
                      lambda m: maths.append(m.group(0)) or f"@@MATH{len(maths) - 1}@@", body, flags=re.S)
        h = markdown.markdown(body, extensions=["tables"])
        h = re.sub(r"@@MATH(\d+)@@", lambda m: html.escape(maths[int(m.group(1))]), h)
        t = wiki.title_and_summary(n)[0]
        nav.append(f'<a href="#{n}">{html.escape(t)}</a>')
        sections.append(f'<section id="{n}">{h}</section>')
    log_html = markdown.markdown((wiki.root / "log.md").read_text(encoding="utf-8"))
    doc = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>貝氏統計入門 LLM Wiki</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
 onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}})"></script>
<style>body{{font-family:system-ui,'Noto Sans TC',sans-serif;margin:0;display:flex;color:#222}}
nav{{width:240px;position:sticky;top:0;height:100vh;overflow:auto;background:#f4f1ea;padding:20px;box-sizing:border-box}}
nav a{{display:block;color:#7a3e00;text-decoration:none;margin:6px 0;font-size:14px}}
main{{max-width:820px;padding:24px 40px;line-height:1.75}}section{{border-bottom:1px solid #ddd;padding-bottom:24px}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 8px}}details{{margin-top:40px}}</style></head>
<body><nav><b>貝氏統計入門 Wiki</b><br><small>{len(sections)} 頁 · 來源 {len(wiki.raw_names())} 篇</small><hr>{''.join(nav)}</nav>
<main>{''.join(sections)}<details><summary>Wiki 變更紀錄（log.md）</summary>{log_html}</details></main></body></html>"""
    Path(path).write_text(doc, encoding="utf-8")
    return path
