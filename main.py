import os
import json
import requests
from dotenv import load_dotenv


load_dotenv()

orgid = os.environ["ORGID"]
token = os.environ["TOKEN"]
queue = os.environ["QUEUE"]
new_token = os.environ["NEWTOKEN"]


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


def edit_trigger(token, orgid, triggers, new_token):
    for trigger in triggers:
        triggerid = trigger["id"]
        triggerversion = trigger["version"]
        triggeractions = trigger["actions"]
        actions = []
        for action in triggeractions:
            try:
                action["headers"]["Authorization"] = new_token
            except KeyError:
                print("Token has not been found in headers")    
            actions.append(action)
        data = json.dumps({"actions": actions})
        headers = {"X-Cloud-Org-Id": f"{orgid}", "Authorization": f"OAuth {token}"}
        response = requests.patch(f"https://api.tracker.yandex.net/v2/queues/{queue}/triggers/{triggerid}?version={triggerversion}", headers=headers, data=data)
        return response.status_code
    

if __name__ == "__main__":
    triggers_for_edit = get_triggers(token, orgid, queue)
    edit_trigger(token, orgid, triggers_for_edit)
