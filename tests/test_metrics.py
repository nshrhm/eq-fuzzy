from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.core.text_inputs import read_text_file
from src.iceccme2026.metrics import prepare_human_reference, aggregate_model_scores


class MetricsSmokeTest(unittest.TestCase):
    def test_prepare_human_reference(self):
        human = pd.DataFrame(
            {
                "story_id": ["T1", "T1"],
                "emotion": ["interest", "surprise"],
                "mean": [50.0, 25.0],
            }
        )
        out = prepare_human_reference(human)
        self.assertListEqual(list(out.columns), ["story_id", "emotion", "human_mean"])
        self.assertEqual(out.iloc[0]["human_mean"], 50.0)

    def test_aggregate_model_scores(self):
        model_scores = pd.DataFrame(
            {
                "model_id": ["m1", "m1"],
                "provider": ["p", "p"],
                "language": ["ja", "ja"],
                "story_id": ["T1", "T1"],
                "emotion": ["interest", "interest"],
                "score": [20, 40],
            }
        )
        out = aggregate_model_scores(model_scores)
        self.assertAlmostEqual(out.iloc[0]["model_mean"], 30.0)


class TextInputsTest(unittest.TestCase):
    def test_legacy_iceccme_text_path_falls_back_to_shared_texts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            shared = repo_root / "data" / "catalogs" / "texts_private" / "en"
            shared.mkdir(parents=True)
            (shared / "T1.txt").write_text("shared text\n", encoding="utf-8")

            text = read_text_file(
                repo_root / "data" / "iceccme2026" / "raw_private" / "texts",
                "en",
                "T1",
            )

            self.assertEqual(text, "shared text\n")


if __name__ == "__main__":
    unittest.main()
