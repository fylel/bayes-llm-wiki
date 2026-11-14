# 先驗機率（Prior Probability）
說明先驗機率與先驗分佈的定義、類型與建構方式。

先驗機率（prior probability）是指在觀測資料加入前，對不確定量（例如模型參數或潛在變數）所假設的機率分佈。它描述了在沒有新證據時，我們對該量的信念。

在貝氏統計（Bayesian statistics）中，貝氏定理（Bayes' rule）規定如何將先驗與新資料（概似）結合，得到後驗分佈（posterior distribution）
$$
\text{posterior} \propto \text{likelihood} \times \text{prior}.
$$

## 先驗的建構方式
- **過去資訊**：利用先前實驗或歷史資料建立先驗。
- **專家意見**：由有經驗的領域專家主觀評估。
- **不偏原則**（principle of indifference）：在沒有資訊時，採用均勻或其他「不資訊」的先驗。
- **機械性考量**：例如正則化（regularization）或特徵選取的需求。
- **層級先驗**（hierarchical priors）：先驗本身可能有參數（超先驗），如 Beta 分佈的參數 \(\alpha,\beta\) 為超先驗。

## 先驗的類型
- **資訊性先驗（informative prior）**：包含具體且明確的資訊，可能強烈影響後驗。
- **弱資訊性先驗（weakly informative prior）**：提供適度的約束，防止極端估計，同時不過度限制結果。
- **無資訊性先驗（uninformative prior）**：表達極少或沒有資訊，常以均勻或對稱形式呈現。

## 數學範例（Beta 先驗與二項概似）
考慮二項分佈的參數 \(p\)，若先驗選擇 Beta 分佈 $\text{Beta}(\alpha,\beta)$，則
$$\pi(p) = \frac{\Gamma(\alpha+\beta)}{\Gamma(\alpha)\Gamma(\beta)} p^{\alpha-1}(1-p)^{\beta-1}.$$
觀測到 $x$ 次成功、$n-x$ 次失敗的二項概似為 $\text{Binom}(n,p)$，其後驗仍為 Beta 分佈 $\text{Beta}(\alpha+x,\beta+n-x)$，顯示先驗與概似的共軛性。

## 與其他頁面的關聯
- 先驗的更新機制詳見 [[bayesian-updating]]。
- 先驗類型的深入說明請參考 [[informative-prior]] 與 [[uninformative-prior]]。

## 來源
- prior_probability
