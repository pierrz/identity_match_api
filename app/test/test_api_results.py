from fastapi.testclient import TestClient
from src.main import app
from utils.test_utils import get_expected_results_dict

client = TestClient(app)


def test_api_results():

    base_url = "http://127.0.0.1:8000/service_api"
    base_url_default = f"{base_url}_default"
    apikey_part = "?apikey=apikey123"
    test_urls = [
        f"{base_url_default}{apikey_part}",
        f"{base_url}{apikey_part}&filepath=../data/examples.json",
    ]

    expected_results = [get_expected_results_dict(test_api_results)] * len(test_urls)
    for p in range(len(test_urls)):
        url = test_urls[p]
        expected_response = expected_results[p]
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == expected_response
