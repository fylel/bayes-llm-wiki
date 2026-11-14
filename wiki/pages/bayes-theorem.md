# Bayes' Theorem
貝氏定理（Bayes' theorem）提供從條件機率反推原因機率的公式。

貝氏定理的數學式為
$$
P(A|B)=\frac{P(B|A)\,P(A)}{P(B)}
$$
其中 $A$、$B$ 為任意事件且 $P(B)\neq0$。

- $P(A|B)$：在已知 $B$ 成立的情況下 $A$ 發生的條件機率，也稱**後驗機率（posterior probability）**。
- $P(B|A)$：在已知 $A$ 成立的情況下 $B$ 發生的條件機率，常被解釋為**概似函數（likelihood）**在 $A$ 處的取值。
- $P(A)$、$P(B)$：不帶條件的機率，稱為**先驗機率（prior probability）**或邊際機率（marginal probability）。

若有一組互斥且完整的事件 $A_1, A_2,\dots, A_k$（即必有且只能發生其中一個），則結合全機率定理可得
$$
P(A_i|B)=\frac{P(A_i)\,P(B|A_i)}{\sum_{j=1}^{k}P(A_j)\,P(B|A_j)}
$$
此式在多類別分類或模型比較時特別有用。

**歷史簡述**：貝氏定理由 18 世紀的統計學家兼牧師 Thomas Bayes（托馬斯·貝氏）首次提出，1763 年由其友人 Richard Price（理查德·普賴斯）編輯發表。後來 Pierre‑Simon Laplace（皮埃爾‑西蒙·拉普拉斯）獨立發展並擴充此結果，使其成為現代貝氏統計的核心。

**應用**：貝氏定理是貝氏推論（[[bayesian-inference]]）的基礎，透過結合先驗與概似得到後驗分佈，進而進行參數估計與模型比較。

## 來源
bayes_theorem
