# Discord Chat GPT Bot

# Setup

The following sections describe how to setup the system so it will
run *locally* (i.e. on your laptop).  For deployment on an EC2 
instance, see the sections in the [AWS section](#AWS) section.

## Running Bot Locally

* Create a virtual environment for the collector and install the required libraries:

# Start Redis as a background process
redis-server --daemonize yes

# Create a trap to shut down Redis when the script exits
trap "redis-cli shutdown" EXIT

# Create Python virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the bot
python bot.py

* Create a file `.env` that contains the hostname and port number for Redis.  We will run Redis on our laptop (`localhost`) using the standard Redis port (6379).  Replace `<API_KEY>` with your WeatherAPI key:

  ```
    DISCORD_TOKEN = '<Discord_Token>'
    OPENAI_KEY = "<OPENAI_KEY?"
    REDIS_HOST=localhost
    REDIS_PORT=6379
  ```

  Deploy SH script for local running

  #!/bin/bash

# Check for .env file
if [ ! -f .env ]; then
    echo "Create .env before deploying"
    exit
fi

# Start Redis as a background process
redis-server --daemonize yes

# Create a trap to shut down Redis when the script exits
trap "redis-cli shutdown" EXIT

# Create Python virtual environment and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the bot
python bot.py
