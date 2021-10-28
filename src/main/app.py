from flask import Flask
from flask_restx import Api
from redis import Redis  # type: ignore

from src.main.api.meta import create_namespace as meta_namespace
from src.main.api.v1 import create_namespace as v1_namespace
from src.main.service.converter_service import ConverterImpl, ConverterInterface
from src.main.service.open_exchange_rates_service import (
    OpenExchangeRatesImpl,
    OpenExchangeRatesInterface,
)


def create_app():
    cache = Redis(host="redis", port=6379, db=0)
    open_exchange_rates = OpenExchangeRatesImpl(cache)
    conv = ConverterImpl(open_exchange_rates)
    flask_app = create_flask_app(conv, open_exchange_rates, "src.main.resources.config")
    return flask_app


def create_flask_app(
    converter: ConverterInterface,
    open_exchange_rates: OpenExchangeRatesInterface,
    config_path: str,
) -> Flask:
    application = Flask(__name__)

    create_api = Api(application, title="currency-converter-python")

    create_api.add_namespace(meta_namespace(), path="/")
    create_api.add_namespace(v1_namespace(converter), path="/v1")

    application.config.from_object(config_path)

    with application.app_context():
        open_exchange_rates.refresh_latest(
            application.config["OPEN_EXCHANGE_RATES_APP_ID"]
        )
        return application


if __name__ == "__main__":
    app = create_app()
    app.run()
