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
                token = action["headers"]["Authorization"]
                token = f"{prefix} {new_token}"
                logger.info("%s", "Token found in headers")
            except KeyError:
                logger.error("%s", "Token has not been found in headers")
            try:
                token = action["authContext"]["accessToken"]
                token = new_token
                logger.info("%s", "Token found in authContext")
            except KeyError:
                logger.error("%s", "Token has not been found even in authContext")
            message = f"Found trigger {action["id"]}"
            logger.info("%s", message)
            print(action)
            actions.append(action)
        data = json.dumps({"actions": actions})
        headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
        if len(sys.argv) > 1 and sys.argv[1] == "--force":
            response = requests.patch(
                f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers/{triggerid}?version={triggerversion}",
                headers=headers,
                data=data,
            )
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
