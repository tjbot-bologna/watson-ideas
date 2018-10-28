#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep

import json
from watson_developer_cloud import AssistantV1

context = None

assistant = AssistantV1(
    username="e7c46313-e382-40f4-a77c-67f9e5cc15ea",
    password="1XaNGI6RwkOM",
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    url="https://gateway.watsonplatform.net/assistant/api",
    version="2018-07-10")


update_id = None


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            update.message.reply_text(update.message.text)


def converse(bot):
    global update_id, context
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message

            response = assistant.message(
                workspace_id="4208099e-d443-405d-bba7-11c3d9f2c620",
                input={
                    "text": update.message.text
                },
                context=context).get_result()

            context = response["context"]

            print(json.dumps(response, indent=2))
            for t in response["output"]["text"]:
                # print(t + "\n")
                update.message.reply_text(t)
            if (len(response["output"]["generic"]) > 1):
                bot.send_photo(chat_id=update.message.chat_id, photo=response["output"]["generic"][1]["source"])



def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot('286358309:AAG-NF68tQam6aN1PLCt0g1gm4kB5XS-Sic')

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            # echo(bot)
            converse(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


if __name__ == '__main__':
    print("kiwibot running at https://telegram.me/sprintingkiwibot")
    main()
