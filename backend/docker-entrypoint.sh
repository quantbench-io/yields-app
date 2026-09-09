#!/bin/sh
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0