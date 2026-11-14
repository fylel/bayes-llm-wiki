# 共軛先驗（Conjugate Prior）
此頁說明共軛先驗的概念、超參數的意義與常見範例，並說明其在貝氏推論中的便利性。

在貝氏機率理論中，若給定概似函數 $p(x\mid\theta)$，後驗分佈 $p(\theta\mid x)$ 與先驗分佈 $p(\theta)$ 屬於同一機率分佈族，則先驗與後驗稱為**共軛分佈（conjugate distributions）**，而先驗稱為**共軛先驗（conjugate prior）**。

共軛先驗的主要好處是能得到封閉形式（closed‑form）的後驗分佈，避免數值積分的需求；同時也能直觀說明資料如何更新先驗。

---
### 1. 代數便利性
若先驗與後驗同屬一個分佈族，更新公式往往只涉及**超參數（hyperparameters）**的簡單加法或乘法。例如在二項-貝塔情況，先驗 $\text{Beta}(\alpha,\beta)$ 觀測 $s$ 次成功、$f$ 次失敗後，後驗變為 $\text{Beta}(\alpha+s,\beta+f)$。

---
### 2. 超參數與偽觀測
超參數可被解釋為**偽觀測（pseudo‑observations）**：
- 在 Beta 分佈中，$\alpha$、$\beta$ 分別對應 $\alpha-1$ 次成功與 $\beta-1$ 次失敗（若以後驗模式為基礎），或 $\alpha$、$\beta$ 次成功與失敗（若以後驗均值為基礎）。
- 這種解釋有助於直觀設定先驗，尤其在資料稀少時。

---
### 3. 動態系統觀點
將超參數視為系統狀態，隨著新資料到來而更新，形成離散時間的**動態系統（dynamical system）**。不同的起始超參數會產生不同的學習軌跡，類似遞迴貝氏估計（recursive Bayesian estimation）。

---
### 4. 常見共軛配對（指數族）
| 概似分佈（Likelihood） | 共軛先驗 | 後驗形式 |
|------------------------|----------|----------|
| 二項分佈（Binomial）   | Beta     | Beta     |
| 正態分佈（已知變異）   | 正態（Normal）| 正態 |
| 正態分佈（未知變異）   | Inverse‑Gamma / Wishart | 同族 |
| 泊松分佈（Poisson）   | Gamma    | Gamma |
| 多項分佈（Multinomial）| Dirichlet| Dirichlet |

---
### 5. 實務範例概述
- **二項‑貝塔**：觀測成功次數 $s$、失敗次數 $f$，先驗 $\text{Beta}(\alpha,\beta)$ 更新為 $\text{Beta}(\alpha+s,\beta+f)$。
- **Gamma‑Poisson**：以 Gamma 先驗 $\text{Gamma}(\alpha,\beta)$ 估計泊松率 $\lambda$，觀測 $n$ 個計數 $x_i$ 後，後驗為 $\text{Gamma}(\alpha+\sum x_i,\,\beta+n)$，其後驗預測分佈為負二項分佈（Negative Binomial）。

---
## 來源
- conjugate_prior
