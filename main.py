import os
import sys
import json
import requests
from dotenv import load_dotenv
from logging import getLogger, basicConfig, FileHandler, StreamHandler, DEBUG, ERROR, INFO


load_dotenv()
logger = getLogger(__name__)
FORMAT = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
file_handler = FileHandler("data.log")
file_handler.setLevel(INFO)
stream = StreamHandler()
stream.setLevel(INFO)
basicConfig(level=INFO, format=FORMAT, handlers=[file_handler, stream])


def get_triggers(token, orgid, queue):
    headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
    response = requests.get(
        f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers", headers=headers
    )
    triggers = response.json()
    stored_triggers = []
    for trigger in triggers:
        for action in trigger["actions"]:
            if action["type"] == "Webhook":
                stored_triggers.append(trigger)
    return stored_triggers


def edit_trigger(token, orgid, triggers, new_token, prefix):
    for trigger in triggers:
        triggerid = trigger["id"]
        triggerversion = trigger["version"]
        triggeractions = trigger["actions"]
        actions = []
        for action in triggeractions:
            try:
                old_token = action["headers"]["Authorization"]
                old_tokentoken = f"{prefix} {new_token}"
                message = f"Trigger ID {triggerid} - token found in headers"
                logger.info("%s", message)
            except KeyError:
                message = f"Trigger ID {triggerid} - token has not been found in headers"
                logger.error("%s", message)
            try:
                old_token = action["authContext"]["accessToken"]
                old_token = new_token
                message = f"Trigger ID {triggerid} - token found in authContext"
                logger.info("%s", message)
            except KeyError:
                message = f"Trigger ID {triggerid} - token has not been found in authContext"
                logger.error("%s", message)
            actions.append(action)
        data = json.dumps({"actions": actions})
        headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
        if len(sys.argv) > 1 and sys.argv[1] == "--force":
            response = requests.patch(
                f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers/{triggerid}?version={triggerversion}",
                headers=headers,
                data=data,
            )
            message = f"Server answered: {response.json()}"
            logger.info("%s", message)
            return response.json()
        else:
            return data


if __name__ == "__main__":
    orgid = os.environ["ORGID"]
    token = os.environ["TOKEN"]
    queue = os.environ["QUEUE"]
    new_token = os.environ["NEWTOKEN"]
    prefix = os.environ["PREFIX"]

    triggers_for_edit = get_triggers(token, orgid, queue)
    edit_trigger(token, orgid, triggers_for_edit, new_token, prefix)
