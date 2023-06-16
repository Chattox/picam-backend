#!/bin/bash

source .venv/bin/activate
flask --app api/app run --host 0.0.0.0
