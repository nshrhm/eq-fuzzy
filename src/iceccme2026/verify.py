from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


REPO = Path(__file__).resolve().parents[2]


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def main() -> None:
    human_summary = REPO / 'data/iceccme2026/derived_public/human_vas_summary.csv'
    primary_manifest = REPO / 'data/iceccme2026/manifests/iceccme2026_primary_neutral_manifest.csv'
    secondary_manifest = REPO / 'data/iceccme2026/manifests/iceccme2026_secondary_persona_manifest.csv'
    human_json = REPO / 'results/iceccme2026/json/human_reference_summary.json'
    primary_manifest_json = REPO / 'data/iceccme2026/results/json/iceccme2026_primary_neutral_manifest_summary.json'
    secondary_manifest_json = REPO / 'data/iceccme2026/results/json/iceccme2026_secondary_persona_manifest_summary.json'
    text_catalog = REPO / 'data/catalogs/text_catalog.csv'
    persona_catalog = REPO / 'data/catalogs/persona_catalog.csv'

    for path in [human_summary, primary_manifest, secondary_manifest, human_json, primary_manifest_json, secondary_manifest_json, text_catalog, persona_catalog]:
        assert_exists(path)

    df_h = pd.read_csv(human_summary)
    df_m1 = pd.read_csv(primary_manifest)
    df_m2 = pd.read_csv(secondary_manifest)

    if df_h.shape[0] != 12:
        raise AssertionError(f'Expected 12 human reference rows, found {df_h.shape[0]}')

    if df_m1.shape[0] != 540:
        raise AssertionError(f'Expected 540 primary-manifest rows, found {df_m1.shape[0]}')

    if df_m2.shape[0] != 1080:
        raise AssertionError(f'Expected 1080 secondary-manifest rows, found {df_m2.shape[0]}')

    human_counts = json.loads(human_json.read_text(encoding='utf-8'))
    if human_counts['n_respondents_total'] != 91:
        raise AssertionError('Unexpected respondent count.')

    if human_counts['n_complete_case'] != 86:
        raise AssertionError('Unexpected complete-case count.')

    primary_counts = json.loads(primary_manifest_json.read_text(encoding='utf-8'))
    if primary_counts['n_models'] != 6 or primary_counts['n_personas'] != 1:
        raise AssertionError('Unexpected primary manifest configuration.')

    secondary_counts = json.loads(secondary_manifest_json.read_text(encoding='utf-8'))
    if secondary_counts['n_models'] != 6 or secondary_counts['n_personas'] != 4:
        raise AssertionError('Unexpected secondary manifest configuration.')

    print('Verification passed.')


if __name__ == '__main__':
    main()
