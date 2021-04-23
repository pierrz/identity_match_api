from src.identity_match_score import IdentityMatchDataframe
from pathlib import Path
import json
import pandas as pd


def test_identity_match_score():
    path_base = [Path(__file__).parent, "fixtures"]
    filename_base = f"{test_identity_match_score.__name__}"

    raw_data_path = Path(*path_base, f"{filename_base}_raw_data.json")
    expected_results_path = Path(*path_base, f"{filename_base}_expected_results.json")

    processed_data = IdentityMatchDataframe()
    processed_data.import_and_process_data(raw_data_path)
    identity_match_scores = processed_data.identity_match_scores

    expected_results_data = json.load(open(expected_results_path, "r"))
    expected_results = pd.DataFrame.from_dict(expected_results_data, orient="index")[0]

    assert identity_match_scores.equals(expected_results)
