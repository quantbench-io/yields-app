#!/bin/sh
source .venv/bin/activate
python -m uvicorn main:app --port 3000 --host 0.0.0.0