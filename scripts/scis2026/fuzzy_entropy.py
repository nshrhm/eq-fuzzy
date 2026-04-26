from __future__ import annotations

"""SCIS 2026 compatibility wrapper for shared fuzzy entropy helpers."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.fuzzy_entropy import (  # noqa: E402,F401
    FAMILY_ORDER,
    clamp_score,
    configured_families,
    entropy_for_score,
    estimate_hmax,
    fuzzy_entropy_raw,
    hmax_by_family,
    linear_ramp,
    load_membership_config,
    membership,
    membership_legacy_linear_v1,
    membership_sigmoid_s_v1,
    s_basis,
    sigmoid_interval,
    sigmoid_s_ramp,
)


DEFAULT_CONFIG = "configs/scis/fuzzy_membership_v1.yaml"
