# ICICIC2026 専用コンテキスト

## 1. このチャットの役割

ICICIC チャットは、**benchmark positioning / matched comparison** を扱う。

中心課題は、

- EQ-Fuzzy の指標は既存 benchmark と比べて何を追加で捉えるか
- reliability / ambiguity / controllability / persona sensitivity のどれが既存 benchmark では抜けやすいか
- conference paper として比較をどこまでコンパクトにまとめるか

である。

---

## 2. スコープ固定

### 採るもの
- matched comparison with existing emotion benchmarks
- aligned prompts / aligned subsets / aligned scoring rules
- compact benchmark methodology framing
- additional value analysis of EQ-Fuzzy metrics
- coverage / sensitivity / robustness の比較表

### 採らないもの
- human-grounded multilingual pilot の再演
- persona×temperature factorial deconfounding の本格実験
- humanities annotation-support workflow

---

## 3. 他活動との差別化

### ICECCME と重ならないようにする
- Japanese human reference への alignment ranking を主題にしない
- EN/ZH drift を主図表にしない

### SCIS と重ならないようにする
- main effect / interaction effect の分離分析を中心にしない
- factorial experiment の novelty を使わない

### SPReAD1000 と重ならないようにする
- application workflow でなく benchmark comparison に徹する

---

## 4. この論文で言うべきこと

- 既存 benchmark は accuracy / agreement / empathy などを測るが、評価の不確実性や controllability を十分に捉えない場合がある
- EQ-Fuzzy 系指標は、単なる勝敗ではなく、曖昧さ・安定性・視点感度を補助的に可視化できる
- 本稿は leaderboard paper ではなく、**what EQ-Fuzzy adds** を問う positioning paper である

---

## 5. この論文で言い過ぎてはいけないこと

- EQ-Fuzzy が既存 benchmark より全面的に優れている、とは言わない
- benchmark の決定版、とは言わない
- human validity をこの論文単独で証明した、とは言わない

---

## 6. 実装面の優先事項

- benchmark adapters を最小限に設計する
- prompts / subsets / score mapping の公平性を文書化する
- 比較対象ごとに何が共通で何が違うかを表にする
- comparison matrix を 1 枚で説明できるようにする

---

## 7. このチャットで扱う論点

- comparison target の選定
- aligned subset の作り方
- additional value claim の言語化
- full paper / extended abstract の見極め

---

## 8. このチャットで扱わない論点

- ICECCME の score drift 詳細
- SCIS の factorial prompt design
- SPReAD1000 の実務導入設計

---

## 9. 次の開始文テンプレート

```text
このチャットは ICICIC2026 専用です。
共通前提は 00_shared_context.md に従います。
本チャットでは、EQ-Fuzzy の benchmark positioning / matched comparison を扱います。
ICECCME の human-grounded multilingual pilot と SCIS の factorial deconfounding は別活動として固定し、本チャットでは既存 benchmark との整列比較と追加価値の説明に集中してください。
```
