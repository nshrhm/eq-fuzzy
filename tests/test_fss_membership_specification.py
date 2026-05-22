from __future__ import annotations

import math
import sys
import unittest
from itertools import combinations
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FSS_SCRIPT_DIR = REPO_ROOT / "scripts" / "fss2026"
if str(FSS_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(FSS_SCRIPT_DIR))

from membership_specification_lib import (  # noqa: E402
    build_family_sensitivity_matrix,
    build_membership_grid,
    entropy_row,
    family_ids,
    hmax_by_family,
    load_config,
    membership_values,
    score_grid,
)


class FSSMembershipSpecificationTests(unittest.TestCase):
    def test_membership_values_are_bounded(self) -> None:
        config = load_config()
        for family_id in family_ids(config):
            for score in score_grid(config):
                values = membership_values(family_id, score)
                self.assertTrue(values)
                self.assertTrue(all(0.0 <= value <= 1.0 for value in values.values()))

    def test_entropy_values_are_finite_and_normalized(self) -> None:
        config = load_config()
        hmaxes = hmax_by_family(config)
        for family_id in family_ids(config):
            self.assertGreater(hmaxes[family_id], 0.0)
            for score in score_grid(config):
                row = entropy_row(family_id, score, hmaxes[family_id])
                self.assertTrue(math.isfinite(row["H_raw"]))
                self.assertTrue(math.isfinite(row["H_star"]))
                self.assertGreaterEqual(row["H_star"], 0.0)
                self.assertLessEqual(row["H_star"], 1.0 + 1e-9)

    def test_all_families_produce_nonempty_grids(self) -> None:
        config = load_config()
        rows = build_membership_grid(config)
        observed = {row["family_id"] for row in rows}
        self.assertEqual(observed, set(family_ids(config)))
        for family_id in family_ids(config):
            self.assertTrue(any(row["family_id"] == family_id for row in rows))

    def test_sensitivity_matrix_has_unordered_family_pairs(self) -> None:
        config = load_config()
        rows = build_family_sensitivity_matrix(config)
        expected = set(combinations(family_ids(config), 2))
        observed = {(row["family_a"], row["family_b"]) for row in rows}
        self.assertEqual(observed, expected)
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
