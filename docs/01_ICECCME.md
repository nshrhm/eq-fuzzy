# ICECCME2026 専用コンテキスト

## 1. このチャットの役割

ICECCME チャットは、**human-grounded multilingual pilot** だけを扱う。

中心課題は、

- Japanese human reference に対してどのモデルが近いか
- EN / ZH 条件でどの程度 drift するか
- compact benchmark としてどこまで工学的に再現可能か

の3点である。

---

## 2. スコープ固定

### 採るもの
- neutral-reader 条件
- 3作品
- Japanese human reference
- 6モデル程度の contemporary LLM comparison
- JA を primary endpoint、EN/ZH を robustness test とする構図
- MAE / Pearson / Spearman / cross-language drift

### 採らないもの
- persona×temperature の本格解析
- fuzzy entropy を論文の主役にすること
- EQ-Fuzzy 全体の提案
- benchmark positioning の本格議論
- matched comparison with EQ-Bench / EmotionBench / EmoBench

---

## 3. 他活動との差別化

### SCIS と重ならないようにする
- persona は neutral-reader のまま固定する
- temperature を主変数にしない
- 因子分離や interaction analysis を主張しない

### ICICIC と重ならないようにする
- 既存 benchmark との head-to-head comparison を主題化しない
- benchmark framework paper ではなく compact pilot として書く

### SPReAD1000 と重ならないようにする
- annotation workflow や review queue の話を入れない
- 応用 PoC ではなく benchmark evaluation に徹する

---

## 4. この論文で言うべきこと

- multilingual variation は human validity と同義ではない
- Japanese human reference に近いモデルと、cross-language robustness が高いモデルは概ね重なるが完全には一致しない
- 小規模でも human-grounded benchmark は model screening に有用である

---

## 5. この論文で言い過ぎてはいけないこと

- multilingual emotional understanding を一般化して評価した、とは言わない
- human-grounded benchmark の決定版、とは言わない
- persona / temperature / ambiguity の統合評価までやった、とは言わない

---

## 6. 実装面の優先事項

- raw JSONL / CSV / figure regeneration を submission version と完全同期させる
- metric 定義を 1 つに固定する
- drift の定義を本文・表・図で完全一致させる
- 翻訳条件の説明を明文化する
- provenance を残す

---

## 7. このチャットで扱う論点

- タイトル調整
- abstract の tightening
- table / figure / body の整合確認
- reviewer が突く limitation の先回り
- ICECCME 向けの short compact framing

---

## 8. このチャットで扱わない論点

- SCIS の factorial design
- ICICIC の benchmark comparison plan
- SPReAD1000 の申請書構成
- monorepo 全体設計の細部

---

## 9. 次の開始文テンプレート

```text
このチャットは ICECCME2026 専用です。
共通前提は 00_shared_context.md に従います。
本チャットでは、human-grounded multilingual pilot としての ICECCME 論文だけを扱います。
neutral-reader 条件、Japanese human reference、EN/ZH robustness、compact engineering benchmark という枠を固定し、SCIS・ICICIC・SPReAD との重複を避けてください。
```
