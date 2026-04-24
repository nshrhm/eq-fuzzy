# SCIS2026 専用コンテキスト

## 1. このチャットの役割

SCIS チャットは、**persona×temperature factorial deconfounding** を本命として扱う。

中心課題は、

- persona 効果と temperature 効果をどこまで分離できるか
- reliability / variance / fuzzy entropy / persona effect をどう因子分解するか
- 既発表 *Mathematics* 論文の最大の limitation にどう正面から答えるか

である。

---

## 2. スコープ固定

### 採るもの
- fully crossed persona × temperature design
- factorial analysis
- mixed-effects / ANOVA / bootstrap CI
- interaction plot
- heatmap
- main-effect summary
- 代表モデル subset での conference-scale 実験

### 採らないもの
- multilingual robustness 主体の論文化
- human-grounded validation を必須化すること
- benchmark positioning / matched comparison を中心にすること
- application / workflow PoC の議論

---

## 3. 他活動との差別化

### ICECCME と重ならないようにする
- neutral-reader single persona に戻さない
- JA human reference を主評価にしない
- EN/ZH drift を主図表にしない

### ICICIC と重ならないようにする
- 既存 benchmark との比較は補助実験に留めるか、入れない
- paper の核を benchmark positioning にしない

### SPReAD1000 と重ならないようにする
- annotation support や workflow 指標を入れない
- humanities 実務への適用ではなく、method paper として書く

---

## 4. この論文で言うべきこと

- 既発表では persona と temperature が設計上ペアであり、分離解釈ができなかった
- 今回は independent crossing によって main effects と interaction を記述できる
- fuzzy entropy や variance の変動を、persona diversity と decoding stochasticity の混合から一段整理できる

---

## 5. この論文で言い過ぎてはいけないこと

- 因果推論が完成した、とは言わない
- human validity を十分に証明した、とは言わない
- cross-lingual generalization を示した、とは言わない

---

## 6. 実装面の優先事項

- persona 記述と temperature 指定を prompt レベルで完全分離する
- condition table を固定し、再現可能な YAML / CSV にする
- valid-output / variance / entropy / effect size を最低限の主要指標として固定する
- 代表モデル数を絞っても interaction が見えるよう pilot で確認する

---

## 7. このチャットで扱う論点

- factorial design の確定
- 代表モデル選定
- prompt template の独立化
- main figures / main tables の設計
- full / short の切替基準

---

## 8. このチャットで扱わない論点

- ICECCME の human-grounded ranking
- ICICIC の matched comparison 実装
- SPReAD1000 の PoC 指標

---

## 9. 次の開始文テンプレート

```text
このチャットは SCIS2026 専用です。
共通前提は 00_shared_context.md に従います。
本チャットでは、persona×temperature factorial deconfounding を本命とし、既発表 Mathematics 論文の confounding limitation に答えることだけを扱います。
multilingual robustness、benchmark positioning、annotation workflow は本チャットの主題にしません。
```
