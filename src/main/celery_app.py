from celery import Celery
from redis import Redis  # type: ignore

from src.main.resources import config
from src.main.service.open_exchange_rates_service import OpenExchangeRatesImpl

celery = Celery(__name__)
celery.conf.result_backend = config.CELERY_RESULT_BACKEND
celery.conf.broker_url = config.CELERY_BROKER_URL
open_exchange_rates_app_id = config.OPEN_EXCHANGE_RATES_APP_ID

cache = Redis(host="redis", port=6379, db=0)

open_exchange_rates = OpenExchangeRatesImpl(cache)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10.0,
        fetch_exchange_rates.s(),
        name="Fetch exchange rates every 10 seconds",
    )


@celery.task()
def fetch_exchange_rates() -> None:
    open_exchange_rates.refresh_latest(open_exchange_rates_app_id)
    return None
