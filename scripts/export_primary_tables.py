from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


COLUMN_ALIASES: dict[str, list[str]] = {
    "language": ["language", "lang"],
    "persona": ["persona_id", "persona"],
    "model": ["model_id", "model"],
    "mae": ["mae_to_human", "mae"],
    "pearson": ["pearson_to_human", "pearson_r", "pearson"],
    "spearman": ["spearman_to_human", "spearman_r", "spearman"],
    "drift": ["mean_drift_vs_japanese", "mean_drift_vs_ja", "drift_vs_ja"],
}

REQUIRED_CANONICAL = ["language", "model", "mae", "pearson", "spearman", "drift"]


def detect_columns(df: pd.DataFrame) -> dict[str, str | None]:
    columns = set(df.columns)
    detected: dict[str, str | None] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        detected[canonical] = next((alias for alias in aliases if alias in columns), None)
    missing = [name for name in REQUIRED_CANONICAL if detected[name] is None]
    if missing:
        available = ", ".join(df.columns)
        raise ValueError(f"Missing required alignment columns for {missing}. Available columns: {available}")
    return detected


def add_stable_aliases(df: pd.DataFrame, detected: dict[str, str | None]) -> pd.DataFrame:
    out = df.copy()
    out["lang"] = out[detected["language"]]
    out["model"] = out[detected["model"]]
    out["mae"] = pd.to_numeric(out[detected["mae"]], errors="coerce")
    out["pearson_r"] = pd.to_numeric(out[detected["pearson"]], errors="coerce")
    out["spearman_r"] = pd.to_numeric(out[detected["spearman"]], errors="coerce")
    out["drift_vs_ja"] = pd.to_numeric(out[detected["drift"]], errors="coerce")
    return out


def export_primary_tables(
    *,
    alignment_path: str | Path,
    output_dir: str | Path,
    primary_language: str = "ja",
    primary_persona: str = "p0",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    alignment_path = Path(alignment_path)
    output_dir = Path(output_dir)
    if not alignment_path.exists():
        raise FileNotFoundError(alignment_path)

    alignment = pd.read_csv(alignment_path)
    detected = detect_columns(alignment)
    with_aliases = add_stable_aliases(alignment, detected)

    print("Detected alignment schema:")
    for canonical in COLUMN_ALIASES:
        print(f"  {canonical}: {detected[canonical]}")
    print(f"Loaded {len(with_aliases)} alignment rows from {alignment_path}")

    primary = with_aliases[with_aliases["lang"] == primary_language].copy()
    persona_col = detected["persona"]
    if persona_col is not None:
        before = len(primary)
        primary = primary[primary[persona_col] == primary_persona].copy()
        print(f"Filtered primary persona {primary_persona}: {before} -> {len(primary)} rows")
    else:
        print("No persona column detected; treating alignment rows as already primary-run aggregated.")

    primary = primary.sort_values(
        ["mae", "pearson_r", "spearman_r"],
        ascending=[True, False, False],
        na_position="last",
    )

    drift = with_aliases.sort_values(["model", "drift_vs_ja", "lang"], ascending=[True, True, True]).copy()

    output_dir.mkdir(parents=True, exist_ok=True)
    primary_path = output_dir / "ja_primary_ranking.csv"
    drift_path = output_dir / "model_language_drift_vs_ja.csv"
    primary.to_csv(primary_path, index=False)
    drift.to_csv(drift_path, index=False)

    print(f"Wrote {len(primary)} rows to {primary_path}")
    print(f"Wrote {len(drift)} rows to {drift_path}")
    return primary, drift


def main() -> None:
    parser = argparse.ArgumentParser(description="Export robust primary ranking and language-drift tables.")
    parser.add_argument("--alignment", default="results/csv/model_language_alignment.csv")
    parser.add_argument("--output-dir", default="results/csv")
    parser.add_argument("--primary-language", default="ja")
    parser.add_argument("--primary-persona", default="p0")
    args = parser.parse_args()

    export_primary_tables(
        alignment_path=args.alignment,
        output_dir=args.output_dir,
        primary_language=args.primary_language,
        primary_persona=args.primary_persona,
    )


if __name__ == "__main__":
    main()
