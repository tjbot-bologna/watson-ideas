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
from watson_developer_cloud import SpeechToTextV1
from os.path import join, dirname


# Define global variables
update_id = None
info = {}
info["context"] = None
info["stt"] = False
info["lang"] = "it"

# Instance Watson resources objects
assistant = AssistantV1(
    iam_apikey="esXISM3aWlgM5HORbmxtKnQnG6_I-fTM3wFa2rLHYBL9",
    url="https://gateway.watsonplatform.net/assistant/api",
    version="2018-07-10")

visual_recognition = VisualRecognitionV3(
    "2018-03-19",
    iam_apikey="UDDvweJSDR32NAZIfyxZ-dlvjIZ8dfRv75Z93xyjWGEX")


# Watson assistant service function
def converse(text):
    response = assistant.message(
        workspace_id="85e09b72-06f2-434d-9f2e-c2897ec4a611",
        input={
            "text": text
        },
        context=info["context"]).get_result()
    print(json.dumps(response, indent=2))
    # Update conversation context
    info["context"] = response["context"]
    return response


# Visual recognition service function
def vrec(pic_file):
    # Send image to your Watson visual recognition resource
    with open(pic_file, 'rb') as image:
        classes = visual_recognition.classify(
            image,
            threshold='0.6').get_result()
        print(json.dumps(classes, indent=2))
        return classes


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
def kiwi_answer(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message:

            # Check if the user sent a voice note
            if update.message.voice is not None:
                print("Received a voice note! Speech to text in progress...")
                voice_note = bot.get_file(update.message.voice.file_id)
                voice_file = voice_note.download()

            # Check if the user sent a picture
            if len(update.message.photo) > 0:
                print("Received a Picture! Visual recognition in progress...")
                picture = bot.get_file(update.message.photo[-1].file_id)
                pic_file = picture.download()                    
                # Send Watson answer in Telegram chat
                update.message.reply_text((json.dumps(vrec(pic_file), indent=2)))
        
            # Check if the user sent text
            if update.message.text is not None:
                # Send text to watson assistant workspace (or skill) and get a response
                response = converse(update.message.text)

                # Make the bot reply in the Telegram chat using the Watson response:
                # This is for text answers, which might be multiple
                for t in response["output"]["text"]:

                    # Parse TJBot conversation command tags
                    tag = None
                    parsed_text = t.split("TJBOT_")
                    elements = len(parsed_text)
                    # Check if there are more than one tag comment per answer
                    if elements > 2:
                        update.message.reply_text("WARNING: Watson conversation can have only one tag command per answer")
                        return
                    elif elements > 1 and  elements < 3:
                        tag = parsed_text[1]
                        # Execute tag commands:
                        if tag == "STT_START":
                            info["stt"] = True
                        elif tag == "STT_STOP":
                            info["stt"] = False
                        t = parsed_text[0]

                    # Post text in Telegram chat
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
            kiwi_answer(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


# Run the bot
print("Bot running at https://telegram.me/sprintingkiwibot")
main()
