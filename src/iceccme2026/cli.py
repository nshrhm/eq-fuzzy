from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.iceccme2026.human_data import prepare_human_outputs
from src.iceccme2026.manifest import build_manifest
from src.iceccme2026.metrics import score_alignment_bundle
from src.iceccme2026.model_scores import normalize_model_scores


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ICECCME 2026 human-grounded repository helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_human = sub.add_parser("prepare-human", help="sanitize the SurveyMonkey workbook")
    p_human.add_argument("--input", required=True)
    p_human.add_argument("--output-dir", required=True)

    p_manifest = sub.add_parser("build-manifest", help="create the multilingual LLM run manifest")
    p_manifest.add_argument("--config", required=True)
    p_manifest.add_argument("--models", required=True)
    p_manifest.add_argument("--output", required=True)

    p_align = sub.add_parser("score-alignment", help="compare model scores against the human reference")
    p_align.add_argument("--human", required=True)
    p_align.add_argument("--model-scores", required=True)
    p_align.add_argument("--output-dir", required=True)
    p_align.add_argument("--primary-language", default="ja")

    p_norm = sub.add_parser("normalize-model-scores", help="normalize raw run outputs into long-format model_scores.csv")
    p_norm.add_argument("--input", required=True)
    p_norm.add_argument("--output", required=True)
    p_norm.add_argument("--manifest")
    p_norm.add_argument("--join-on-order", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "prepare-human":
        prepare_human_outputs(args.input, args.output_dir)
    elif args.command == "build-manifest":
        build_manifest(args.config, args.models, args.output)
    elif args.command == "score-alignment":
        score_alignment_bundle(
            human_summary_path=args.human,
            model_scores_path=args.model_scores,
            output_dir=args.output_dir,
            primary_language=args.primary_language,
        )
    elif args.command == "normalize-model-scores":
        normalize_model_scores(
            input_path=args.input,
            output_path=args.output,
            manifest_path=args.manifest,
            join_on_order=args.join_on_order,
        )
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
