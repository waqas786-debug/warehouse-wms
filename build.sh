#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Seed the database and 42 tables automatically on deploy
python seed.py
