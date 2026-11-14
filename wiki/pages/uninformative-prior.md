# 無資訊性先驗（Uninformative Prior）
說明無資訊性先驗的定義、常見形式與哲學背景。

無資訊性先驗（uninformative prior），亦稱平坦先驗（flat prior）或擴散先驗（diffuse prior），用來表示對變數幾乎沒有先驗資訊，只提供最小的限制。例如「變數為正」或「變數小於某上限」等客觀限制。

## 原則不偏性（Principle of Indifference）
- 依此原則，所有可能的結果被賦予相等機率。最簡單的例子是三個杯子 A、B、C 隱藏球的位置，均勻先驗 $p(A)=p(B)=p(C)=\frac13$。
- 此種先驗在標籤置換下保持不變，符合對稱性原則。

## 常見形式
- **均勻先驗**：在有限區間 $[a,b]$ 上 $\pi(\theta)=\frac{1}{b-a}$。
- **Jeffreys 先驗**：基於概似的 Fisher 資訊 $I(\theta)$，取 $\pi(\theta)\propto\sqrt{I(\theta)}$，具參數變換不變性。
- **Haldane 先驗**：$\pi(p)\propto p^{-1}(1-p)^{-1}$，在完全不確定的二項參數情況下由對稱性推導而得（雖具爭議）。

## 與後驗的關係
在參數估計問題中，若使用無資訊性先驗，往往後驗主要由概似函數決定，結果與傳統頻率統計的估計值相近。

## 與其他頁面的關聯
- 先驗的基本概念與層級結構請見 [[prior-probability]]。
- 資訊性先驗的比較與說明請參考 [[informative-prior]]。

## 來源
- prior_probability
