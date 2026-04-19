# ICECCME 2026 repo: script execution guide

## 前提

- 仮想環境を有効化済み
- `requirements.txt` に `scipy>=1.11` を追加済み
- standalone scripts は repo root を `sys.path` に追加する修正済み
- private texts は以下に配置済み
  - `data/raw_private/texts/ja/T1.txt`
  - `data/raw_private/texts/ja/T2.txt`
  - `data/raw_private/texts/ja/T3.txt`
  - `data/raw_private/texts/en/T1.txt`
  - `data/raw_private/texts/en/T2.txt`
  - `data/raw_private/texts/en/T3.txt`
  - `data/raw_private/texts/zh/T1.txt`
  - `data/raw_private/texts/zh/T2.txt`
  - `data/raw_private/texts/zh/T3.txt`
- human workbook を置く場合
  - `data/raw_private/human/文学短編作品.xlsx`

## 実行順

### 1. 人間データを整形

```bash
python scripts/prepare_human_data.py \
  --input data/raw_private/human/文学短編作品.xlsx \
  --output-dir data/derived_public
```

同等の `main.py` コマンド:

```bash
python main.py prepare-human \
  --input data/raw_private/human/文学短編作品.xlsx \
  --output-dir data/derived_public
```

主要出力:
- `data/derived_public/human_vas_summary.csv`
- `data/derived_public/human_reference_12cell.csv`
- `data/derived_public/human_respondent_summary.csv`

### 2. primary manifest を生成

```bash
python scripts/build_run_manifest.py \
  --config configs/experiment.yaml \
  --models configs/models_default.yaml \
  --output data/manifests/iceccme2026_primary_neutral_manifest.csv
```

同等の `main.py` コマンド:

```bash
python main.py build-manifest \
  --config configs/experiment.yaml \
  --models configs/models_default.yaml \
  --output data/manifests/iceccme2026_primary_neutral_manifest.csv
```

想定行数:
- 540 行 = 6 models × 3 languages × 3 stories × 1 persona(p0) × 10 repeats

確認:

```bash
python - <<'PY'
import pandas as pd
p='data/manifests/iceccme2026_primary_neutral_manifest.csv'
df=pd.read_csv(p)
print(df.shape)
print(df.head())
print(df[['model_id','language','story_id','persona_id']].drop_duplicates().head(20))
PY
```

### 3. prompt を1本だけ確認

```bash
python scripts/render_prompt_preview.py \
  --story-id T1 \
  --persona-id p0 \
  --language ja \
  --text-file data/raw_private/texts/ja/T1.txt \
  --output /tmp/T1_p0_ja_prompt.txt
```

画面に直接出すなら:

```bash
python scripts/render_prompt_preview.py \
  --story-id T1 \
  --persona-id p0 \
  --language ja \
  --text-file data/raw_private/texts/ja/T1.txt
```

### 4. OpenRouter 実行

API key を設定:

```bash
export OPENROUTER_API_KEY='YOUR_KEY_HERE'
```

6件だけ smoke test:

```bash
python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --limit 6 \
  --sleep-sec 1.0 \
  --resume
```

540件を本実行:

```bash
python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --sleep-sec 0.7 \
  --resume
```

### 5. raw 出力を model_scores.csv に正規化

```bash
python main.py normalize-model-scores \
  --input data/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/interim/model_scores.csv
```

### 6. human alignment を採点

```bash
python scripts/score_human_alignment.py \
  --human data/derived_public/human_vas_summary.csv \
  --model-scores data/interim/model_scores.csv \
  --output-dir results/csv \
  --primary-language ja
```

同等の `main.py` コマンド:

```bash
python main.py score-alignment \
  --human data/derived_public/human_vas_summary.csv \
  --model-scores data/interim/model_scores.csv \
  --output-dir results/csv \
  --primary-language ja
```

主要出力:
- `results/csv/model_language_alignment.csv`
- `results/csv/model_language_cell_level.csv`

### 7. primary ranking / language drift table を出力

```bash
python scripts/export_primary_tables.py \
  --alignment results/csv/model_language_alignment.csv \
  --output-dir results/csv \
  --primary-language ja \
  --primary-persona p0
```

主要出力:
- `results/csv/ja_primary_ranking.csv`
- `results/csv/model_language_drift_vs_ja.csv`

## いちばん安全な実行順

```bash
python scripts/prepare_human_data.py \
  --input data/raw_private/human/文学短編作品.xlsx \
  --output-dir data/derived_public

python scripts/build_run_manifest.py \
  --config configs/experiment.yaml \
  --models configs/models_default.yaml \
  --output data/manifests/iceccme2026_primary_neutral_manifest.csv

python scripts/render_prompt_preview.py \
  --story-id T1 \
  --persona-id p0 \
  --language ja \
  --text-file data/raw_private/texts/ja/T1.txt

python run_openrouter_manifest.py \
  --repo-root . \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --texts-dir data/raw_private/texts \
  --output-jsonl data/raw_private/openrouter_primary_raw.jsonl \
  --limit 6 \
  --sleep-sec 1.0 \
  --resume

python main.py normalize-model-scores \
  --input data/raw_private/openrouter_primary_raw.jsonl \
  --manifest data/manifests/iceccme2026_primary_neutral_manifest.csv \
  --join-on-order \
  --output data/interim/model_scores.csv

python scripts/score_human_alignment.py \
  --human data/derived_public/human_vas_summary.csv \
  --model-scores data/interim/model_scores.csv \
  --output-dir results/csv \
  --primary-language ja
```

## 補足

- human は日本語で学生対象に実施しているため、論文本文の main endpoint は `--primary-language ja` に固定するのが妥当。
- EN/ZH は cross-language robustness 用の secondary analysis として扱う。
- `--resume` を付ければ、JSONL に記録済みの `manifest_row` は再実行されない。
- まず 6件、次に 30件、その後に 540件本実行の順が安全。
