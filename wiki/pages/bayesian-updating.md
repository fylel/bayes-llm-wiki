# Bayesian Updating
貝氏更新（Bayesian updating）是指在觀測到新證據 $E$ 後，依據貝氏定理將先驗機率 $P(H)$ 更新為後驗機率 $P(H\mid E)$ 的過程，並可在後續觀測到更多證據時重複此步驟，形成動態的信念修正機制。

### 單次更新
單次觀測時，貝氏定理給出
$$
P(H\mid E)=\frac{P(E\mid H)\,P(H)}{P(E)}
$$
其中 $P(E)=\sum_i P(E\mid H_i)P(H_i)$ 為證據的邊際機率，確保所有後驗機率加總為 1。

### 多次觀測的遞迴更新
若有一系列獨立且同分佈的觀測 $\mathbf{E}=\{e_1,\dots,e_n\}$，則整體概似為
$$
P(\mathbf{E}\mid H)=\prod_{k=1}^{n}P(e_k\mid H)
$$
將此代入貝氏定理，可直接得到一次性更新的後驗：
$$
P(H\mid \mathbf{E})=\frac{P(\mathbf{E}\mid H)\,P(H)}{\sum_i P(\mathbf{E}\mid H_i)P(H_i)}
$$
這等價於對每一次觀測依序應用單次更新的結果。

### 與貝氏推論的關係
貝氏更新是貝氏推論（[[bayesian-inference]]）的核心步驟，負責在資料累積時持續修正參數或模型的信念分佈。貝氏推論則進一步討論如何選擇先驗、計算後驗以及進行模型比較等更廣泛的議題。

## 來源
bayesian_inference
