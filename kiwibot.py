# -*- coding: utf-8 -*-

from time import sleep

# Import Telegram libraries
import logging
import telegram
from telegram.error import NetworkError, Unauthorized

# Import Watson libraries
import json
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import VisualRecognitionV3


# Define global variables
update_id = None
context = None

# Instance Watson resources objects
assistant = AssistantV1(
    iam_apikey="esXISM3aWlgM5HORbmxtKnQnG6_I-fTM3wFa2rLHYBL9",
    url="https://gateway.watsonplatform.net/assistant/api",
    version="2018-07-10")

visual_recognition = VisualRecognitionV3(
    "2018-03-19",
    iam_apikey="UDDvweJSDR32NAZIfyxZ-dlvjIZ8dfRv75Z93xyjWGEX")


# Simple echo function for tests
def echo(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            update.message.reply_text(update.message.text)


# Main function to handle incoming messages
def converse(bot):
    global update_id, context
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message:

            # Check if the user sent a picture
            if len(update.message.photo) > 0:
                picture = bot.get_file(update.message.photo[-1].file_id)
                pic_file = picture.download()

                # Send image to your Watson visual recognition resource
                with open(pic_file, 'rb') as image:
                    classes = visual_recognition.classify(
                        image,
                        threshold='0.6').get_result()
                    print(json.dumps(classes, indent=2))

                    # Send Watson answer in Telegram chat
                    update.message.reply_text(json.dumps(classes, indent=2))
        
            # Check if the user sent text
            if update.message.text is not None:
                # Send text to watson assistant workspace (or skill) and get a response
                response = assistant.message(
                    workspace_id="85e09b72-06f2-434d-9f2e-c2897ec4a611",
                    input={
                        "text": update.message.text
                    },
                    context=context).get_result()
                print(json.dumps(response, indent=2))

                # Update conversation context
                context = response["context"]

                # Make the bot reply in the Telegram chat using the Watson response:
                # This is for text answers, which might be multiple
                for t in response["output"]["text"]:
                    update.message.reply_text(t)

                # This is for pictures link the response might contain
                if (len(response["output"]["generic"]) > 1):
                    try:
                        pic = response["output"]["generic"][1]["source"]
                        bot.send_photo(chat_id=update.message.chat_id, photo=pic)
                    except Exception(e):
                        print(e)


# Main bot behaviour
def main():
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


# Run the bot
print("Bot running at https://telegram.me/sprintingkiwibot")
main()
