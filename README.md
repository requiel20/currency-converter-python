# currency-converter-python

This service provides an API to convert between currencies.

The API is built using [flask](https://flask.palletsprojects.com/)
running on top of [gunicorn](https://gunicorn.org/) and the API client
is [requests](https://docs.python-requests.org/).

Currencies exchange rates are pulled from [open-exchange-rates](https://openexchangerates.org/)
and refreshed every 10s via a [celery](https://docs.celeryproject.org/) task
using [redis](https://redis.io/) as a backend. Redis is also used to
store the currencies themselves.

## Usage

### Starting the app

You can start the app with `docker compose up`. This will start three containers:
1. The `web` container starts the flask app to serve request
2. The `celery` container starts the celery app to update the conversion rates
3. The `redis` container starts redis as a backend for celery

A `Dockerfile` is also present to build containers 1 and 2 (they only differ in
entry point) and this should be able to suit any preference
for a production-ready deployment, be it kubernetes or a managed cloud service.

Once the app is started, you can see its swagger docs at
[localhost:5000/doc](localhost:5004/doc) or convert between currencies
with curl:

```shell
$ curl -XPOST http://127.0.0.1:5004/v1/convert \
  -H 'Content-Type: application/json' \
  -d '{"currency": "usd", "value": 10, "target_currency": "GBP"}'
```

### Local development

To develop locally, you will have to install three sets of dependencies

1. requirements.txt - to run the app
2. requirements-dev.txt - to run pre-commit hooks
3. requirements-test.txt - to run tests

Dependencies have been pinned to ensure a stable and replicable environment.

To run the tests, run `python -m pytest`

## App structure

The structure has been chosen to favour testability wherever possible.

That is why flask app creation is done in functions instead than in the top-level
of a file, and why the converter and the open exchange rates code is in a class
implementing a "soft interface" that can be overridden with mocks for tests.

Similarly, config is specified differently for testing and production:
production uses environment variables why testing uses raw Python values.

## Observability

Observability has been left as a future concern. Given more time, one should implement
logging and monitoring using e.g. loki, prometheus and grafana.

Metrics to monitor should be:

* Incoming `POST /v1/convert`
  * Requests per second
  * Average response time
    * Alert if > 100ms 
  * 99th percentile response time
    * Alert if > 500ms

* Celery tasks
    * Tasks per second
    * Average completion time
        * Alert if > 100ms
    * 99th percentile completion time
        * Alert if > 500ms

* Outgoing requests to open exchange rates
    * Requests per second
    * Average response time
        * Alert if > 100ms
    * 99th percentile response time
        * Alert if > 500ms

Note that alert thresholds depend on what level of performance is expected and
could be revisited.

## Improvement opportunities

Aside of what has been mentioned already, one looking at improve this app
should probably look at:

1. Store the timestamp that the conversion rates were last updated in redis and 
  implement a mechanism to refresh them if they're not fresh enough. This should also
  trigger an alert.
2. Hardening the app with some end-to-end tests that spin up the three containers
  and hit them with some requests. Redis should also be hit to check that the
  keys are being refreshed correctly by the celery task.
3. Running multiple copies of the web server is advised, to improve reliability.
  redis and celery can be kept in one copy and just restarted on crash.
