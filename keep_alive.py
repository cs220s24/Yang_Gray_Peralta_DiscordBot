from flask import Flask
from threading import Thread
import schedule
import time

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
  app.run(host='0.0.0.0',port=8080)

def periodic_task():
    print("Performing a periodic task...")

schedule.every(30).minutes.do(periodic_task)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # make the thread a daemon thread
    t.start()

    while True:
        schedule.run_pending()
        time.sleep(1)