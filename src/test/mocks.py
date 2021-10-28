import re
from typing import Dict, List, Optional

from redis import Redis  # type: ignore

from src.main.exceptions import CurrencyNotFoundException
from src.main.service.converter_service import ConverterInterface
from src.main.service.open_exchange_rates_service import OpenExchangeRatesInterface


class ConverterMock(ConverterInterface):
    def __init__(self):
        self.calls = []

    def convert(self, currency: str, value: float, target_currency: str) -> float:
        self.calls += ("convert", currency, value, target_currency)
        if (
            currency.upper()
            not in [
                "USD",
                "EUR",
                "GBP",
            ]
            or target_currency.upper() not in ["USD", "EUR", "GBP"]
        ):
            raise CurrencyNotFoundException()
        return value


class OpenExchangeRatesMock(OpenExchangeRatesInterface):
    def get_latest(self) -> Dict[str, float]:
        return {"USD": 1, "GBP": 0.73, "EUR": 0.86}

    def refresh_latest(self, app_id: str) -> None:
        pass


class RedisMock(Redis):
    cache: Dict[bytes, float] = {
        b"open_exchange_rates_USD_to_USD": 1,
        b"open_exchange_rates_USD_to_GBP": 0.73,
        b"open_exchange_rates_USD_to_EUR": 0.86,
    }

    def __init__(self):
        super().__init__()
        self.calls = []

    def get(self, name) -> Optional[float]:
        self.calls.append(("get", name))
        if name in self.cache:
            return self.cache[name]
        else:
            return None

    def mset(self, mapping) -> None:
        self.calls.append(("mset", mapping))
        pass

    def keys(self, pattern="*") -> List[bytes]:
        self.calls.append(("keys", pattern))
        res: List[bytes] = []
        regex = re.compile(pattern)
        for key in self.cache:
            if regex.match(key.decode("UTF-8")) != None:
                res.append(key)
        return res
