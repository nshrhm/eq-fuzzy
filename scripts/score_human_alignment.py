import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.iceccme2026.metrics import score_alignment_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--human", required=True)
    parser.add_argument("--model-scores", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--primary-language", default="ja")
    args = parser.parse_args()
    score_alignment_bundle(
        human_summary_path=args.human,
        model_scores_path=args.model_scores,
        output_dir=args.output_dir,
        primary_language=args.primary_language,
    )


if __name__ == "__main__":
    main()
