# 二項‑貝塔範例（Beta‑Binomial Example）
說明二項分佈的概似與 Beta 先驗的共軛關係，以及超參數的更新方式。

**模型設定**
- 觀測 $s$ 次成功、$f=n-s$ 次失敗，符合二項分佈 $\text{Binomial}(n,q)$，其中 $q\in[0,1]$ 為成功機率。
- 先驗選擇 Beta 分佈 $\text{Beta}(\alpha,\beta)$：
  $$p(q)=\frac{q^{\alpha-1}(1-q)^{\beta-1}}{B(\alpha,\beta)}$$
  其中 $B(\alpha,\beta)$ 為 Beta 正規化常數。

**後驗推導**
根據貝氏定理：
$$p(q\mid s,f) \propto p(s,f\mid q)\,p(q)$$
將二項概似與 Beta 先驗相乘得到：
$$p(q\mid s,f) \propto q^{s+\alpha-1}(1-q)^{f+\beta-1}$$
因此後驗仍為 Beta 分佈，參數更新為：
$$\boxed{\text{Beta}(\alpha+s,\,\beta+f)}$$

**超參數解釋**
- $\alpha$、$\beta$ 可視為偽觀測：$\alpha-1$ 次成功、$\beta-1$ 次失敗（若以模式為基礎），或 $\alpha$、$\beta$ 次成功、失敗（若以均值為基礎）。
- 每次新資料到來，只需把成功次數加到 $\alpha$，失敗次數加到 $\beta$，即完成更新。

**數值示例**
假設先驗 $\text{Beta}(\alpha=2,\beta=2)$（對稱、稍微集中於 $0.5$），觀測 $n=10$ 次，其中 $s=7$ 次成功、$f=3$ 次失敗。
- 後驗為 $\text{Beta}(2+7,\,2+3)=\text{Beta}(9,5)$。
- 後驗均值 $=\frac{9}{9+5}=0.643$，比先驗均值 $0.5$ 更靠近觀測比例 $0.7$，同時保留不確定性。

---
## 來源
- conjugate_prior
