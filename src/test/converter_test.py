import math
from typing import Generator

import pytest
import responses

from src.main.app import create_flask_app
from src.main.exceptions import CurrencyNotFoundException
from src.main.service import open_exchange_rates_service
from src.main.service.converter_service import ConverterImpl
from src.test.mocks import ConverterMock, OpenExchangeRatesMock


@pytest.fixture(autouse=True)
def client() -> Generator:
    app = create_flask_app(
        ConverterMock(), OpenExchangeRatesMock(), "src.test.resources.test_config"
    )
    with app.app_context():
        yield


@responses.activate
def test_converts():
    """Should convert currencies"""
    open_exchange_rates_service.latest = {"USD": 1, "EUR": 0.86, "GBP": 0.73}
    under_test = ConverterImpl(OpenExchangeRatesMock())
    actual = under_test.convert("EUR", 1, "GBP")

    assert math.isclose(actual, 0.84, abs_tol=0.01)


@responses.activate
def test_call_dependency_http_error():
    """Should currency not found error"""
    open_exchange_rates_service.latest = {"USD": 1, "EUR": 0.86, "GBP": 0.73}
    under_test = ConverterImpl(OpenExchangeRatesMock())

    with pytest.raises(CurrencyNotFoundException):
        under_test.convert("ZZZ", 1, "GBP")

    with pytest.raises(CurrencyNotFoundException):
        under_test.convert("GBP", 1, "ZZZ")
