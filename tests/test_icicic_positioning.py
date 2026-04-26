import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ICICIC_SCRIPTS = REPO_ROOT / "scripts" / "icicic2026"
if str(ICICIC_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(ICICIC_SCRIPTS))

from analyze_matched_subset import run_analysis  # noqa: E402
from analyze_external_mini import run_analysis as run_external_analysis  # noqa: E402
from build_comparison_matrix import build_matrix  # noqa: E402
from build_external_mini_manifest import build_manifest as build_external_manifest  # noqa: E402
from build_matched_subset_manifest import build_manifest as build_matched_manifest  # noqa: E402


MEMBERSHIP_CONFIG = REPO_ROOT / "configs" / "scis" / "fuzzy_membership_v1.yaml"
MATCHED_CONFIG = REPO_ROOT / "configs" / "icicic" / "benchmark_positioning_v1.yaml"
EXTERNAL_CONFIG = REPO_ROOT / "configs" / "icicic" / "external_mini_comparison_v1.yaml"


def make_record(target_mode: str, repetition: int, scores: dict[str, int]) -> dict:
    return {
        "manifest_row": repetition,
        "run_id": "fixture",
        "stage": "sanity",
        "design_id": "icicic2026_benchmark_positioning_v1",
        "model_id": "m1",
        "provider": "fixture",
        "route": "fixture",
        "language": "en",
        "story_id": "T1",
        "target_mode": target_mode,
        "target_label": target_mode,
        "persona_id": "p0",
        "persona_label": "neutral_reader",
        "temperature": 0.4,
        "top_p": 1.0,
        "repetition": repetition,
        "ok": True,
        "validation_errors": [],
        "parsed": {
            "story_id": "T1",
            "persona_id": "p0",
            "language": "en",
            "scores": scores,
            "reasons": {emotion: f"{emotion} reason" for emotion in scores},
        },
    }


class IcicicPositioningTest(unittest.TestCase):
    def test_build_comparison_matrix_writes_csv_and_tex(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "matrix"
            summary = build_matrix(output_dir)

            self.assertEqual(summary["n_rows"], 4)
            csv_path = output_dir / "benchmark_coverage_matrix.csv"
            tex_path = output_dir / "benchmark_coverage_matrix.tex"
            self.assertTrue(csv_path.exists())
            self.assertTrue(tex_path.exists())
            with csv_path.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual([row["benchmark"] for row in rows], [
                "EQ-Bench",
                "EmoBench",
                "SECEU / Emotion Understanding",
                "EQ-Fuzzy matched subset",
            ])

    def test_build_matched_subset_sanity_manifest_counts_and_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.csv"
            rows = build_matched_manifest(
                repo_root=REPO_ROOT,
                config_path=MATCHED_CONFIG,
                stage="sanity",
                output_path=output,
            )

            self.assertEqual(len(rows), 4)
            self.assertEqual({row["language"] for row in rows}, {"en"})
            self.assertEqual({row["story_id"] for row in rows}, {"T1"})
            self.assertEqual({row["target_mode"] for row in rows}, {"reader_side", "character_side"})
            self.assertEqual({row["prompt_version"] for row in rows}, {"icicic_eq_fuzzy_matched_subset_v1"})
            self.assertEqual({row["schema_version"] for row in rows}, {"shared_emotion_scores_v1"})
            self.assertTrue(output.exists())
            self.assertTrue((output.parent / "manifest_summary.json").exists())

    def test_external_manifest_requires_curated_public_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                build_external_manifest(
                    repo_root=Path(tmp),
                    config_path=EXTERNAL_CONFIG,
                    output_path=Path(tmp) / "manifest.csv",
                )

    def test_analyze_matched_subset_fixture_outputs_target_shift(self):
        records = [
            make_record("reader_side", 1, {"interest": 20, "surprise": 30, "sadness": 40, "anger": 50}),
            make_record("reader_side", 2, {"interest": 30, "surprise": 40, "sadness": 50, "anger": 60}),
            make_record("character_side", 1, {"interest": 60, "surprise": 50, "sadness": 40, "anger": 30}),
            make_record("character_side", 2, {"interest": 70, "surprise": 60, "sadness": 50, "anger": 40}),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw.jsonl"
            raw.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
                encoding="utf-8",
            )
            summary = run_analysis(
                input_jsonl=raw,
                output_dir=tmp_path / "out",
                membership_config_path=MEMBERSHIP_CONFIG,
            )

            self.assertEqual(summary["n_response_rows"], 4)
            self.assertEqual(summary["n_emotion_rows"], 16)
            self.assertEqual(summary["n_cell_rows"], 8)
            self.assertEqual(summary["n_target_shift_rows"], 4)
            self.assertTrue((tmp_path / "out" / "emotion_long.csv").exists())
            self.assertTrue((tmp_path / "out" / "response_profile_entropy.csv").exists())
            self.assertTrue((tmp_path / "out" / "target_shift.csv").exists())

    def test_analyze_external_mini_fixture_outputs_native_summary(self):
        records = [
            {
                "run_id": "fixture",
                "design_id": "icicic2026_external_mini_comparison_v1",
                "manifest_row": 0,
                "model_id": "m1",
                "provider": "fixture",
                "benchmark_id": "eq_bench",
                "item_id": "item1",
                "native_metric": "exact_match",
                "answer_key": "B",
                "ok": True,
                "validation_errors": [],
                "parsed": {
                    "benchmark_id": "eq_bench",
                    "item_id": "item1",
                    "answer": "B",
                    "confidence": 80,
                    "reason": "fixture",
                },
            },
            {
                "run_id": "fixture",
                "design_id": "icicic2026_external_mini_comparison_v1",
                "manifest_row": 1,
                "model_id": "m1",
                "provider": "fixture",
                "benchmark_id": "emobench",
                "item_id": "item2",
                "native_metric": "exact_match",
                "answer_key": "C",
                "ok": True,
                "validation_errors": [],
                "parsed": {
                    "benchmark_id": "emobench",
                    "item_id": "item2",
                    "answer": "D",
                    "confidence": 70,
                    "reason": "fixture",
                },
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw.jsonl"
            raw.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
                encoding="utf-8",
            )
            summary = run_external_analysis(input_jsonl=raw, output_dir=tmp_path / "out")

            self.assertEqual(summary["n_response_rows"], 2)
            self.assertEqual(summary["n_item_rows"], 2)
            self.assertEqual(summary["n_summary_rows"], 2)
            self.assertTrue((tmp_path / "out" / "item_results.csv").exists())
            self.assertTrue((tmp_path / "out" / "benchmark_model_summary.csv").exists())


if __name__ == "__main__":
    unittest.main()
