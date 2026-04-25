import json
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


if __name__ == "__main__":
    unittest.main()
