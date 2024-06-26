# bot.py

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

import os
import discord
import openai
import redis
import sys

from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

# Get Redis connection details from environment variables
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

# Set up the OpenAI API client
openai.api_key = OPENAI_KEY

# Set up the Redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # Only respond to messages from other users, not from the bot itself
    if message.author == client.user:
        return

    # Store user input in Redis
    current_date = datetime.now().strftime('%Y-%m-%d')
    user_key = f"{str(message.author.id)}:{current_date}"
    if r.exists(user_key) and r.type(user_key) != b'list':
        r.delete(user_key)
    r.rpush(user_key, message.content)

    # Check if the bot is mentioned in the message
    if client.user in message.mentions:
        # Use the OpenAI API to generate a response to the message
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{message.content}"},
            ]
        )

        # Send the response as a message
        await message.channel.send(response['choices'][0]['message']['content'])

try:
    # Start the bot
    client.run(TOKEN)
except KeyboardInterrupt:
    print("Bot stopped by user")
    sys.exit(0)  # exit without error
except RuntimeError as e:
    if str(e) == "Session is closed":
        print("Caught 'Session is closed' error. The bot will now exit.")
    else:
        raise  # re-raise the exception if it's not the one we're trying to catch
except Exception as e:
    print(f"An unexpected error occurred: {e}")
