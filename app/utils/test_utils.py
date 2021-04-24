import json
from pathlib import Path


def get_expected_results_dict(test_file_object):
    filename_base = get_filename_base(test_file_object)
    expected_results_path = Path(
        *get_test_fixtures_path(), f"{filename_base}_expected_results.json"
    )
    return json.load(open(expected_results_path, "r"))


def get_test_fixtures_path():
    return [Path(__file__).parent.parent, "test", "fixtures"]


def get_filename_base(test_file_object):
    return f"{test_file_object.__name__}"
