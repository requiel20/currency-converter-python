from typing import Generator

import pytest
import responses

from src.main.app import create_flask_app
from src.main.service.open_exchange_rates_service import OpenExchangeRatesImpl
from src.test.mocks import ConverterMock, OpenExchangeRatesMock, RedisMock

cache_mock = RedisMock()


@pytest.fixture(autouse=True)
def client() -> Generator:
    app = create_flask_app(
        ConverterMock(), OpenExchangeRatesMock(), "src.test.resources.test_config"
    )
    cache_mock.calls = []
    with app.app_context():
        yield


@responses.activate
def test_get():
    """Should get the currencies"""
    under_test = OpenExchangeRatesImpl(cache_mock)

    assert under_test.get_latest() == {"USD": 1, "GBP": 0.73, "EUR": 0.86}

    assert cache_mock.calls == [
        ("keys", f"{under_test.redis_key_prefix}*"),
        ("get", f"{under_test.redis_key_prefix}USD".encode("UTF-8")),
        ("get", f"{under_test.redis_key_prefix}GBP".encode("UTF-8")),
        ("get", f"{under_test.redis_key_prefix}EUR".encode("UTF-8")),
    ]


@responses.activate
def test_call_dependency():
    """Should call the dependency"""
    responses.add(
        responses.GET,
        "https://openexchangerates.org/api/latest.json?app_id=123",
        json={"rates": {"USD": 1, "EUR": 2}},
        status=404,
    )

    under_test = OpenExchangeRatesImpl(cache_mock)

    under_test.refresh_latest("123")

    assert cache_mock.calls == [
        ("mset", {f"{under_test.redis_key_prefix}USD": 1}),
        ("mset", {f"{under_test.redis_key_prefix}EUR": 2}),
    ]


@responses.activate
def test_call_dependency_http_error():
    """Should surface dependency http errors"""
    responses.add(
        responses.GET,
        "https://openexchangerates.org/api/latest.json?app_id=123",
        body=Exception("Internal server error"),
        status=500,
    )

    under_test = OpenExchangeRatesImpl(cache_mock)

    with pytest.raises(Exception):
        under_test.refresh_latest("123")

    assert cache_mock.calls == []


@responses.activate
def test_call_dependency_json_error():
    """Should surface dependency deserialization errors"""
    responses.add(
        responses.GET,
        "https://openexchangerates.org/api/latest.json?app_id=123",
        json={},
        status=404,
    )

    under_test = OpenExchangeRatesImpl(cache_mock)

    with pytest.raises(Exception):
        under_test.refresh_latest("123")

    assert cache_mock.calls == []
