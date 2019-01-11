from __future__ import print_function
import json
from watson_developer_cloud import AssistantV1

context = None
user_input = ""

assistant = AssistantV1(
    iam_apikey="esXISM3aWlgM5HORbmxtKnQnG6_I-fTM3wFa2rLHYBL9",
    url="https://gateway.watsonplatform.net/assistant/api",
    version="2018-07-10")

while True:
    user_input = input()

    response = assistant.message(
        workspace_id="cb3034c7-dacf-4347-b292-2ba55fcb539d",
        input={
            "text": user_input
        },
        context=context).get_result()

    context = response["context"]

    # print(json.dumps(response, indent=2))
    for t in response["output"]["text"]:
        print(t)