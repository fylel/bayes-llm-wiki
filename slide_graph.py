"""用 LLM Wiki 產生教學 HTML 簡報的 graph。

節點（node）與邊（edge）：

    plan ──► check_plan ──(不過，最多重試 2 次)──► plan
               │通過
               ▼
    compute_facts（Python 先算好範例數字；PRECOMPUTE=False 時跳過）
               ▼
    ┌─► retrieve ─► draft ─► check_slide ──(不過且未超過上限)──┐
    │                              │通過 / 超過上限就標記 ⚑     │
    │    （每張投影片一輪）         ▼                           │
    └──────────────────────── 下一張 ◄──────── draft（帶回饋）◄─┘
               ▼
    deck_review ──(指出需修改的投影片)──► 回到該張的 draft loop（只做一輪）
               ▼
    render_html
"""
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from wiki_tools import WIKI_STYLE, to_tw

GRAPH_MERMAID = """flowchart TD
    A[取得資料 fetch 5+ 篇] --> B[ingest.discuss<br/>先討論]
    B --> H{{人工回饋}}
    H --> C[ingest.generate<br/>後生成頁面]
    C --> C1{規則檢查<br/>來源/標題}
    C1 -- 不過 --> C
    C1 -- 通過 --> D[更新 index.md / log.md]
    D -->|下一篇| B
    D --> L[lint<br/>斷連結/矛盾/觀念錯誤]
    L --> P[plan 大綱<br/>讀 index.md]
    P --> P1{check_plan<br/>頁面存在?張數?}
    P1 -- 不過 --> P
    P1 -- 通過 --> F[compute_facts<br/>Python 先算範例數字]
    F --> R[retrieve 查 Wiki]
    R --> W[draft 單張投影片]
    W --> K{check_slide<br/>規則+數字+LLM 依據/易懂}
    K -- 不過 且 < 上限 --> W
    K -- 通過 或 達上限⚑ --> N{還有下一張?}
    N -- 是 --> R
    N -- 否 --> V{deck_review<br/>順序/重複/涵蓋}
    V -- 指出問題 --> W
    V -- 通過 --> O[render_html 輸出簡報]"""


@dataclass
class Config:
    topic: str = "貝氏統計入門：用新證據更新你的相信程度"
    audience: str = "修過基礎機率、但沒學過貝氏統計的大學生"
    n_slides: tuple = (8, 11)          # 內容頁張數範圍（不含封面與參考頁）
    max_slide_attempts: int = 3        # 單張投影片最多生成幾次
    max_plan_attempts: int = 3
    precompute_numbers: bool = True    # v2：把數字檢查往前移到 draft 之前
    use_llm_judge: bool = True
    k_extra: int = 2                   # retrieve 時除了大綱指定頁，再用關鍵字檢索補幾頁
    # 教學範例的參數（由 Python 計算，不讓 LLM 自己算）
    examples: dict = field(default_factory=lambda: {
        "disease_test": {"prior": 0.01, "sensitivity": 0.90, "false_positive_rate": 0.05},
        "coin": {"a": 2, "b": 2, "heads": 7, "n": 10},
    })


# ------------------------------------------------------------------ 計算器：範例數字的唯一真相來源
def calc_disease_test(prior, sensitivity, false_positive_rate, population=10000):
    sick = prior * population
    tp = sensitivity * sick
    fp = false_positive_rate * (population - sick)
    post = tp / (tp + fp)
    return {"population": population, "sick": round(sick), "true_positive": round(tp),
            "false_positive": round(fp), "posterior": round(post, 4),
            "posterior_pct": f"{post * 100:.1f}%"}


def calc_coin(a, b, heads, n):
    from scipy.stats import beta
    a2, b2 = a + heads, b + n - heads
    lo, hi = beta.ppf([0.025, 0.975], a2, b2)
    return {"prior": f"Beta({a},{b})", "posterior": f"Beta({a2},{b2})",
            "posterior_mean": round(a2 / (a2 + b2), 4), "mle": round(heads / n, 4),
            "ci95": [round(lo, 3), round(hi, 3)]}


def compute_facts(cfg):
    ex = cfg.examples
    return {"disease_test": {"inputs": ex["disease_test"], **calc_disease_test(**ex["disease_test"])},
            "coin": {"inputs": ex["coin"], **calc_coin(**ex["coin"])}}


# ------------------------------------------------------------------ 節點
def node_plan(llm, wiki, cfg, feedback=""):
    lo, hi = cfg.n_slides
    user = f"""你要用下面這份 Wiki 做一份教學簡報。
主題：{cfg.topic}
聽眾：{cfg.audience}

Wiki 目錄（index.md）：
{wiki.index_text()}

請規劃 {lo}~{hi} 張內容投影片（不含封面與參考資料頁），由淺入深，每個概念在被使用前要先介紹。
可用範例代號：disease_test（疾病篩檢，基礎比率謬誤）、coin（擲硬幣，Beta-二項共軛更新）。
回傳 JSON：
{{"slides": [{{"id": 1, "title": "投影片標題", "goal": "看完這張聽眾要懂什麼",
  "pages": ["這張要依據的 wiki page-name，1~3 個，必須在目錄中"],
  "example": "disease_test / coin / 空字串"}}]}}
{("上一版大綱的問題：" + feedback) if feedback else ""}"""
    return llm.json(WIKI_STYLE, user, tag="plan")


def check_plan(outline, wiki, cfg):
    problems = []
    names = set(wiki.names())
    slides = outline.get("slides", [])
    lo, hi = cfg.n_slides
    if not lo <= len(slides) <= hi:
        problems.append(f"張數 {len(slides)} 不在 {lo}~{hi}")
    for s in slides:
        bad = [p for p in s.get("pages", []) if p not in names]
        if bad:
            problems.append(f"第 {s.get('id')} 張引用不存在的頁面 {bad}（可用：{sorted(names)}）")
        if not s.get("pages"):
            problems.append(f"第 {s.get('id')} 張沒有指定依據頁面")
    used = {s.get("example") for s in slides}
    for ex in ("disease_test", "coin"):
        if ex not in used:
            problems.append(f"大綱沒有用到範例 {ex}")
    return problems


def node_retrieve(wiki, item, k_extra=2):
    pages = [p for p in item.get("pages", []) if wiki.read(p)]
    for p in wiki.search(item["title"] + " " + item.get("goal", ""), k=k_extra + len(pages)):
        if p not in pages and len(pages) < len(item.get("pages", [])) + k_extra:
            pages.append(p)
    return {p: wiki.read(p) for p in pages}


SLIDE_SCHEMA = """{"title": "標題",
 "bullets": ["2~5 點，每點 45 字以內，給初學者看的白話說明"],
 "formula": "需要的話放一條 LaTeX 公式（不含 $ 符號），不需要就空字串",
 "example": "範例說明文字（沒有就空字串）",
 "calc": null 或 {"type": "disease_test", "posterior": 0.xxxx} 或 {"type": "coin", "posterior_mean": 0.xxxx},
 "notes": "講者備註：口頭補充、類比、常見誤解",
 "sources": ["實際用到的 wiki page-name"]}"""


def node_draft(llm, item, context, facts, cfg, feedback="", prev=None):
    fact_txt = ""
    if item.get("example") and facts:
        fact_txt = (f"\n這張使用範例 {item['example']}。以下數字已由程式計算並驗證，請直接引用，不要自己重算：\n"
                    + json.dumps(facts[item["example"]], ensure_ascii=False))
    elif item.get("example"):
        fact_txt = (f"\n這張使用範例 {item['example']}，參數：{json.dumps(cfg.examples[item['example']])}。"
                    "請自行計算結果並填入 calc。")
    user = f"""聽眾：{cfg.audience}
投影片規劃：{json.dumps(item, ensure_ascii=False)}
{fact_txt}

只能根據以下 Wiki 頁面撰寫（不可加入頁面沒有的說法）：
{json.dumps(context, ensure_ascii=False, indent=1)}

回傳 JSON，格式：
{SLIDE_SCHEMA}"""
    if feedback:
        user += f"\n\n上一版：{json.dumps(prev, ensure_ascii=False)}\n檢查沒通過，原因：{feedback}\n請針對問題修改。"
    return llm.json(WIKI_STYLE, user, tag="draft")


def rule_check(slide, item, wiki):
    p = []
    if not slide.get("title"):
        p.append("缺標題")
    b = slide.get("bullets") or []
    if not 2 <= len(b) <= 5:
        p.append(f"重點數 {len(b)} 不在 2~5")
    long = [x[:15] + "…" for x in b if len(x) > 60]
    if long:
        p.append(f"重點過長：{long}")
    src = slide.get("sources") or []
    if not src:
        p.append("沒有列出依據的 wiki 頁面")
    bad = [s for s in src if s not in wiki.names()]
    if bad:
        p.append(f"sources 有不存在的頁面 {bad}")
    if item.get("example") and not slide.get("calc"):
        p.append(f"這張應該有 {item['example']} 範例的 calc 欄位")
    return p


def numeric_check(slide, cfg):
    calc = slide.get("calc")
    if not calc:
        return []
    ex = cfg.examples
    p = []
    try:
        if calc.get("type") == "disease_test":
            truth = calc_disease_test(**ex["disease_test"])
            if abs(float(calc.get("posterior", -1)) - truth["posterior"]) > 0.005:
                p.append(f"後驗機率寫成 {calc.get('posterior')}，正確是 {truth['posterior']}（{truth['posterior_pct']}）")
            text = json.dumps(slide, ensure_ascii=False)
            pcts = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", text)]
            wrong = [x for x in pcts if 10 < x < 99 and x not in (90.0, 95.0) and abs(x - truth["posterior"] * 100) > 0.6]
            if wrong:
                p.append(f"內文出現的百分比 {wrong} 與正確後驗 {truth['posterior_pct']} 不符")
        elif calc.get("type") == "coin":
            truth = calc_coin(**ex["coin"])
            if abs(float(calc.get("posterior_mean", -1)) - truth["posterior_mean"]) > 0.005:
                p.append(f"後驗平均寫成 {calc.get('posterior_mean')}，正確是 {truth['posterior_mean']}（{truth['posterior']}）")
    except (TypeError, ValueError) as e:
        p.append(f"calc 欄位格式錯誤：{e}")
    return p


def llm_judge(llm, slide, context, cfg):
    out = llm.json("你是嚴格的統計學審稿人，負責檢查教學投影片。", f"""聽眾：{cfg.audience}
依據的 Wiki 內容：
{json.dumps(context, ensure_ascii=False)}

投影片：
{json.dumps(slide, ensure_ascii=False)}

請檢查：
(a) grounded：每個重點與公式是否都能在 Wiki 內容中找到依據？統計觀念是否正確？
(b) beginner_ok：聽眾看得懂嗎？有沒有未定義就使用的術語？
回傳 JSON：{{"grounded": true/false, "unsupported": ["沒有依據或錯誤的句子"],
"beginner_ok": true/false, "undefined_terms": ["..."], "feedback": "具體修改建議（通過可留空）"}}""",
                   tag="check.judge")
    p = []
    if not out.get("grounded", False):
        p.append(f"缺乏 Wiki 依據或觀念錯誤：{out.get('unsupported')}")
    if not out.get("beginner_ok", False):
        p.append(f"初學者不易懂，未定義術語：{out.get('undefined_terms')}")
    if p and out.get("feedback"):
        p.append("審稿建議：" + out["feedback"])
    return p


def slide_loop(llm, wiki, item, facts, cfg, extra_feedback=""):
    """retrieve → draft → check_slide 的 loop，回傳 (slide, 紀錄)。"""
    log = llm.log
    ctx = node_retrieve(wiki, item, cfg.k_extra)
    log.add("retrieve", "ok", f"#{item['id']} {item['title']} ← {list(ctx)}")
    slide, fb, history = None, extra_feedback, []
    for attempt in range(1, cfg.max_slide_attempts + 1):
        slide = node_draft(llm, item, ctx, facts, cfg, fb, slide)
        checks = {"rule": rule_check(slide, item, wiki), "numeric": numeric_check(slide, cfg)}
        for k in ("rule", "numeric"):
            log.add(f"check.{k}", "fail" if checks[k] else "ok",
                    f"#{item['id']} 第{attempt}版：" + ("; ".join(checks[k]) or "通過"))
        # 規則／數字沒過就不浪費一次 LLM judge
        if not checks["rule"] and not checks["numeric"] and cfg.use_llm_judge:
            checks["judge"] = llm_judge(llm, slide, ctx, cfg)
            log.add("check.judge", "fail" if checks["judge"] else "ok",
                    f"#{item['id']} 第{attempt}版：" + ("; ".join(checks["judge"]) or "通過"))
        problems = sum(checks.values(), [])
        history.append({"attempt": attempt, "problems": problems})
        if not problems:
            log.add("draft", "ok", f"#{item['id']} 第{attempt}版通過")
            break
        log.add("draft", "info" if attempt < cfg.max_slide_attempts else "flag",
                f"#{item['id']} 第{attempt}版不過，{'重新生成' if attempt < cfg.max_slide_attempts else '已達上限，標記⚑待人工確認'}")
        fb = "; ".join(problems)
    slide["_attempts"] = history
    slide["_flagged"] = bool(history[-1]["problems"])
    slide["_id"] = item["id"]
    return slide


def deck_review(llm, slides, cfg):
    brief = [{"id": s["_id"], "title": s["title"], "bullets": s["bullets"]} for s in slides]
    return llm.json("你是教學設計審稿人。", f"""主題：{cfg.topic}；聽眾：{cfg.audience}
整份簡報（依序）：
{json.dumps(brief, ensure_ascii=False, indent=1)}

請檢查整體：概念是否在使用前已介紹？有沒有重複？有沒有缺少讓初學者理解的關鍵步驟？
只指出真正需要改的投影片（最多 3 張）。回傳 JSON：
{{"pass": true/false, "fix_slides": [{{"id": 編號, "feedback": "具體要怎麼改"}}], "comment": "整體評語"}}""",
                    tag="deck_review")


# ------------------------------------------------------------------ 整條 graph
def run_graph(llm, wiki, cfg, ckpt=None):
    """ckpt：檢查點檔名。免費額度（每日 token 上限）用完時程式會停下，隔天重跑同一格就從檢查點接續；
    檢查點同時保存 RunLog 事件與 LLM 呼叫數，分天執行的紀錄會合併成一份。"""
    log = llm.log
    ck = Path(ckpt) if ckpt else None
    st = json.loads(ck.read_text(encoding="utf-8")) if ck and ck.exists() else \
        {"outline": None, "slides": [], "review": None, "fixed": [], "events": [], "calls": 0}
    log.events[:0] = st["events"]
    base_calls, c0 = st["calls"], llm.calls

    def save():
        if ck:
            st["events"], st["calls"] = log.events, base_calls + llm.calls - c0
            ck.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")

    done = (st["outline"] and len(st["slides"]) == len(st["outline"]["slides"]) and st["review"] is not None
            and all(f["id"] in st["fixed"] for f in st["review"].get("fix_slides", [])))
    if st["events"] and not done:
        log.add("resume", "info", f"從檢查點接續：已完成 {len(st['slides'])} 張投影片")
    try:
        # plan ⇄ check_plan
        if st["outline"] is None:
            fb = ""
            for attempt in range(1, cfg.max_plan_attempts + 1):
                outline = node_plan(llm, wiki, cfg, fb)
                problems = check_plan(outline, wiki, cfg)
                log.add("check_plan", "fail" if problems else "ok",
                        f"第{attempt}版大綱 {len(outline.get('slides', []))} 張：" + ("; ".join(problems) or "通過"))
                if not problems:
                    break
                fb = "; ".join(problems)
            for it in outline["slides"]:  # 若最後仍有不存在的頁面，直接剔除，避免後面整串出錯
                it["pages"] = [p for p in it.get("pages", []) if wiki.read(p)]
            st["outline"] = outline
            save()
        items = st["outline"]["slides"]

        facts = compute_facts(cfg) if cfg.precompute_numbers else None
        if not st["slides"]:
            log.add("compute_facts", "info", json.dumps(facts, ensure_ascii=False) if facts else "略過（v1 模式：讓 LLM 自己算）")

        slides = st["slides"]
        for it in items[len(slides):]:
            slides.append(slide_loop(llm, wiki, it, facts, cfg))
            save()

        if st["review"] is None:
            review = deck_review(llm, slides, cfg)
            fixes = [f for f in review.get("fix_slides", []) if any(s["_id"] == f.get("id") for s in slides)]
            log.add("deck_review", "ok" if not fixes else "fail",
                    review.get("comment", "") + (f"｜需修改 {[f['id'] for f in fixes]}" if fixes else ""))
            st["review"] = review
            save()
        review = st["review"]
        fixes = [f for f in review.get("fix_slides", []) if any(s["_id"] == f.get("id") for s in slides)]
        for f in fixes:
            if f["id"] in st["fixed"]:
                continue
            i = next(k for k, s in enumerate(slides) if s["_id"] == f["id"])
            item = next(it for it in items if it["id"] == f["id"])
            new = slide_loop(llm, wiki, item, facts, cfg, extra_feedback="整體審稿意見：" + f["feedback"])
            new["_attempts"] = slides[i]["_attempts"] + [{"attempt": "deck_review", "problems": [f["feedback"]]}] + new["_attempts"]
            slides[i] = new
            st["fixed"].append(f["id"])
            save()
    finally:
        save()  # 中途因額度用完而停下時，已發生的呼叫與紀錄也保留
    return {"outline": st["outline"], "facts": facts, "slides": slides, "deck_review": review,
            "llm_calls": st["calls"]}


# ------------------------------------------------------------------ 輸出 HTML 簡報
def _esc(s):
    """跳脫 HTML（保留 $...$ 讓 KaTeX 處理），並統一為台灣用語。"""
    return html.escape(to_tw(str(s)), quote=False)


def render_html(result, wiki, cfg, path, wiki_href="wiki.html"):
    slides = result["slides"]
    sections = [f"""<section class="slide cover"><div>
<p class="kicker">LLM Wiki 教學簡報</p><h1>{_esc(cfg.topic)}</h1>
<p class="sub">給{_esc(cfg.audience)}</p>
<p class="hint">按 → 或空白鍵翻頁 · N 顯示講者備註</p></div></section>"""]
    for k, s in enumerate(slides, 1):
        bullets = "".join(f"<li>{_esc(b)}</li>" for b in s.get("bullets", []))
        formula = f'<div class="formula">$${html.escape(s["formula"], quote=False)}$$</div>' if s.get("formula") else ""
        example = f'<div class="example"><b>範例</b>{_esc(s["example"])}</div>' if s.get("example") else ""
        src = " ".join(f'<a href="{wiki_href}#{p}" target="_blank">[[{p}]]</a>' for p in s.get("sources", []))
        n_try = len([a for a in s["_attempts"] if a["attempt"] != "deck_review"])
        badge = ('<span class="badge flag">⚑ 未完全通過檢查</span>' if s["_flagged"]
                 else f'<span class="badge">✓ 第 {n_try} 版通過檢查</span>')
        sections.append(f"""<section class="slide"><div class="num">{k:02d}</div>
<h2>{_esc(s.get('title', ''))}</h2><div class="body"><ul>{bullets}</ul>{formula}{example}</div>
<footer><span>依據 Wiki：{src}</span>{badge}</footer>
<aside class="notes"><b>講者備註</b>{_esc(s.get('notes', ''))}</aside></section>""")
    used = sorted({p for s in slides for p in s.get("sources", [])})
    refs = "".join(f'<li><a href="{wiki_href}#{p}" target="_blank">{_esc(wiki.title_and_summary(p)[0])}</a></li>' for p in used)
    raws = "、".join(wiki.raw_names())
    sections.append(f"""<section class="slide"><h2>參考資料</h2><div class="body">
<p>本簡報每一張都只根據下列 Wiki 頁面生成：</p><ul class="refs">{refs}</ul>
<p class="small">Wiki 的原始資料（raw）：{_esc(raws)}</p></div></section>""")

    doc = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{_esc(cfg.topic)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
 onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}})"></script>
<style>
:root{{--bg:#faf7f2;--ink:#1f1d1a;--accent:#b4531a;--soft:#efe6d8;--muted:#7b736a}}
*{{box-sizing:border-box}}html,body{{margin:0;height:100%;background:#2b2724;font-family:system-ui,'Noto Sans TC','PingFang TC',sans-serif}}
.deck{{position:relative;width:min(100vw,177.78vh);height:min(56.25vw,100vh);margin:auto;top:50%;transform:translateY(-50%)}}
.slide{{position:absolute;inset:0;background:var(--bg);color:var(--ink);padding:5% 7% 4%;display:none;flex-direction:column;font-size:clamp(14px,2.1vw,30px)}}
.slide.active{{display:flex}}
.cover{{justify-content:center;background:linear-gradient(135deg,#faf7f2 60%,#f1e2cf)}}
.kicker{{color:var(--accent);letter-spacing:.15em;font-weight:600;font-size:.7em;margin:0}}
h1{{font-size:2.1em;line-height:1.2;margin:.3em 0}}.sub{{color:var(--muted)}}.hint{{color:var(--muted);font-size:.55em;margin-top:3em}}
h2{{font-size:1.45em;margin:0 0 .6em;border-left:.25em solid var(--accent);padding-left:.5em}}
.num{{position:absolute;top:4%;right:5%;color:var(--soft);font-size:2.6em;font-weight:800}}
.body{{flex:1;overflow:auto}}ul{{margin:0;padding-left:1.1em}}li{{margin:.35em 0;line-height:1.45}}
.formula{{background:white;border:1px solid var(--soft);border-radius:8px;margin:.6em 0;padding:.2em .6em;font-size:.95em}}
.example{{background:var(--soft);border-radius:8px;padding:.5em .8em;margin-top:.5em;font-size:.82em;line-height:1.5}}
.example b{{color:var(--accent);margin-right:.6em}}
footer{{display:flex;justify-content:space-between;align-items:center;font-size:.45em;color:var(--muted);border-top:1px solid var(--soft);padding-top:.6em}}
footer a{{color:var(--accent);text-decoration:none;margin-right:.4em}}
.badge{{background:#e3efe2;color:#2f6b2c;padding:.2em .6em;border-radius:99px}}.badge.flag{{background:#fbe3d9;color:#a23a12}}
.notes{{display:none;position:absolute;left:0;right:0;bottom:0;background:#1f1d1aee;color:#f5efe6;padding:1em 7%;font-size:.55em;line-height:1.6}}
.notes b{{display:block;color:#f0a35e}}body.show-notes .slide.active .notes{{display:block}}
.small{{font-size:.6em;color:var(--muted)}}.refs a{{color:var(--accent)}}
.bar{{position:fixed;left:0;bottom:0;height:4px;background:var(--accent);transition:width .2s}}
.ctr{{position:fixed;right:12px;bottom:10px;color:#ccc;font-size:12px}}
</style></head><body><div class="deck">{''.join(sections)}</div><div class="bar"></div><div class="ctr"></div>
<script>
const S=[...document.querySelectorAll('.slide')];let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1));
function fit(s){{const b=s.querySelector('.body');if(!b)return;let f=100;b.style.fontSize='';
while(b.scrollHeight>b.clientHeight+1&&f>70){{f-=5;b.style.fontSize=f+'%';}}}}
window.addEventListener('load',()=>setTimeout(()=>fit(S[i]),300));window.addEventListener('resize',()=>fit(S[i]));
function show(n){{i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,k)=>s.classList.toggle('active',k===i));fit(S[i]);
document.querySelector('.bar').style.width=((i+1)/S.length*100)+'%';document.querySelector('.ctr').textContent=(i+1)+' / '+S.length;history.replaceState(null,'','#'+(i+1));}}
document.addEventListener('keydown',e=>{{if(['ArrowRight',' ','PageDown'].includes(e.key))show(i+1);
else if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);else if(e.key==='n'||e.key==='N')document.body.classList.toggle('show-notes');}});
document.addEventListener('click',e=>{{if(e.target.closest('a'))return;show(e.clientX>innerWidth/3?i+1:i-1);}});
let x0=null;document.addEventListener('touchstart',e=>x0=e.touches[0].clientX);
document.addEventListener('touchend',e=>{{if(x0===null)return;const d=e.changedTouches[0].clientX-x0;if(Math.abs(d)>40)show(i+(d<0?1:-1));x0=null;}});
window.addEventListener('hashchange',()=>{{const n=parseInt(location.hash.slice(1));if(n&&n-1!==i)show(n-1);}});
show(i);
</script></body></html>"""
    Path(path).write_text(doc, encoding="utf-8")
    return path


def check_record(result):
    """把每張投影片的檢查過程整理成 Markdown，當作「實際執行的檢查紀錄」。"""
    lines = ["# 投影片檢查紀錄", "", "| # | 標題 | 生成次數 | 結果 | 被擋下的原因 |", "|---|---|---|---|---|"]
    for s in result["slides"]:
        tries = [a for a in s["_attempts"] if a["attempt"] != "deck_review"]
        why = " / ".join(("整體審稿" if a["attempt"] == "deck_review" else f"第{a['attempt']}版")
                         + "：" + "; ".join(a["problems"]) for a in s["_attempts"] if a["problems"])
        why = re.sub(r"\s*\n\s*", " ", why).replace("|", "／")  # 換行會打斷 Markdown 表格
        lines.append(f"| {s['_id']} | {s.get('title', '')} | {len(tries)} | {'⚑ 待人工確認' if s['_flagged'] else '通過'} | "
                     f"{why[:400] + ('…' if len(why) > 400 else '') or '—'} |")
    r = result["deck_review"]
    lines += ["", f"**整體審稿（deck_review）**：{r.get('comment', '')}",
              f"需修改：{[f.get('id') for f in r.get('fix_slides', [])] or '無'}"]
    return "\n".join(lines)
