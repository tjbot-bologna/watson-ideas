from __future__ import print_function
import json
from watson_developer_cloud import AssistantV1

context = None
user_input = ""

assistant = AssistantV1(
    username="e7c46313-e382-40f4-a77c-67f9e5cc15ea",
    password="1XaNGI6RwkOM",
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    url="https://gateway.watsonplatform.net/assistant/api",
    version="2018-07-10")

while True:
    user_input = input()

    response = assistant.message(
        workspace_id="4208099e-d443-405d-bba7-11c3d9f2c620",
        input={
            "text": user_input
        },
        context=context).get_result()

    context = response["context"]

    # print(json.dumps(response, indent=2))
    for t in response["output"]["text"]:
        print(t + "\n")