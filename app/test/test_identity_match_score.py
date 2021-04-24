from pathlib import Path

import pandas as pd

from src.identity_match_score import IdentityMatchDataframe
from utils.test_utils import (
    get_expected_results_dict,
    get_filename_base,
    get_test_fixtures_path,
)


def test_identity_match_score():
    path_base = get_test_fixtures_path()
    expected_results = pd.DataFrame.from_dict(
        get_expected_results_dict(test_identity_match_score), orient="index"
    )[0]
    processed_data = IdentityMatchDataframe()
    processed_data.import_and_process_data(
        Path(
            *path_base, f"{get_filename_base(test_identity_match_score)}_raw_data.json"
        )
    )
    identity_match_scores = processed_data.identity_match_scores

    assert identity_match_scores.equals(expected_results)
