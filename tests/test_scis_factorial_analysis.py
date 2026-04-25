import json
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCIS_SCRIPTS = REPO_ROOT / "scripts" / "scis2026"
if str(SCIS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCIS_SCRIPTS))

from analyze_factorial_scores import (  # noqa: E402
    EMOTIONS,
    decompose_two_way,
    expand_emotion_rows,
    run_analysis,
)
from fuzzy_entropy import (  # noqa: E402
    estimate_hmax,
    membership_legacy_linear_v1,
    membership_sigmoid_s_v1,
)
from build_primary_tables import build_primary_tables  # noqa: E402
from build_primary_figures import build_primary_figures  # noqa: E402
from bootstrap_main_effects import run_bootstrap  # noqa: E402
from inspect_main_results import run_inspection  # noqa: E402


MEMBERSHIP_CONFIG = REPO_ROOT / "configs" / "scis" / "fuzzy_membership_v1.yaml"


def make_record(persona_id="p1", temperature=0.1, repetition=1, ok=True):
    parsed = {
        "story_id": "T1",
        "persona_id": persona_id,
        "language": "ja",
        "scores": {
            "interest": 10,
            "surprise": 20,
            "sadness": 30,
            "anger": 40,
        },
        "reasons": {emotion: f"{emotion} reason" for emotion in EMOTIONS},
    }
    return {
        "run_id": "fixture",
        "stage": "pilot",
        "design_id": "scis2026_factorial_v1",
        "manifest_row": 0,
        "model_id": "m1",
        "story_id": "T1",
        "condition_id": f"{persona_id}_{temperature}",
        "persona_id": persona_id,
        "persona_label": persona_id,
        "temperature": temperature,
        "temperature_label": str(temperature),
        "repetition": repetition,
        "ok": ok,
        "parsed": parsed if ok else None,
        "validation_errors": [] if ok else ["fixture_error"],
    }


class ScisFactorialAnalysisTest(unittest.TestCase):
    def test_expand_emotion_rows_preserves_invalid_responses(self):
        rows = expand_emotion_rows([make_record(ok=False)])

        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["response_ok"] is False for row in rows))
        self.assertTrue(all(row["ok"] is False for row in rows))
        self.assertTrue(all(row["score"] == "" for row in rows))
        self.assertEqual(rows[0]["validation_errors"], "fixture_error")

    def test_decompose_two_way_balanced_table(self):
        values = {
            ("p1", 0.1): 1.0,
            ("p1", 0.4): 2.0,
            ("p2", 0.1): 3.0,
            ("p2", 0.4): 4.0,
        }
        out = decompose_two_way(values)

        self.assertTrue(out["is_estimable"])
        self.assertEqual(out["missing_cells"], 0)
        self.assertAlmostEqual(out["SS_persona"], 4.0)
        self.assertAlmostEqual(out["SS_temperature"], 1.0)
        self.assertAlmostEqual(out["SS_persona_x_temperature"], 0.0)
        self.assertAlmostEqual(out["separability_share"], 1.0)

    def test_run_analysis_writes_complete_fixture_outputs(self):
        personas = ("p1", "p2", "p3", "p4")
        temperatures = (0.1, 0.4, 0.7, 0.9)
        records = []
        row_id = 0
        for persona_idx, persona_id in enumerate(personas):
            for temp_idx, temperature in enumerate(temperatures):
                record = make_record(persona_id=persona_id, temperature=temperature)
                record["manifest_row"] = row_id
                for emotion_idx, emotion in enumerate(EMOTIONS):
                    record["parsed"]["scores"][emotion] = persona_idx * 10 + temp_idx + emotion_idx
                records.append(record)
                row_id += 1

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw.jsonl"
            raw.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records),
                encoding="utf-8",
            )
            summary = run_analysis(
                input_jsonl=raw,
                output_dir=tmp_path / "out",
                membership_config_path=MEMBERSHIP_CONFIG,
                expected_responses=16,
                expected_emotion_rows=64,
                expected_decomposition_units=4,
            )

            self.assertTrue(summary["readiness_passed"])
            self.assertEqual(summary["primary_membership_family"], "sigmoid_s_v1")
            self.assertEqual(summary["n_response_rows"], 16)
            self.assertEqual(summary["n_emotion_rows"], 64)
            self.assertEqual(summary["n_entropy_rows"], 128)
            self.assertEqual(summary["n_decomposition_units"], 4)
            self.assertTrue((tmp_path / "out" / "emotion_long.csv").exists())
            self.assertTrue((tmp_path / "out" / "entropy_long.csv").exists())
            self.assertTrue((tmp_path / "out" / "entropy_cell_summary.csv").exists())
            self.assertTrue((tmp_path / "out" / "factorial_decomposition.csv").exists())


class ScisFuzzyEntropyTest(unittest.TestCase):
    def test_legacy_linear_v1_representative_points(self):
        expected = {
            0: {"low": 1.0, "medium": 0.0, "high": 0.0},
            30: {"low": 0.0, "medium": 1.0, "high": 0.0},
            50: {"low": 0.0, "medium": 1.0, "high": 0.0},
            70: {"low": 0.0, "medium": 0.0, "high": 0.4},
            100: {"low": 0.0, "medium": 0.0, "high": 1.0},
        }

        for score, memberships in expected.items():
            out = membership_legacy_linear_v1(score)
            for key, value in memberships.items():
                self.assertAlmostEqual(out[key], value)

    def test_sigmoid_s_v1_endpoints_and_bounds(self):
        endpoint_expectations = {
            0: {"low": 1.0},
            30: {"low": 0.0, "medium": 1.0},
            50: {"medium": 1.0, "high": 0.0},
            70: {"medium": 0.0},
            100: {"high": 1.0},
        }
        for score, memberships in endpoint_expectations.items():
            out = membership_sigmoid_s_v1(score)
            for key, value in memberships.items():
                self.assertAlmostEqual(out[key], value)

        for score in range(0, 101):
            out = membership_sigmoid_s_v1(score)
            for value in out.values():
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)
            self.assertAlmostEqual(out["low"] * out["high"], 0.0)

    def test_sigmoid_s_v1_transition_derivatives_are_continuous_near_endpoints(self):
        eps = 1e-4
        left = (membership_sigmoid_s_v1(30.0)["low"] - membership_sigmoid_s_v1(30.0 - eps)["low"]) / eps
        right = (membership_sigmoid_s_v1(30.0 + eps)["low"] - membership_sigmoid_s_v1(30.0)["low"]) / eps
        self.assertAlmostEqual(left, right, places=5)

    def test_hmax_estimation_is_deterministic(self):
        h1 = estimate_hmax("sigmoid_s_v1", grid_step=0.01)
        h2 = estimate_hmax("sigmoid_s_v1", grid_step=0.01)
        self.assertAlmostEqual(h1, h2)
        self.assertGreater(h1, 0.0)


class ScisRetryWorkflowTest(unittest.TestCase):
    def test_build_factorial_retry_manifest_keeps_only_failed_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest = tmp_path / "manifest.csv"
            raw = tmp_path / "raw.jsonl"
            retry = tmp_path / "retry.csv"

            with manifest.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["manifest_row", "model_id"])
                writer.writeheader()
                writer.writerows(
                    [
                        {"manifest_row": "0", "model_id": "m0"},
                        {"manifest_row": "1", "model_id": "m1"},
                        {"manifest_row": "2", "model_id": "m2"},
                    ]
                )
            raw.write_text(
                "\n".join(
                    [
                        json.dumps({"manifest_row": 0, "ok": True}),
                        json.dumps({"manifest_row": 1, "ok": False}),
                        json.dumps({"manifest_row": 2, "ok": True}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCIS_SCRIPTS / "build_factorial_retry_manifest.py"),
                    "--repo-root",
                    str(tmp_path),
                    "--source-manifest",
                    "manifest.csv",
                    "--raw-jsonl",
                    "raw.jsonl",
                    "--output",
                    "retry.csv",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Wrote 1 retry rows", result.stdout)
            with retry.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows, [{"manifest_row": "1", "model_id": "m1"}])

    def test_merge_factorial_retry_replaces_only_retry_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base = tmp_path / "raw.jsonl"
            retry = tmp_path / "retry.jsonl"
            repaired = tmp_path / "repaired.jsonl"
            base_records = [
                {"manifest_row": 0, "ok": True, "value": "base0"},
                {"manifest_row": 1, "ok": False, "value": "base1"},
                {"manifest_row": 2, "ok": True, "value": "base2"},
            ]
            retry_records = [{"manifest_row": 1, "ok": True, "value": "retry1"}]
            base.write_text(
                "\n".join(json.dumps(record) for record in base_records) + "\n",
                encoding="utf-8",
            )
            retry.write_text(
                "\n".join(json.dumps(record) for record in retry_records) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCIS_SCRIPTS / "merge_factorial_retry.py"),
                    "--repo-root",
                    str(tmp_path),
                    "--base-jsonl",
                    "raw.jsonl",
                    "--retry-jsonl",
                    "retry.jsonl",
                    "--output-jsonl",
                    "repaired.jsonl",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Replaced manifest rows: 1", result.stdout)
            repaired_records = [
                json.loads(line) for line in repaired.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([record["value"] for record in repaired_records], ["base0", "retry1", "base2"])


class ScisMainInspectionTest(unittest.TestCase):
    def test_run_inspection_writes_score_and_entropy_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            analysis_dir = tmp_path / "analysis"
            analysis_dir.mkdir()
            output_dir = tmp_path / "inspection"
            doc_path = tmp_path / "phase6.md"
            (analysis_dir / "analysis_summary.json").write_text(
                json.dumps(
                    {
                        "run_id": "fixture",
                        "primary_membership_family": "sigmoid_s_v1",
                        "n_response_rows": 4,
                        "n_response_ok": 4,
                        "n_emotion_rows": 16,
                        "n_missing_score_rows": 0,
                        "n_missing_structural_cells": 0,
                        "n_non_estimable_decomposition_units": 0,
                        "readiness_passed": True,
                    }
                ),
                encoding="utf-8",
            )

            score_rows = []
            entropy_rows = []
            values = {
                ("p1", 0.1): 1.0,
                ("p1", 0.4): 2.0,
                ("p2", 0.1): 3.0,
                ("p2", 0.4): 5.0,
            }
            for (persona_id, temperature), value in values.items():
                score_rows.append(
                    {
                        "model_id": "m1",
                        "story_id": "T1",
                        "condition_id": "",
                        "persona_id": persona_id,
                        "temperature": temperature,
                        "temperature_label": "",
                        "emotion": "interest",
                        "n_attempts": 1,
                        "n_valid_scores": 1,
                        "mean_score": value,
                        "median_score": value,
                        "sd_score": 0.0,
                        "var_score": 0.0,
                        "min_score": value,
                        "max_score": value,
                        "mean_abs_dev_from_median": 0.0,
                        "n_missing_scores": 0,
                    }
                )
                entropy_rows.append(
                    {
                        "model_id": "m1",
                        "story_id": "T1",
                        "condition_id": "",
                        "persona_id": persona_id,
                        "temperature": temperature,
                        "temperature_label": "",
                        "emotion": "interest",
                        "membership_family": "sigmoid_s_v1",
                        "membership_hmax": 1.0,
                        "n_attempts": 1,
                        "n_valid_entropy": 1,
                        "n_missing_entropy": 0,
                        "n_valid_H_raw": 1,
                        "mean_H_raw": value / 10.0,
                        "median_H_raw": value / 10.0,
                        "sd_H_raw": 0.0,
                        "min_H_raw": value / 10.0,
                        "max_H_raw": value / 10.0,
                        "n_valid_H_norm": 1,
                        "mean_H_norm": value / 10.0,
                        "median_H_norm": value / 10.0,
                        "sd_H_norm": 0.0,
                        "min_H_norm": value / 10.0,
                        "max_H_norm": value / 10.0,
                    }
                )

            for path, rows in (
                (analysis_dir / "cell_score_summary.csv", score_rows),
                (analysis_dir / "entropy_cell_summary.csv", entropy_rows),
            ):
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)

            summary = run_inspection(
                analysis_dir=analysis_dir,
                output_dir=output_dir,
                doc_path=doc_path,
                primary_family="sigmoid_s_v1",
                top_n=5,
            )

            self.assertEqual(summary["n_score_decomposition_units"], 1)
            self.assertEqual(summary["n_entropy_decomposition_units"], 1)
            self.assertTrue((output_dir / "metric_decomposition.csv").exists())
            self.assertTrue((output_dir / "top_absolute_interactions.csv").exists())
            self.assertTrue(doc_path.exists())


class ScisPrimaryTablesTest(unittest.TestCase):
    def test_build_primary_tables_writes_csv_and_latex_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            analysis_dir = tmp_path / "analysis"
            inspection_dir = tmp_path / "inspection"
            output_dir = tmp_path / "tables"
            doc_path = tmp_path / "phase7.md"
            analysis_dir.mkdir()
            inspection_dir.mkdir()

            (analysis_dir / "analysis_summary.json").write_text(
                json.dumps(
                    {
                        "run_id": "fixture",
                        "stage": "main",
                        "membership_hmax": {
                            "sigmoid_s_v1": 1.0,
                            "legacy_linear_v1": 1.1,
                        },
                        "n_response_rows": 4,
                        "n_response_ok": 4,
                        "n_emotion_rows": 16,
                        "n_missing_score_rows": 0,
                        "n_missing_structural_cells": 0,
                        "n_non_estimable_decomposition_units": 0,
                    }
                ),
                encoding="utf-8",
            )
            (analysis_dir / "entropy_family_comparison.csv").write_text(
                "\n".join(
                    [
                        "primary_family,baseline_family,n_cell_pairs,pearson_H_norm_cell_mean,mean_abs_H_norm_diff,max_abs_H_norm_diff",
                        "sigmoid_s_v1,legacy_linear_v1,16,0.9,0.1,0.2",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            metric_rows = [
                {
                    "metric": "score",
                    "model_id": "m1",
                    "story_id": "T1",
                    "emotion": "interest",
                    "is_estimable": "True",
                    "missing_cells": "0",
                    "SS_persona": "4.0",
                    "SS_temperature": "1.0",
                    "SS_persona_x_temperature": "1.0",
                    "interaction_burden": "0.166667",
                    "separability_share": "0.833333",
                    "total_SS": "6.0",
                },
                {
                    "metric": "H_norm_sigmoid_s_v1",
                    "model_id": "m1",
                    "story_id": "T1",
                    "emotion": "interest",
                    "is_estimable": "True",
                    "missing_cells": "0",
                    "SS_persona": "0.4",
                    "SS_temperature": "0.1",
                    "SS_persona_x_temperature": "0.1",
                    "interaction_burden": "0.166667",
                    "separability_share": "0.833333",
                    "total_SS": "0.6",
                },
            ]
            for name in (
                "metric_decomposition.csv",
                "top_interaction_burdens.csv",
                "top_absolute_interactions.csv",
            ):
                with (inspection_dir / name).open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(metric_rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(metric_rows)
            (inspection_dir / "inspection_summary.json").write_text("{}", encoding="utf-8")

            summary = build_primary_tables(
                analysis_dir=analysis_dir,
                inspection_dir=inspection_dir,
                output_dir=output_dir,
                doc_path=doc_path,
                primary_family="sigmoid_s_v1",
                top_case_limit_each=1,
            )

            self.assertEqual(summary["n_effect_summary_rows"], 2)
            self.assertEqual(summary["n_model_metric_rows"], 2)
            self.assertTrue((output_dir / "table2_effect_summary.csv").exists())
            self.assertTrue((output_dir / "table2_effect_summary.tex").exists())
            self.assertTrue((output_dir / "primary_table_summary.json").exists())
            self.assertTrue(doc_path.exists())


class ScisPrimaryFiguresTest(unittest.TestCase):
    def test_build_primary_figures_writes_png_and_latex_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            analysis_dir = tmp_path / "analysis"
            inspection_dir = tmp_path / "inspection"
            tables_dir = tmp_path / "tables"
            output_dir = tmp_path / "figures"
            doc_path = tmp_path / "phase8.md"
            for directory in (analysis_dir, inspection_dir, tables_dir):
                directory.mkdir()

            top_rows = [
                {
                    "metric": "H_norm_sigmoid_s_v1",
                    "model_id": "m1",
                    "model_label": "M1",
                    "story_id": "T1",
                    "emotion": "interest",
                    "SS_persona": "0.4",
                    "SS_temperature": "0.1",
                    "SS_persona_x_temperature": "0.2",
                    "total_SS": "0.7",
                    "interaction_burden": "0.285714",
                    "separability_share": "0.714286",
                },
                {
                    "metric": "score",
                    "model_id": "m1",
                    "model_label": "M1",
                    "story_id": "T1",
                    "emotion": "interest",
                    "SS_persona": "4.0",
                    "SS_temperature": "1.0",
                    "SS_persona_x_temperature": "2.0",
                    "total_SS": "7.0",
                    "interaction_burden": "0.285714",
                    "separability_share": "0.714286",
                },
            ]
            for name in ("top_interaction_burdens.csv", "top_absolute_interactions.csv"):
                with (inspection_dir / name).open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(top_rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(top_rows)

            score_rows = []
            entropy_rows = []
            for persona_idx, persona_id in enumerate(("p1", "p2", "p3", "p4")):
                for temp_idx, temperature in enumerate((0.1, 0.4, 0.7, 0.9)):
                    score = 10.0 + persona_idx * 10.0 + temp_idx
                    score_rows.append(
                        {
                            "model_id": "m1",
                            "story_id": "T1",
                            "condition_id": "",
                            "persona_id": persona_id,
                            "temperature": temperature,
                            "temperature_label": "",
                            "emotion": "interest",
                            "mean_score": score,
                        }
                    )
                    entropy_rows.append(
                        {
                            "model_id": "m1",
                            "story_id": "T1",
                            "condition_id": "",
                            "persona_id": persona_id,
                            "temperature": temperature,
                            "temperature_label": "",
                            "emotion": "interest",
                            "membership_family": "sigmoid_s_v1",
                            "mean_H_norm": score / 100.0,
                        }
                    )
            for path, rows in (
                (analysis_dir / "cell_score_summary.csv", score_rows),
                (analysis_dir / "entropy_cell_summary.csv", entropy_rows),
            ):
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)

            model_metric_rows = [
                {
                    "model_id": "m1",
                    "model_label": "M1",
                    "metric": "score",
                    "mean_interaction_burden": "0.2",
                },
                {
                    "model_id": "m1",
                    "model_label": "M1",
                    "metric": "H_norm_sigmoid_s_v1",
                    "mean_interaction_burden": "0.3",
                },
            ]
            with (tables_dir / "table3_model_metric_summary.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(model_metric_rows[0].keys()))
                writer.writeheader()
                writer.writerows(model_metric_rows)

            summary = build_primary_figures(
                analysis_dir=analysis_dir,
                inspection_dir=inspection_dir,
                tables_dir=tables_dir,
                output_dir=output_dir,
                doc_path=doc_path,
                primary_family="sigmoid_s_v1",
            )

            self.assertEqual(summary["n_figures"], 7)
            self.assertEqual(
                summary["main_text_figures"],
                [
                    "figure1a_prior_diagonal_design",
                    "figure1b_factorial_design",
                    "figure2a_entropy_heatmap",
                    "figure2b_score_heatmap",
                    "figure3_model_metric_interaction_heatmap",
                ],
            )
            self.assertTrue((output_dir / "figure1_design_comparison.png").exists())
            self.assertTrue((output_dir / "figure1a_prior_diagonal_design.png").exists())
            self.assertTrue((output_dir / "figure1b_factorial_design.png").exists())
            self.assertTrue((output_dir / "figure2_representative_heatmaps.png").exists())
            self.assertTrue((output_dir / "figure2a_entropy_heatmap.png").exists())
            self.assertTrue((output_dir / "figure2b_score_heatmap.png").exists())
            self.assertTrue((output_dir / "figure3_model_metric_interaction_heatmap.png").exists())
            self.assertTrue((output_dir / "figure_manifest.csv").exists())
            self.assertTrue((output_dir / "figure1_design_comparison.tex").exists())
            self.assertTrue((output_dir / "figure1a_prior_diagonal_design.tex").exists())
            self.assertTrue((output_dir / "figure2a_entropy_heatmap.tex").exists())
            self.assertTrue(doc_path.exists())


class ScisBootstrapEffectsTest(unittest.TestCase):
    def test_run_bootstrap_writes_ci_outputs(self):
        personas = ("p1", "p2")
        temperatures = (0.1, 0.4)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw = tmp_path / "raw.jsonl"
            primary_table = tmp_path / "primary.csv"
            output_dir = tmp_path / "bootstrap"
            doc_path = tmp_path / "phase9.md"

            records = []
            row_id = 0
            for persona_idx, persona_id in enumerate(personas):
                for temp_idx, temperature in enumerate(temperatures):
                    for repetition in range(1, 4):
                        record = make_record(
                            persona_id=persona_id,
                            temperature=temperature,
                            repetition=repetition,
                        )
                        record["manifest_row"] = row_id
                        record["model_id"] = "m1"
                        record["story_id"] = "T1"
                        for emotion_idx, emotion in enumerate(EMOTIONS):
                            record["parsed"]["scores"][emotion] = (
                                10 + persona_idx * 20 + temp_idx * 5 + repetition + emotion_idx
                            )
                        records.append(record)
                        row_id += 1
            raw.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
                encoding="utf-8",
            )
            primary_rows = [
                {
                    "metric": "score",
                    "emotion": emotion,
                    "n_units": 1,
                    "mean_persona_share": 0.8,
                    "mean_temperature_share": 0.1,
                    "mean_interaction_burden": 0.1,
                    "median_interaction_burden": 0.1,
                    "mean_separability_share": 0.9,
                    "median_total_SS": 1.0,
                }
                for emotion in EMOTIONS
            ]
            primary_rows.extend(
                {
                    "metric": "H_norm_sigmoid_s_v1",
                    "emotion": emotion,
                    "n_units": 1,
                    "mean_persona_share": 0.7,
                    "mean_temperature_share": 0.1,
                    "mean_interaction_burden": 0.2,
                    "median_interaction_burden": 0.2,
                    "mean_separability_share": 0.8,
                    "median_total_SS": 1.0,
                }
                for emotion in EMOTIONS
            )
            with primary_table.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(primary_rows[0].keys()))
                writer.writeheader()
                writer.writerows(primary_rows)

            summary = run_bootstrap(
                input_jsonl=raw,
                membership_config=MEMBERSHIP_CONFIG,
                primary_table=primary_table,
                output_dir=output_dir,
                doc_path=doc_path,
                primary_family="sigmoid_s_v1",
                n_bootstrap=5,
                seed=1,
            )

            self.assertEqual(summary["n_records"], 12)
            self.assertEqual(summary["cell_sizes"], [3])
            self.assertEqual(summary["n_ci_rows"], 8)
            self.assertTrue((output_dir / "effect_summary_bootstrap_ci.csv").exists())
            self.assertTrue((output_dir / "effect_summary_bootstrap_ci.tex").exists())
            self.assertTrue((output_dir / "bootstrap_summary.json").exists())
            self.assertTrue(doc_path.exists())


if __name__ == "__main__":
    unittest.main()
