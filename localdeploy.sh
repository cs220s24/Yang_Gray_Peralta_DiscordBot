#!/bin/bash

# Copyright 2024 Fernando Peralta Castro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
