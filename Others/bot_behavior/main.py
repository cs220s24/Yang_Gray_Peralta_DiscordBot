import discord
import os
import dotenv
import requests
import json
import random
import redis

from discord.ext import commands

dotenv.load_dotenv()

host = os.getenv('REDIS_HOST')
port = os.getenv('REDIS_PORT')

r = redis.Redis(host=host, port=port)

intents = discord.Intents.default()
intents.message_content = True

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there.",
    "You are a great person / bot!"
]

if "responding" not in r.keys():
    r.set("responding", "True")

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

def get_encouragements():
    if "encouragements" in r.keys():
        return json.loads(r.get("encouragements"))
    else:
        return starter_encouragements

def update_encouragements(encouraging_message):
    encouragements = get_encouragements()
    encouragements.append(encouraging_message)
    r.set("encouragements", json.dumps(encouragements))

def delete_encouragement(index):
    encouragements = get_encouragements()
    if len(encouragements) > index:
        del encouragements[index]
        r.set("encouragements", json.dumps(encouragements))

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()

    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if r.get("responding"):
        options = get_encouragements()
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")

    if msg.startswith("$del"):
        index = int(msg.split("$del ", 1)[1])
        delete_encouragement(index)
        await message.channel.send("Encouraging message deleted.")

    if msg.startswith("$list"):
        encouragements = get_encouragements()
        if "encouragements" in r.keys():
            encouragements = r.get("encouragements")
        await message.channel.send(encouragements)

    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]

        if value.lower() == "true":
            r.set("responding", "True")
            await message.channel.send("Responding is on.")
        else:
            r.set("responding", "False")
            await message.channel.send("Responding is off.")

client.run(os.getenv('TOKEN'))
