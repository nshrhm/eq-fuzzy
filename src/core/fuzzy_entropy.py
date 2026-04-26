from __future__ import annotations

"""Claim-neutral fuzzy membership and entropy helpers."""

import math
from pathlib import Path
from typing import Any

import yaml


FAMILY_ORDER = ("legacy_linear_v1", "sigmoid_s_v1")


def load_membership_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def clamp_score(x: float, score_range: tuple[float, float] = (0.0, 100.0)) -> float:
    lo, hi = score_range
    return min(max(float(x), lo), hi)


def linear_ramp(x: float, lo: float, hi: float) -> float:
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return (x - lo) / (hi - lo)


def s_basis(z: float, b: float = 0.1, c: float = 0.9) -> float:
    mid = (b + c) / 2.0
    if z <= b:
        return 0.0
    if z <= mid:
        return 2.0 * ((z - b) ** 2) / ((c - b) ** 2)
    if z < c:
        return 1.0 - 2.0 * ((z - c) ** 2) / ((c - b) ** 2)
    return 1.0


def sigmoid_interval(x: float, lo: float, hi: float) -> float:
    mid = (lo + hi) / 2.0
    gain = 2.0 * math.log(9.0) / (hi - lo)
    return 1.0 / (1.0 + math.exp(-gain * (x - mid)))


def sigmoid_s_ramp(x: float, lo: float, hi: float) -> float:
    return s_basis(sigmoid_interval(x, lo, hi))


def membership_legacy_linear_v1(x: float) -> dict[str, float]:
    x = clamp_score(x)
    low = 1.0 - linear_ramp(x, 0.0, 30.0)

    if x <= 10.0:
        medium = 0.0
    elif x <= 30.0:
        medium = linear_ramp(x, 10.0, 30.0)
    elif x <= 50.0:
        medium = 1.0
    elif x <= 70.0:
        medium = 1.0 - linear_ramp(x, 50.0, 70.0)
    else:
        medium = 0.0

    high = linear_ramp(x, 50.0, 100.0)
    return {"low": low, "medium": medium, "high": high}


def membership_sigmoid_s_v1(x: float) -> dict[str, float]:
    x = clamp_score(x)
    low = 1.0 - sigmoid_s_ramp(x, 0.0, 30.0)

    if x <= 10.0:
        medium = 0.0
    elif x < 30.0:
        medium = sigmoid_s_ramp(x, 10.0, 30.0)
    elif x <= 50.0:
        medium = 1.0
    elif x < 70.0:
        medium = 1.0 - sigmoid_s_ramp(x, 50.0, 70.0)
    else:
        medium = 0.0

    high = sigmoid_s_ramp(x, 50.0, 100.0)
    return {"low": low, "medium": medium, "high": high}


def membership(family: str, x: float) -> dict[str, float]:
    if family == "legacy_linear_v1":
        return membership_legacy_linear_v1(x)
    if family == "sigmoid_s_v1":
        return membership_sigmoid_s_v1(x)
    raise ValueError(f"Unknown membership family: {family}")


def fuzzy_entropy_raw(mu: dict[str, float]) -> float:
    entropy = 0.0
    for value in mu.values():
        if value > 0.0:
            entropy -= value * math.log2(value)
    return entropy


def estimate_hmax(
    family: str,
    *,
    score_range: tuple[float, float] = (0.0, 100.0),
    grid_step: float = 0.001,
) -> float:
    lo, hi = score_range
    n_steps = int(round((hi - lo) / grid_step))
    hmax = 0.0
    for i in range(n_steps + 1):
        x = lo + i * grid_step
        hmax = max(hmax, fuzzy_entropy_raw(membership(family, x)))
    return hmax


def configured_families(config: dict[str, Any]) -> list[str]:
    primary = str(config["primary_family"])
    baselines = [str(family) for family in config.get("baseline_families", [])]
    families = [primary, *baselines]
    return [family for family in FAMILY_ORDER if family in families]


def hmax_by_family(config: dict[str, Any]) -> dict[str, float]:
    score_range = tuple(float(v) for v in config["score_range"])
    grid_step = float(config["entropy"]["normalized"]["grid_step"])
    return {
        family: estimate_hmax(family, score_range=score_range, grid_step=grid_step)
        for family in configured_families(config)
    }


def entropy_for_score(family: str, x: float, hmax: float) -> dict[str, float]:
    mu = membership(family, x)
    h_raw = fuzzy_entropy_raw(mu)
    h_norm = h_raw / hmax if hmax else 0.0
    return {
        "mu_low": mu["low"],
        "mu_medium": mu["medium"],
        "mu_high": mu["high"],
        "H_raw": h_raw,
        "H_norm": h_norm,
    }
