# Discord Bot Project

## Contributors

Fernando Peralta Castro - peraltaf2
Brandon Yang - clouduki
Trevor Gray - trevor-gray17

## Purpose

The goal of this project is to demonstrate how to set up a simple Discord bot with varying components:

1. A Python program using [`requests`](https://docs.python-requests.org/en/master/) to collect data.
2. The [redis](https://redis.io/) database to store data

## Features

The data used in this example pulls inspirational quotes from the ZenQuotes API [ZenQuotes Api](https://www.zenquotes.io).

- **$inspire:** Users can receive randomized inspirational quotes from the Zen Quotes Website
- **$new:** Users can add encouraging messages to the redis database of positive affirmations.
- **$del:** Users can delete old encoruaging messages from the database
- **$list:** Users can receivie a list of the positive messages that are currently being saved in the database
- **$responding:** Users can toggle whether the bot responds or not

## How to Use

1. **Installation:**

Read this article or watch this video on how to create a discord bot using your discord account

Read up to the 'How to Set Up Discord Events for Your Bot' section
[Creating a Discord Bot Article](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/)

Watch this video up to 6:05 to see how to create a bot user
[Video on how to create a Discord bot](https://www.youtube.com/watch?v=SPTfmiYiuok)


* Create a environment for the code and install the required libraries:
* 
  ```
   cd into the bot_behavior folder
   pip3 install -r requirements.txt
  
  ```

* Create a file .env that contains the hostname and port number for Redis. We will run Redis on our laptop (localhost) using the standard Redis port (6379). Replace <API_KEY> with your Discord Bot Token:

## You will not be able to run the code if you do not create this .env file

 ```
REDIS_HOST=localhost
REDIS_PORT=6379
TOKEN=<API_KEY>

 ```
2. **Database Setup:**


## Redis Setup

* (If needed) Install [Homebrew](https://brew.sh/)

  ```
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
  
* Install Redis on your system

  ```
  brew install redis
  ```

3. **Launch the System**:

We will launch the system in two terminal windows:

* Terminal #1 (In the project root) Launch Redis:

  ```
  redis-server
  ```
  
* Terminal #2 (In the `bot_behavior` folder) Launch the bot:

  ```
  python bot_behavior.py
  ```

4. **Stop the System**

In each terminal window, press ctrl-c to stop the program.

