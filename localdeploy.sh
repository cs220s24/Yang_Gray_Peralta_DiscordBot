#!/bin/bash

# Check for .env file
if [ ! -f .env ]; then
    echo "Create .env before deploying"
    exit
fi

# Start Redis as a background process
redis-server --daemonize yes

sleep 5  # Wait for 5 seconds for Redis to start

# Create a trap to shut down Redis when the script exits
trap "redis-cli shutdown" EXIT

# Create Python virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt

# Start the bot
python3 bot.py