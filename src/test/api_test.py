import pytest
from flask.testing import FlaskClient

from src.main.app import create_flask_app
from src.test.mocks import ConverterMock, OpenExchangeRatesMock

converterMock = ConverterMock()


@pytest.fixture(autouse=True)
def client() -> FlaskClient:
    app = create_flask_app(
        converterMock, OpenExchangeRatesMock(), "src.test.resources.test_config"
    )
    with app.app_context():
        yield app.test_client()
    converterMock.calls = []


def test_call_converter(client: FlaskClient):
    """Should call the converter"""

    rv = client.post(
        "/v1/convert", json={"currency": "usd", "value": 10, "target_currency": "GBP"}
    )
    json_data = rv.get_json()
    assert rv.status_code == 200
    assert {
        "original_value": 10,
        "original_currency": "USD",
        "converted_value": 10,
        "converted_currency": "GBP",
    } == json_data
    assert converterMock.calls == ["convert", "usd", 10, "GBP"]


def test_400_bad_body(client: FlaskClient):
    """Should return 400 for bad body"""

    rv = client.post("/v1/convert", json="BAD")
    assert rv.status_code == 400


def test_400_no_body(client: FlaskClient):
    """Should return 400 for no body"""

    rv = client.post("/v1/convert")
    assert rv.status_code == 400


def test_400_missing_field(client: FlaskClient):
    """Should return 400 for missing field"""

    rv = client.post("/v1/convert", json={"currency": "usd", "value": 10})
    assert rv.status_code == 400


def test_400_bad_currency(client: FlaskClient):
    """Should return 400 for missing field"""

    rv = client.post(
        "/v1/convert", json={"currency": "usd", "value": 10, "target_currency": "ZZZ"}
    )
    assert rv.status_code == 400
