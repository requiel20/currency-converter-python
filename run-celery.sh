#!/bin/bash

python -m celery -A src.main.celery_app.celery worker -B --loglevel=WARN
