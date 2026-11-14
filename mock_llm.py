"""離線測試用的假 LLM：不呼叫 API，回傳結構正確的內容，並刻意製造幾種常見錯誤，
用來驗證 loop / graph 的檢查與重生機制有正常運作。正式執行時不會用到。"""
import json
import re

PAGES = {
    "bayes_theorem": [("bayes-theorem", "貝氏定理（Bayes' theorem）", "描述如何用新證據更新事件機率的公式。",
                       "$$P(A\\mid B)=\\frac{P(B\\mid A)P(A)}{P(B)}$$\n其中 $P(A)$ 是先驗，$P(A\\mid B)$ 是後驗。見 [[prior-and-posterior]]。")],
    "base_rate_fallacy": [("base-rate-fallacy", "基礎比率謬誤（base rate fallacy）", "忽略事前比例而高估檢驗陽性代表患病的機率。",
                           "罕見疾病即使檢驗準確，陽性者真正患病的比例仍可能很低。用 [[bayes-theorem]] 可以算出來。")],
    "bayesian_inference": [("bayesian-inference", "貝氏推論（Bayesian inference）", "把參數視為隨機變數，用資料把先驗更新成後驗的推論方式。",
                            "後驗 ∝ 概似 × 先驗。見 [[prior-and-posterior]]、[[likelihood]]。"),
                           ("likelihood", "概似函數（likelihood）", "在給定參數下觀察到資料的機率，視為參數的函數。",
                            "概似不是參數的機率分佈。見 [[bayesian-inference]]。")],
    "prior_probability": [("prior-and-posterior", "先驗與後驗（prior and posterior）", "看到資料前的相信程度稱為先驗，看到資料後更新的稱為後驗。",
                           "先驗可以是資訊性或無資訊性的。見 [[bayes-theorem]]、[[conjugate-prior]]。")],
    "conjugate_prior": [("conjugate-prior", "共軛先驗（conjugate prior）", "與概似搭配後，後驗仍與先驗屬於同一分佈族的先驗。",
                         "Beta 先驗搭配二項概似：Beta(a,b) 觀察 k 次成功 n 次試驗 → Beta(a+k, b+n-k)。見 [[likelihood]]。")],
    "credible_interval": [("credible-interval", "可信區間（credible interval）", "參數落在區間內的後驗機率為 95% 的區間。",
                           "與頻率學派的信賴區間解釋不同。見 [[prior-and-posterior]]。")],
}


class MockLLM:
    def __init__(self):
        self.seen = {}

    def _count(self, key):
        self.seen[key] = self.seen.get(key, 0) + 1
        return self.seen[key]

    def reply(self, system, user, tag):
        f = getattr(self, "_" + tag.replace(".", "_"), None)
        return json.dumps(f(user) if f else {}, ensure_ascii=False)

    @staticmethod
    def _src(user):
        return re.search(r"原始資料（(\w+)）", user).group(1)

    def _ingest_discuss(self, u):
        s = self._src(u)
        return {"summary": f"{s} 的摘要", "key_points": ["重點一", "重點二"], "conflicts": [],
                "proposed_pages": [{"name": n, "action": "create", "reason": "新概念"} for n, *_ in PAGES[s]],
                "questions": ["範例要用醫療篩檢嗎？"]}

    def _ingest_generate(self, u):
        s = self._src(u)
        first = self._count("gen:" + s) == 1
        pages = []
        for n, t, summ, body in PAGES[s]:
            src = "" if (first and s == "base_rate_fallacy") else f"\n\n## 來源\n- {s}"  # 故意漏來源一次
            pages.append({"name": n, "content": f"# {t}\n{summ}\n\n{body}{src}"})
        return {"pages": pages, "log": f"新增 {[p['name'] for p in pages]}"}

    def _lint_llm(self, u):
        return {"issues": [{"page": "credible-interval", "problem": "沒說明與信賴區間差在哪",
                            "fix": "補一句頻率學派解釋"}]} if self._count("lint") == 1 else {"issues": []}

    def _lint_fix(self, u):
        return {"content": "# 可信區間（credible interval）\n參數落在區間內的後驗機率為 95% 的區間。\n\n"
                           "信賴區間則是指重複抽樣下有 95% 的區間會包含真值。見 [[prior-and-posterior]]。\n\n## 來源\n- credible_interval"}

    def _plan(self, u):
        bad = self._count("plan") == 1
        S = [(1, "為什麼需要貝氏統計？", ["bayesian-inference"], ""),
             (2, "貝氏定理一行公式", ["bayes-theorem"], ""),
             (3, "先驗與後驗", ["prior-and-posterior"], ""),
             (4, "概似函數", ["likelihood"], ""),
             (5, "陽性就一定得病嗎？", ["base-rate-fallacy", "bayes-theorem"], "disease_test"),
             (6, "基礎比率謬誤", ["base-rate-fallacy"], ""),
             (7, "共軛先驗：Beta 與二項", ["conjugate-prior"], ""),
             (8, "擲硬幣：一步步更新", ["conjugate-prior", "bayesian-inference"], "coin"),
             (9, "可信區間怎麼解讀", ["credible-interval" if not bad else "credible-intervals"], ""),
             (10, "重點回顧", ["bayesian-inference", "prior-and-posterior"], "")]
        return {"slides": [{"id": i, "title": t, "goal": t, "pages": p, "example": e} for i, t, p, e in S]}

    def _draft(self, u):
        item = json.loads(re.search(r"投影片規劃：(\{.*?\})\n", u).group(1))
        n = self._count(f"draft:{item['id']}")
        verified = "已由程式計算並驗證" in u
        s = {"title": item["title"], "bullets": ["白話重點一，說明概念", "白話重點二，連到前一張"],
             "formula": "", "example": "", "calc": None, "notes": "可以用天氣預報當類比。", "sources": item["pages"]}
        if item["example"] == "disease_test":
            post = 0.1538 if (verified or n > 1) else 0.9  # 沒有預先算好時，第一版常把敏感度當成後驗
            s.update(formula="P(\\text{病}\\mid +)=\\frac{0.9\\times0.01}{0.9\\times0.01+0.05\\times0.99}",
                     example=f"一萬人中 100 人有病，90 人陽性；9900 人沒病，495 人偽陽性。陽性者有病機率約 {post*100:.1f}%。",
                     calc={"type": "disease_test", "posterior": post})
        if item["example"] == "coin":
            s.update(formula="\\text{Beta}(2,2)\\to\\text{Beta}(9,5)", example="擲 10 次 7 次正面，後驗平均 9/14≈0.643。",
                     calc={"type": "coin", "posterior_mean": 0.6429})
        if item["id"] == 4 and n == 1:
            s["bullets"] = ["概似函數是在給定參數下觀察到資料的機率，但要把它看成參數的函數而不是資料的函數，因此它不是一個機率分佈，積分不一定等於一"]
        return s

    def _check_judge(self, u):
        if '"title": "共軛先驗：Beta 與二項"' in u and self._count("judge7") == 1:
            return {"grounded": True, "unsupported": [], "beginner_ok": False,
                    "undefined_terms": ["分佈族"], "feedback": "先用一句話解釋什麼是分佈族"}
        return {"grounded": True, "unsupported": [], "beginner_ok": True, "undefined_terms": [], "feedback": ""}

    def _deck_review(self, u):
        return {"pass": False, "fix_slides": [{"id": 6, "feedback": "與第 5 張重複，改成『如何避免』"}],
                "comment": "順序合理，第 6 張與第 5 張重複。"}
