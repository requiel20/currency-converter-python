#!/bin/bash

python -m gunicorn -w 4 -b 0.0.0.0:5000 "src.main.app:create_app()"
