from __future__ import unicode_literals

import telegram
import praw
import html
import sys
import os
import json
import pickle

from time import sleep
from datetime import datetime

credentials = {}

credentials["token"] = os.environ.get('TOKEN')
credentials["subreddit"] = os.environ.get('SUB')
credentials["channel"] = os.environ.get('CHANNEL')

if credentials["token"] == "": 
    raise RuntimeError('Bot token not found 🙁! Put bot token🔐 in credentials.json!')
if credentials["subreddit"] == "":
    raise RuntimeError('Subreddit name not found 🙁! Enter the subreddit name📃 in credentials.json!')
if credentials["channel"] == "":
    raise RuntimeError('Telegram Channel name not found 🙁! Enter the channel name📰 in credentials.json!')


token = credentials["token"]
channel = credentials["channel"]
sub = credentials["subreddit"]
start_time = datetime.utcnow().timestamp()


def get_prev_submissions():
    try:
        with open('prev_submissions.pickle', 'rb') as f:
            return pickle.load(f)
    except:
        return []

def write_submissions(sub_ids):
    try:
        with open('prev_submissions.pickle', 'wb') as f:
            pickle.dump(sub_ids, f)
    except:
        print('exception: Error writing sub ID!')

r = praw.Reddit(user_agent="Dank Doggo by Harsha :D",
                client_id=os.environ.get('CLIENT_ID'),
                client_secret=os.environ.get('CLIENT_SECRET'),
                username=os.environ.get('RUSERNAME'),
                password=os.environ.get('RPASS'))
r.read_only = True
subreddit = r.subreddit(sub)

bot = telegram.Bot(token=token)

while True:
    try:
        prev_submissions = get_prev_submissions()
        for submission in subreddit.hot():
            try:
                if submission.id in prev_submissions:
                    continue

                link = "https://redd.it/{id}".format(id=submission.id)
                if submission.created_utc < start_time:
                    print("Skipping {} --- latest submission not found!".format(submission.id))
                    continue
                
                image = html.escape(submission.url or '')
                title = html.escape(submission.title or '')
                user = html.escape(submission.author.name or '')

                template = "{title}\n{link}\nby {user}"
                message = template.format(title=title, link=link, user=user)

                print("Posting {}".format(link))
                bot.sendPhoto(chat_id=channel, photo=submission.url, caption=message)
                prev_submissions.add(submission.id)
                sleep(60)
            except Exception as e:
                print("Exception: Error parsing {}".format(link))
                print(e)
        
        write_submissions(prev_submissions)
    except Exception as e:
        print("Exception: Error fetching new submissions, restarting in 10 secs")
        sleep(10)