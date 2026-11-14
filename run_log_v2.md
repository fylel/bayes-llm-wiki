# 執行紀錄：run_log_v2

## 各節點成功／失敗次數

| 節點 | 成功 | 失敗或重試 | 失敗率 |
|---|---|---|---|
| check.judge | 5 | 13 | 72% |
| check.rule | 18 | 8 | 31% |
| deck_review | 0 | 1 | 100% |
| check_plan | 1 | 0 | 0% |
| retrieve | 10 | 0 | 0% |
| check.numeric | 26 | 0 | 0% |
| draft | 5 | 0 | 0% |

## 逐步紀錄

| 時間(s) | 節點 | 狀態 | 說明 |
|---|---|---|---|
| 15.2 | check_plan | ok | 第1版大綱 7 張：通過 |
| 37.2 | compute_facts | info | {"disease_test": {"inputs": {"prior": 0.01, "sensitivity": 0.9, "false_positive_rate": 0.05}, "population": 10000, "sick": 100, "true_positive": 90, "false_positive": 495, "posterior": 0.1538, "poster |
| 37.2 | retrieve | ok | #1 什麼是先驗機率與後驗機率？ ← ['prior-probability', 'bayesian-updating', 'informative-prior'] |
| 37.3 | draft | info | 每日額度用完，等待回補 9.2 分鐘 |
| 590.2 | check.rule | ok | #1 第1版：通過 |
| 590.2 | check.numeric | ok | #1 第1版：通過 |
| 590.4 | check.judge | info | 每日額度用完，等待回補 18.6 分鐘 |
| 1707.0 | check.judge | info | JSON 有未跳脫的反斜線，已在本地修復：Invalid \escape: line 6 column 113 (char 235) |
| 1707.0 | check.judge | fail | #1 第1版：初學者不易懂，未定義術語：['似然', '證據', '遞迴更新', '動態的信念修正機制']; 審稿建議：內容大體正確且都有 Wiki 依據。為了讓未學過貝氏統計的學生易於理解，建議在投影片中加入以下說明： 1. 簡短定義「似然」：在給定假說 H 下，觀測到資料 E 的機率。 2. 解釋「證據」\(P(E)\)：所有可能假說的加權總和，使後驗機率正規化。 3. 用更口語化的說法說明「 |
| 1707.0 | draft | info | #1 第1版不過，重新生成 |
| 1707.2 | draft | info | 每日額度用完，等待回補 23.8 分鐘 |
| 16521.9 | check.rule | ok | #1 第2版：通過 |
| 16521.9 | check.numeric | ok | #1 第2版：通過 |
| 16523.8 | check.judge | fail | #1 第2版：缺乏 Wiki 依據或觀念錯誤：['「似然是指在假說 H 成立時，觀測到資料 E 的機率。」——雖然概念在 Wiki 中提及，但未明確以此文字說明。', '「證據 P(E) 是所有可能假說的加權總和，用來讓後驗機率總和為 1。」——此說法在 Wiki 中未出現，且「所有可能假說」的說法過於簡化，應為「所有假說的邊際機率」。', '「單次觀測時，後驗 = 似然 × 先驗 ÷ 證據；每次 |
| 16523.8 | draft | info | #1 第2版不過，重新生成 |
| 16538.9 | check.rule | ok | #1 第3版：通過 |
| 16538.9 | check.numeric | ok | #1 第3版：通過 |
| 16557.3 | check.judge | ok | #1 第3版：通過 |
| 16557.3 | draft | ok | #1 第3版通過 |
| 16557.3 | retrieve | ok | #2 貝氏定理：從條件機率到原因機率 ← ['bayes-theorem', 'prior-probability'] |
| 16574.0 | check.rule | fail | #2 第1版：重點過長：['貝氏定理把已知條件下的機率 $…', '公式為 $P(A／B)=\\fr…', '若有多個互斥且完整的假設 $A…'] |
| 16574.0 | check.numeric | ok | #2 第1版：通過 |
| 16574.0 | draft | info | #2 第1版不過，重新生成 |
| 16593.4 | check.rule | ok | #2 第2版：通過 |
| 16593.4 | check.numeric | ok | #2 第2版：通過 |
| 16610.4 | check.judge | fail | #2 第2版：初學者不易懂，未定義術語：['正規化']; 審稿建議：建議在投影片或備註中加入「正規化」的簡短說明，例如：在多個假設下，分母的求和把所有可能的情況加起來，使後驗機率的總和為 1。此外，可補充一個簡單的例子（如醫學檢驗或硬幣投擲）說明先驗、似然與後驗的關係，並明確指出 $P(B)$ 需要透過全機率定理計算，而不是固定常數。 |
| 16610.4 | draft | info | #2 第2版不過，重新生成 |
| 16631.3 | check.rule | fail | #2 第3版：重點過長：['在多個假設 $A_1\\dots…'] |
| 16631.3 | check.numeric | ok | #2 第3版：通過 |
| 16631.3 | draft | flag | #2 第3版不過，已達上限，標記⚑待人工確認 |
| 16631.3 | retrieve | ok | #3 基礎率謬誤與假陽性悖論 ← ['base-rate-fallacy', 'false-positive-paradox', 'medical-diagnosis-example'] |
| 16654.2 | check.rule | fail | #3 第1版：重點過長：['在 disease_test …'] |
| 16654.2 | check.numeric | ok | #3 第1版：通過 |
| 16654.2 | draft | info | #3 第1版不過，重新生成 |
| 16684.5 | check.rule | ok | #3 第2版：通過 |
| 16684.5 | check.numeric | ok | #3 第2版：通過 |
| 16706.7 | check.judge | fail | #3 第2版：缺乏 Wiki 依據或觀念錯誤：['disease_test：先驗 1%、靈敏度 90%、偽陽性 5% 時，後驗約 15.4%。']; 審稿建議：將 disease_test 的數值說明改為與 Wiki 中的範例一致，或在投影片註明此為自行假設的示例並提供計算過程。其餘內容皆有對應的 Wiki 依據，且術語已在來源中解釋，適合基礎機率背景的學生。 |
| 16706.7 | draft | info | #3 第2版不過，重新生成 |
| 16706.8 | draft | info | 每日額度用完，等待回補 11.4 分鐘 |
| 17390.0 | check.rule | fail | #3 第3版：這張應該有 disease_test 範例的 calc 欄位 |
| 17390.0 | check.numeric | ok | #3 第3版：通過 |
| 17390.0 | draft | flag | #3 第3版不過，已達上限，標記⚑待人工確認 |
| 17390.0 | retrieve | ok | #4 貝氏推論的流程 ← ['bayesian-inference', 'bayesian-updating', 'prior-probability'] |
| 17390.1 | draft | info | 每日額度用完，等待回補 20.4 分鐘 |
| 18615.6 | check.rule | ok | #4 第1版：通過 |
| 18615.6 | check.numeric | ok | #4 第1版：通過 |
| 18615.7 | check.judge | info | 每日額度用完，等待回補 18.3 分鐘 |
| 19718.3 | check.judge | ok | #4 第1版：通過 |
| 19718.4 | draft | ok | #4 第1版通過 |
| 19718.4 | retrieve | ok | #5 共軛先驗與 Beta‑Binomial 範例 ← ['conjugate-prior', 'beta-binomial-example', 'prior-probability'] |
| 19718.6 | draft | info | 每日額度用完，等待回補 22.3 分鐘 |
| 21073.9 | check.rule | fail | #5 第1版：重點過長：['使用 Beta‑Binomia…'] |
| 21073.9 | check.numeric | ok | #5 第1版：通過 |
| 21073.9 | draft | info | #5 第1版不過，重新生成 |
| 21074.0 | draft | info | 每日額度用完，等待回補 27.7 分鐘 |
| 23018.6 | check.rule | ok | #5 第2版：通過 |
| 23018.6 | check.numeric | ok | #5 第2版：通過 |
| 23018.9 | check.judge | info | 每日額度用完，等待回補 18.0 分鐘 |
| 24114.1 | check.judge | fail | #5 第2版：初學者不易懂，未定義術語：['MLE']; 審稿建議：整體內容與 Wiki 資料相符，統計概念正確。建議在投影片中加入對 'MLE'（最大概似估計）的簡短說明，或改用「樣本比例」等更易懂的詞彙，以免未接觸過此概念的學生感到困惑。 |
| 24114.1 | draft | info | #5 第2版不過，重新生成 |
| 24114.3 | draft | info | 每日額度用完，等待回補 25.9 分鐘 |
| 25711.6 | check.rule | ok | #5 第3版：通過 |
| 25711.6 | check.numeric | ok | #5 第3版：通過 |
| 25711.7 | check.judge | info | 每日額度用完，等待回補 22.9 分鐘 |
| 27084.4 | check.judge | fail | #5 第3版：初學者不易懂，未定義術語：['95% 信賴區間', '點估計']; 審稿建議：整體內容與 Wiki 資料相符，統計概念正確。建議在投影片中簡要說明「95% 信賴區間」與「點估計」的意義，或改用「後驗分布的可信區間」等較易理解的說法，避免未定義術語影響初學者理解。 |
| 27084.4 | draft | flag | #5 第3版不過，已達上限，標記⚑待人工確認 |
| 27084.5 | retrieve | ok | #6 可信區間與結果解讀 ← ['credible-interval', 'bayesian-inference'] |
| 27084.6 | draft | info | 每日額度用完，等待回補 16.7 分鐘 |
| 28130.2 | check.rule | ok | #6 第1版：通過 |
| 28130.2 | check.numeric | ok | #6 第1版：通過 |
| 28130.4 | check.judge | info | 每日額度用完，等待回補 16.8 分鐘 |
| 29180.8 | check.judge | fail | #6 第1版：初學者不易懂，未定義術語：['後驗分佈', '密度', '模式', '中位數', '解析法', 'MCMC']; 審稿建議：建議在投影片中加入簡短定義： - 後驗分佈：在觀測資料後，參數的機率分佈。 - 密度：指機率密度函數的高度，表示參數取某值的相對可能性。 - 模式 (mode)：後驗分佈中機率密度最高的點。 - 中位數：使分佈左右各有 50% 資料的值。 - 解析法：利用已知的 |
| 29180.8 | draft | info | #6 第1版不過，重新生成 |
| 29180.9 | draft | info | 每日額度用完，等待回補 22.4 分鐘 |
| 30607.7 | check.rule | ok | #6 第2版：通過 |
| 30607.7 | check.numeric | ok | #6 第2版：通過 |
| 30607.9 | check.judge | info | 每日額度用完，等待回補 16.8 分鐘 |
| 31618.0 | check.judge | fail | #6 第2版：初學者不易懂，未定義術語：['SCI', 'MCI', 'MCMC']; 審稿建議：1. 在首次出現 SCI、MCI、MCMC 時加入簡短說明，例如：    - SCI（Smallest Credible Interval，最小可信區間）    - MCI（Median Credible Interval，等尾可信區間）    - MCMC（Markov Chain Monte Ca |
| 31618.0 | draft | info | #6 第2版不過，重新生成 |
| 31618.1 | draft | info | 每日額度用完，等待回補 22.9 分鐘 |
| 32992.2 | draft | info | 每日額度用完，等待回補 1.2 分鐘 |
| 33064.5 | check.rule | ok | #6 第3版：通過 |
| 33064.5 | check.numeric | ok | #6 第3版：通過 |
| 33064.6 | check.judge | info | 每日額度用完，等待回補 19.6 分鐘 |
| 34241.3 | check.judge | info | 每日額度用完，等待回補 1.4 分鐘 |
| 34354.7 | check.judge | ok | #6 第3版：通過 |
| 34354.7 | draft | ok | #6 第3版通過 |
| 34354.7 | retrieve | ok | #7 醫學診斷實務：結合所有概念 ← ['medical-diagnosis-example', 'bayes-theorem', 'base-rate-fallacy', 'false-positive-paradox'] |
| 34354.8 | draft | info | 每日額度用完，等待回補 23.9 分鐘 |
| 35793.1 | check.rule | ok | #7 第1版：通過 |
| 35793.1 | check.numeric | ok | #7 第1版：通過 |
| 35793.3 | check.judge | info | 每日額度用完，等待回補 23.5 分鐘 |
| 37201.1 | check.judge | info | 每日額度用完，等待回補 1.5 分鐘 |
| 37292.3 | check.judge | fail | #7 第1版：缺乏 Wiki 依據或觀念錯誤：['先驗機率（先驗）代表疾病在一般族群的發生率，這裡是 1%。', '靈敏度是測試在真患病者中呈陽性的機率，給定為 90%。', '偽陽性率是測試在未患病者中誤判為陽性的機率，這裡是 5%。', '在 10,000 人的族群中，根據給定參數，真陽性 90 人、偽陽性 495 人，最終陽性者中實際患病機率為 15.4%。']; 審稿建議：1. 將所有數值 |
| 37292.3 | draft | info | #7 第1版不過，重新生成 |
| 37292.4 | draft | info | 每日額度用完，等待回補 31.5 分鐘 |
| 39184.1 | draft | info | 每日額度用完，等待回補 2.2 分鐘 |
| 39316.7 | check.rule | ok | #7 第2版：通過 |
| 39316.7 | check.numeric | ok | #7 第2版：通過 |
| 39316.8 | check.judge | info | 每日額度用完，等待回補 26.0 分鐘 |
| 40876.9 | check.judge | ok | #7 第2版：通過 |
| 40876.9 | draft | ok | #7 第2版通過 |
| 40877.1 | deck_review | info | 每日額度用完，等待回補 10.1 分鐘 |
| 41506.0 | deck_review | fail | 整體結構清晰，概念大多循序漸進，但有少數關鍵術語（全機率定理、二項分布、SCI/MCI）在使用前未充分鋪陳，且部分進階內容對初學者可能造成負擔。調整上述三張投影片即可提升易懂度與連貫性。｜需修改 [2, 6, 5] |
| 41506.0 | retrieve | ok | #2 貝氏定理：從條件機率到原因機率 ← ['bayes-theorem', 'prior-probability'] |
| 41506.1 | draft | info | 每日額度用完，等待回補 17.9 分鐘 |
| 42579.9 | check.rule | fail | #2 第1版：重點過長：['全機率定理：若 {A₁…A_k…', '貝氏定理把先驗機率 $P(A)…', '在單一事件情況下，公式為 $P…', '若有多個互斥且完整的假設 $A…'] |
| 42579.9 | check.numeric | ok | #2 第1版：通過 |
| 42579.9 | draft | info | #2 第1版不過，重新生成 |
| 42580.1 | draft | info | 每日額度用完，等待回補 21.7 分鐘 |
| 43883.7 | check.rule | ok | #2 第2版：通過 |
| 43883.7 | check.numeric | ok | #2 第2版：通過 |
| 43883.9 | check.judge | info | 每日額度用完，等待回補 13.8 分鐘 |
| 44747.4 | check.judge | fail | #2 第2版：缺乏 Wiki 依據或觀念錯誤：['先驗$P(A)$與似然$P(B／A)$相乘，得到後驗$P(A／B)$。']; 初學者不易懂，未定義術語：['全機率', '先驗', '似然', '後驗']; 審稿建議：1. 修正第四點說明，應補上除以證據項 P(B)：先驗 P(A) 與似然 P(B／A) 相乘再除以 P(B) 才得到後驗 P(A／B)。 2. 為避免初學者困惑，於投影片或備註中簡要 |
| 44747.4 | draft | info | #2 第2版不過，重新生成 |
| 44747.6 | draft | info | 每日額度用完，等待回補 21.8 分鐘 |
| 46058.6 | draft | info | 每日額度用完，等待回補 1.8 分鐘 |
| 46166.7 | check.rule | fail | #2 第3版：重點過長：['先驗機率（prior prob…'] |
| 46166.7 | check.numeric | ok | #2 第3版：通過 |
| 46166.7 | draft | flag | #2 第3版不過，已達上限，標記⚑待人工確認 |
| 46166.7 | retrieve | ok | #6 可信區間與結果解讀 ← ['credible-interval', 'bayesian-inference'] |
| 46166.9 | draft | info | 每日額度用完，等待回補 18.9 分鐘 |
| 47302.7 | check.rule | ok | #6 第1版：通過 |
| 47302.7 | check.numeric | ok | #6 第1版：通過 |
| 47302.8 | check.judge | info | 每日額度用完，等待回補 15.3 分鐘 |
| 48218.1 | check.judge | info | 每日額度用完，等待回補 2.8 分鐘 |
| 48388.2 | check.judge | info | 每日額度用完，等待回補 4.3 分鐘 |
| 48646.8 | check.judge | fail | #6 第1版：缺乏 Wiki 依據或觀念錯誤：['95% 可信區間表示 $P(a\\le\\theta\\mid資料)=0.95$。', '公式欄位的 $P(a \\le \\theta \\mid \\text{資料}) = \\gamma$（缺少上界 $b$）']; 審稿建議：1. 修正公式為完整的區間形式：$P(a \le \theta \le b \mid \text{資料}) = \ga |
| 48646.8 | draft | info | #6 第1版不過，重新生成 |
| 48646.9 | draft | info | 每日額度用完，等待回補 18.6 分鐘 |
| 49762.4 | check.rule | ok | #6 第2版：通過 |
| 49762.4 | check.numeric | ok | #6 第2版：通過 |
| 49762.7 | check.judge | info | 每日額度用完，等待回補 18.3 分鐘 |
| 50859.7 | check.judge | fail | #6 第2版：初學者不易懂，未定義術語：['最高密度區間', '等尾區間', 'MCMC', '解析求分位']; 審稿建議：內容與 Wiki 基本一致，但對於初學者仍有未解釋的術語。建議在投影片或講稿中加入簡短定義： - 最高密度區間（HDI）：在後驗分布中，密度最高的連續區間，使其內的總機率等於所設定的可信度。 - 等尾區間（Equal‑tailed interval）：取後驗分布的兩側分位數， |
| 50859.8 | draft | info | #6 第2版不過，重新生成 |
| 50859.9 | draft | info | 每日額度用完，等待回補 21.5 分鐘 |
| 52149.6 | check.rule | ok | #6 第3版：通過 |
| 52149.6 | check.numeric | ok | #6 第3版：通過 |
| 52149.8 | check.judge | info | 每日額度用完，等待回補 17.2 分鐘 |
| 53181.9 | check.judge | fail | #6 第3版：初學者不易懂，未定義術語：['HDI', 'MCMC', '解析求分位']; 審稿建議：建議在投影片中加入簡短定義： - HDI（Highest Density Interval）即最高密度區間，說明它是使密度最高且總機率等於設定值的最小區間。 - MCMC（Markov Chain Monte Carlo）簡要說明為一種透過馬可夫鏈抽樣近似後驗分布的方法。 - 解析求分位可說明為在 |
| 53181.9 | draft | flag | #6 第3版不過，已達上限，標記⚑待人工確認 |
| 53181.9 | retrieve | ok | #5 共軛先驗與 Beta‑Binomial 範例 ← ['conjugate-prior', 'beta-binomial-example', 'prior-probability'] |
| 53182.0 | draft | info | 每日額度用完，等待回補 23.8 分鐘 |
| 54608.1 | draft | info | 每日額度用完，等待回補 1.2 分鐘 |
| 54682.0 | check.rule | fail | #5 第1版：重點過長：['Beta‑Binomial 範…'] |
| 54682.0 | check.numeric | ok | #5 第1版：通過 |
| 54682.0 | draft | info | #5 第1版不過，重新生成 |
| 54682.1 | draft | info | 每日額度用完，等待回補 28.1 分鐘 |
| 56372.3 | check.rule | ok | #5 第2版：通過 |
| 56372.4 | check.numeric | ok | #5 第2版：通過 |
| 56372.5 | check.judge | info | 每日額度用完，等待回補 21.6 分鐘 |
| 57672.2 | check.judge | ok | #5 第2版：通過 |
| 57672.2 | draft | ok | #5 第2版通過 |