#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Pulling latest changes..."
git pull

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt -q

echo "Starting bot..."
exec .venv/bin/python bot.py
