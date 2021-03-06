# -*- coding: utf-8 -*-

from time import sleep
import os
import json

# Import Telegram libraries
import logging
import telegram
from telegram.error import NetworkError, Unauthorized

# Import Watson libraries
from watson_developer_cloud import VisualRecognitionV3

# Define global variables
update_id = None
active_class = ""
behaviour = "recognize"

# Instance Watson resources objects
visual_recognition = VisualRecognitionV3(
    "2018-03-19",
    iam_apikey="UDDvweJSDR32NAZIfyxZ-dlvjIZ8dfRv75Z93xyjWGEX")


classifiers = visual_recognition.list_classifiers(verbose=True).get_result()
print(json.dumps(classifiers, indent=2))           


# Visual recognition service function
def vrec(pic_file):
    classes = ""
    try:
        # Send image to your Watson visual recognition resource
        with open(pic_file, 'rb') as image:
            classes = visual_recognition.classify(
                image,
                threshold='0.6').get_result()
            print(json.dumps(classes, indent=2))
    except Exception as e:
        print(e)
    return classes


# Function to handle incoming messages
def bot_answer(bot):
    global update_id, behaviour, active_class
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message:

            # Check if the user sent text
            if update.message.text is not None:
                if update.message.text == "/recognize":
                    behaviour = "recognize"
                    update.message.reply_text("Recognize mode")
                elif update.message.text == "/learn":
                    behaviour = "learn"
                    update.message.reply_text("Learn mode, active class: " + active_class)
                elif behaviour == "learn":
                    active_class = update.message.text

            # Check if the user sent a picture
            if len(update.message.photo) > 0:
                picture = bot.get_file(update.message.photo[-1].file_id)
                pic_file = picture.download()

                if behaviour == "recognize":
                    update.message.reply_text((json.dumps(vrec(pic_file), indent=2)))
                else:
                    with open(pic_file, 'rb') as new_pic:
                        parameters = {}
                        parameters["classifier_id"] = 'dogs_1477088859'
                        parameters[active_class+"_examples"] = new_pic
                        updated_model = visual_recognition.update_classifier(parameters).get_result()
                        update.message.reply_text(json.dumps(updated_model, indent=2))

                os.remove(pic_file)


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
            bot_answer(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


# Run the bot
print("Bot running at https://telegram.me/sprintingkiwibot")
main()