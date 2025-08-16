#!/bin/bash
pytest tests/ -n 4 --html=test-report.html --self-contained-html
python notify.py
