import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

orgid = os.environ["ORGID"]
token = os.environ["TOKEN"]
queue = "COMMONTASKS"


def get_triggers(token, orgid, queue):
    headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
    response = requests.get(f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers", headers=headers)
    triggers = response.json()
    stored_triggers = []
    for trigger in triggers:
        for action in trigger["actions"]:
            if action["type"] == "Webhook":
                stored_triggers.append(trigger)
    return stored_triggers


def edit_trigger(token, orgid, triggers):
    for trigger in triggers:
        if trigger["id"] == 8:
            triggerid = trigger["id"]
            triggerversion = trigger["version"]
            triggeractions = trigger["actions"]
            triggeractions[0]["headers"]["Authorization"] = "TOKEN FOR REPLACE"
            print(triggeractions)
            data = json.dumps({"actions": triggeractions})
            print(f"DATA: {data}")
            headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
            response = requests.patch(f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers/{triggerid}?version={triggerversion}", headers=headers, data=data)
    return print(response.status_code)


triggers_for_edit = get_triggers(token, orgid, queue)
edit_trigger(token, orgid, triggers_for_edit)