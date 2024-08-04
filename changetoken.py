import os
import sys
import json
import requests
from dotenv import load_dotenv
from logging import getLogger, basicConfig, FileHandler, StreamHandler, INFO


load_dotenv()
logger = getLogger(__name__)
FORMAT = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
file_handler = FileHandler("data.log")
file_handler.setLevel(INFO)
stream = StreamHandler()
stream.setLevel(INFO)
basicConfig(level=INFO, format=FORMAT, handlers=[file_handler, stream])


def get_triggers(token, orgid, orgheader, queue):
    headers = {orgheader: orgid, "Authorization": f"OAuth {token}"}
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


def edit_trigger(token, orgid, orgheader, triggers, new_token, prefix):
    for trigger in triggers:
        triggerid = trigger["id"]
        triggerversion = trigger["version"]
        triggeractions = trigger["actions"]
        actions = []
        for action in triggeractions:
            try:
                action["headers"].update({"Authorization": f"{prefix} {new_token}"})
                message = f"Trigger ID {triggerid} - token found in headers"
                logger.info("%s", message)
            except KeyError:
                message = (
                    f"Trigger ID {triggerid} - token has not been found in headers"
                )
                logger.warning("%s", message)
            try:
                if action["authContext"].get("accessToken") is not None:
                    action["authContext"]["accessToken"] = new_token
                    message = f"Trigger ID {triggerid} - token found in authContext"
                    logger.info("%s", message)
                else:
                    raise KeyError
            except KeyError:
                message = (
                    f"Trigger ID {triggerid} - token has not been found in authContext"
                )
                logger.warning("%s", message)
            actions.append(action)
        data = json.dumps({"actions": actions})
        headers = {orgheader: orgid, "Authorization": f"OAuth {token}"}
        if len(sys.argv) > 1 and sys.argv[1] == "--force":
            response = requests.patch(
                f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers/{triggerid}?version={triggerversion}",
                headers=headers,
                data=data,
            )
            message = f"Server answered: {response.json()}"
            return logger.info("%s", message)
        else:
            message = f"Actions would be replaced: {data}"
            return logger.info("%s", message)


if __name__ == "__main__":
    orgid = os.environ["ORGID"]
    orgheader = os.environ["ORG_HEADER"]
    token = os.environ["TOKEN"]
    queue = os.environ["QUEUE"]
    new_token = os.environ["NEWTOKEN"]
    prefix = os.environ["PREFIX"]

    triggers_for_edit = get_triggers(token, orgid, orgheader, queue)
    edit_trigger(token, orgid, orgheader, triggers_for_edit, new_token, prefix)
