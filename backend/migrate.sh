#!/bin/bash
# Migration runner script for Recipe Saver Enhancements

cd "$(dirname "$0")"
python3 run_migrations.py
