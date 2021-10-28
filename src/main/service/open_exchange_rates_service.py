from typing import Dict

import requests  # type: ignore
from redis import Redis  # type: ignore


class OpenExchangeRatesInterface:
    def refresh_latest(self, app_id: str) -> None:
        """Fetches the latest currency exchange rates"""
        raise NotImplementedError

    def get_latest(self) -> Dict[str, float]:
        """Returns the latest currency exchange rates"""
        raise NotImplementedError


class OpenExchangeRatesImpl(OpenExchangeRatesInterface):
    def __init__(self, cache: Redis):
        self.cache = cache

    redis_key_prefix = "open_exchange_rates_USD_to_"

    def refresh_latest(self, app_id: str) -> None:
        response: Dict[str, float] = requests.get(
            "https://openexchangerates.org/api/latest.json", params={"app_id": app_id}
        ).json()["rates"]
        for currency, exchange_rate in response.items():
            self.cache.mset({f"{self.redis_key_prefix}{currency}": exchange_rate})

    def get_latest(self) -> Dict[str, float]:
        """Fetches the latest currency exchange rates"""
        res: Dict[str, float] = {}
        cache_keys = self.cache.keys(pattern=f"{self.redis_key_prefix}*")
        for cache_key in cache_keys:
            cache_key_str = cache_key.decode("utf-8")
            currency = cache_key_str[len(self.redis_key_prefix) :]
            res[currency] = float(self.cache.get(cache_key))
        return res
