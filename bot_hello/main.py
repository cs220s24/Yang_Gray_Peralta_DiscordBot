import discord

TOKEN = '.'

client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() in ['hello', 'hi']:
        await message.channel.send(f'Hello {message.author.display_name}!')
    elif message.content.upper() in ['Hello', 'Hi']:
        await message.channel.send(f'Hello {message.author.display_name}!')

client.run(TOKEN)