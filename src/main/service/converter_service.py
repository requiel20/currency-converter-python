from src.main.exceptions import CurrencyNotFoundException
from src.main.service.open_exchange_rates_service import OpenExchangeRatesInterface


class ConverterInterface:
    def convert(self, currency: str, value: float, target_currency: str) -> float:
        """Convert between currencies"""
        raise NotImplementedError


class ConverterImpl(ConverterInterface):
    def __init__(self, rates_service: OpenExchangeRatesInterface):
        self.rates_service = rates_service

    def convert(self, currency: str, value: float, target_currency: str) -> float:
        rates = self.rates_service.get_latest()
        try:
            usd_to_currency = rates[currency.upper()]
        except KeyError:
            raise CurrencyNotFoundException(f"Currency not found: {currency}")

        try:
            usd_to_target_currency = rates[target_currency.upper()]
        except KeyError:
            raise CurrencyNotFoundException(f"Currency not found: {target_currency}")

        print(
            f"found usd_to_currency rate {usd_to_currency} and usd_to_target_currency rate {usd_to_target_currency}, converting ..."
        )

        usd = value * (1 / usd_to_currency)
        return usd * usd_to_target_currency
