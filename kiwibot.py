# -*- coding: utf-8 -*-

from time import sleep
import os
import json

# Import Telegram libraries
import logging
import telegram
from telegram.error import NetworkError, Unauthorized

# Import Watson libraries
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import VisualRecognitionV3
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import LanguageTranslatorV3
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions

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

speech_to_text = SpeechToTextV1(
    iam_apikey="V8tmwaVMQteiGjuE6N2colYvu__DxTAso_tms2yqxw9o",
    url="https://gateway-lon.watsonplatform.net/speech-to-text/api")

language_translator = LanguageTranslatorV3(
    version="2018-05-01",
    iam_apikey="aWORISQg1cm1P6bkcm_YraJEIo9r-mBl1hnVrSiamcN-",
    url="https://gateway.watsonplatform.net/language-translator/api")

naturalLanguageUnderstanding = NaturalLanguageUnderstandingV1(
    version="2018-11-16",
    iam_apikey="M2LbjCau1hh5A-yrj8m0BVbUm-ptmBdaU0oX6G74OfZA",
    url="https://gateway-lon.watsonplatform.net/natural-language-understanding/api")


# Watson assistant service function
def converse(text):
    response = ""
    try:
        response = assistant.message(
            workspace_id="85e09b72-06f2-434d-9f2e-c2897ec4a611",
            input={
                "text": text
            },
            context=info["context"]).get_result()
        print(json.dumps(response, indent=2))
        # Update conversation context
        info["context"] = response["context"]
    except Exception as e:
        print(e)
    return response


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

# Speech to text service function
def stt(audio):
    transcript = ""
    try:
        speech_recognition_results = ""
        with open(audio, 'rb') as audio_file:
            speech_recognition_results = speech_to_text.recognize(
                audio=audio_file,
                content_type="audio/ogg"
                ).get_result()            
        print(json.dumps(speech_recognition_results, indent=2))
        transcript = speech_recognition_results["results"][0]["alternatives"][0]["transcript"]  
    except Exception as e:
        print(e)
    return transcript


def translate(text, target, source="default"):
    translation = ""
    try:
        if source == "default":
            source = identify_language(text)
        if source != "en":
            text = translate(text, "en", source)

        response = language_translator.translate(
        text=text,
        source=source,
        target=target).get_result()
        print(json.dumps(response, indent=2, ensure_ascii=False))        
        translation = response[0]["translation"]
    except Exception as e:
        print(e)
    return translation


def identify_language(text):
    language = "en"
    try:
        response = language_translator.identify(text).get_result()
        print(json.dumps(response, indent=2))
        confidence = 0.0
        for l in response["languages"]:
            c = float(l["confidence"])
            if c > confidence:
                language = l["language"]
    except Exception as e:
        print(e)
    return language


def understand(text):
    response = ""
    try:
        response = naturalLanguageUnderstanding.analyze(
        text=text,
        features=Features(
            entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
            keywords=KeywordsOptions(emotion=True, sentiment=True,
                                    limit=2))).get_result()
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(e)
    return response


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
                transcript = stt(voice_file)
                os.remove(voice_file)
                if transcript != "" and transcript is not None:
                    if (info["stt"] is False):                        
                        update.message.text = transcript
                    else:
                        update.message.reply_text("Ho capito:\n" + transcript)

            # Check if the user sent a picture
            if len(update.message.photo) > 0:
                print("Received a Picture! Visual recognition in progress...")
                picture = bot.get_file(update.message.photo[-1].file_id)
                pic_file = picture.download()                    
                # Send Watson answer in Telegram chat
                update.message.reply_text((json.dumps(vrec(pic_file), indent=2)))
                os.remove(pic_file)
        
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
                        t = parsed_text[0]
                        tag = parsed_text[1]
                        # Execute tag commands:
                        if tag == "STT_START":
                            info["stt"] = True
                        elif tag == "STT_STOP":
                            info["stt"] = False
                        else:
                            update.message.reply_text("WARNING: unknown tag command")

                    # Post text in Telegram chat
                    if info["stt"] is False:
                        update.message.reply_text(t)
                    else:
                        update.message.reply_text("Modalità analisi messaggio attiva")
                        update.message.reply_text((json.dumps(understand(update.message.text), indent=2)))

                # This is for pictures link the response might contain
                if (len(response["output"]["generic"]) > 1):
                    try:
                        pic = response["output"]["generic"][1]["source"]
                        bot.send_photo(chat_id=update.message.chat_id, photo=pic)
                    except Exception as e:
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
