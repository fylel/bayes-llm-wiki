# Wiki 變更紀錄

## [2026-11-13 14:20] ingest | bayes_theorem
- 使用者回饋：照建議
- 寫入頁面：bayes-theorem, bayesian-inference, medical-diagnosis-example
- 說明：新增 bayes-theorem、bayesian-inference、medical-diagnosis-example 三頁，說明定理、推論流程與醫學診斷範例。

## [2026-11-13 14:23] ingest | base_rate_fallacy
- 使用者回饋：1.好 2.不用
- 寫入頁面：base-rate-fallacy, false-positive-paradox
- 說明：新增 base-rate-fallacy 與 false-positive-paradox 兩頁，說明概念、例子與貝氏推論關聯

## [2026-11-13 14:24] ingest | base_rate_fallacy
- 使用者回饋：1.好 2.不用
- 寫入頁面：base-rate-fallacy, false-positive-paradox
- 說明：在 base-rate-fallacy 頁面加入醫學診斷連結，保持原有內容；更新 false-positive-paradox 內容保持一致。

## [2026-11-13 14:25] ingest | bayesian_inference
- 使用者回饋：可以
- 寫入頁面：bayesian-inference, bayesian-updating
- 說明：在 bayesian-inference 頁面加入實務範例與非貝氏更新差異說明，並新增 bayesian-updating 子頁說明單次與多次更新流程

## [2026-11-13 14:27] 人工修正 | false-positive-paradox
- 原因：ingest base_rate_fallacy 時使用者同意「新頁面加入 [[medical-diagnosis-example]] 連結」，重新生成後只有 base-rate-fallacy 加上
- 修改：在「相關頁面」補上 [[medical-diagnosis-example]]

## [2026-11-13 14:27] ingest | prior_probability
- 使用者回饋：好
- 寫入頁面：prior-probability, informative-prior, uninformative-prior
- 說明：新增先驗機率、資訊性先驗、無資訊性先驗三頁，並加入數學範例與應用說明

## [2026-11-13 14:28] ingest | conjugate_prior
- 使用者回饋：不要
- 寫入頁面：conjugate-prior, beta-binomial-example, gamma-poisson-example
- 說明：新增共軛先驗及兩個具體範例頁面

## [2026-11-13 14:29] ingest | credible_interval
- 使用者回饋：不用
- 寫入頁面：credible-interval
- 說明：新增 credible-interval 頁面，說明定義、類型、與信賴區間的比較及計算方法。

## [2026-11-13 14:38] lint
- 斷連結：[]
- 孤兒頁：['beta-binomial-example', 'gamma-poisson-example', 'conjugate-prior', 'credible-interval']
- LLM 檢查問題：

## [2026-11-14 14:34] 人工修正 | 公式與用語
- false-positive-paradox：`999 × 0.05 \approx 49.95` 不在 $…$ 內，wiki.html 顯示原始 LaTeX（lint 未抓到），補上 $…$
- 用語統一為台灣習慣（似然→概似、分布→分佈、信息→資訊），影響 10 頁：base-rate-fallacy, bayes-theorem, bayesian-inference, bayesian-updating, beta-binomial-example, conjugate-prior, credible-interval, gamma-poisson-example, prior-probability, uninformative-prior
