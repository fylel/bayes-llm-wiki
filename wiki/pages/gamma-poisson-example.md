# Gamma‑Poisson 範例（Gamma‑Poisson Example）
展示 Gamma 分佈作為泊松分佈（Poisson）之共軛先驗，並說明後驗預測為負二項分佈的計算步驟。

**模型設定**
- 觀測資料 $x_1,\dots,x_n$ 為計數，假設服從泊松分佈 $\text{Poisson}(\lambda)$，其中 $\lambda>0$ 為事件率。
- 先驗選擇 Gamma 分佈 $\text{Gamma}(\alpha,\beta)$（形狀 $\alpha$, 速率 $\beta$）：
  $$p(\lambda)=\frac{\beta^{\alpha}}{\Gamma(\alpha)}\,\lambda^{\alpha-1}e^{-\beta\lambda}$$

**後驗推導**
泊松概似：
$$p(\mathbf{x}\mid\lambda)=\prod_{i=1}^{n}\frac{\lambda^{x_i}e^{-\lambda}}{x_i!}=\lambda^{\sum x_i}e^{-n\lambda}\times\text{常數}$$
與 Gamma 先驗相乘得到後驗：
$$p(\lambda\mid\mathbf{x}) \propto \lambda^{\alpha-1+\sum x_i}\,e^{-(\beta+n)\lambda}$$
因此後驗仍為 Gamma 分佈，參數更新為：
$$\boxed{\text{Gamma}(\alpha' = \alpha+\sum_{i}x_i,\; \beta' = \beta + n)}$$

**後驗預測（Posterior Predictive）**
對於新觀測 $x_{\text{new}}$，預測分佈為：
$$p(x_{\text{new}}\mid\mathbf{x}) = \int_0^{\infty} p(x_{\text{new}}\mid\lambda)\,p(\lambda\mid\mathbf{x})\,d\lambda$$
代入泊松與 Gamma 後驗，可得負二項分佈（Negative Binomial）：
$$p(x_{\text{new}}=k\mid\mathbf{x}) = \binom{k+\alpha'-1}{k}\left(\frac{\beta'}{\beta'+1}\right)^{\alpha'}\left(\frac{1}{\beta'+1}\right)^{k}$$
其中 $k=0,1,2,\dots$。

**實務示例（租車服務）**
- 觀測三天內在家附近可見的車輛數 $\mathbf{x}=[3,4,1]$。
- 先驗選 $\text{Gamma}(\alpha=2,\beta=2)$（對平均車輛數有寬鬆的先驗）。
- 總計 $\sum x_i = 8$, $n=3$，得到後驗 $\text{Gamma}(\alpha'=10,\;\beta'=5)$。
- 後驗預測 $P(x>0\mid\mathbf{x}) = 1-\text{NB}(0\mid\alpha'=10,\;p=\frac{\beta'}{\beta'+1}=\frac{5}{6}) \approx 0.84$，較單純的最大概似估計（約 $0.93$）更保守，因考慮了參數不確定性。

---
## 來源
- conjugate_prior
