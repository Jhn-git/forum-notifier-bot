#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Pulling latest changes..."
git pull

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Starting bot..."
python bot.py
