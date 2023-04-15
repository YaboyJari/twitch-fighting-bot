import os
from dotenv import load_dotenv
import socket
import requests
import re
import webbrowser
import threading
import time
from flask import Flask, request
import vgamepad as vg
from shared_gamepad import GAMEPAD

load_dotenv()

app = Flask(__name__)


class TwitchBot:
    def __init__(self):
        self.SERVER = os.getenv("SERVER")
        self.PORT = os.getenv("PORT")
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.BOT_NAME = os.getenv("BOT_NAME")
        self.CHANNEL = "#jayrivm"
        self.sock = socket.socket()
        self.callback_completed = False
        self.sock.connect((self.SERVER, int(self.PORT)))
        self.gamepad = GAMEPAD

    def join_chat(self):
        loaded = False
        while True:
            resp = self.sock.recv(2048).decode("utf-8")

            if resp.startswith("PING"):
                self.sock.send("PONG\n".encode("utf-8"))

            elif len(resp) > 0:
                for line in resp.split("\n")[:-1]:
                    if not loaded:
                        loaded = self.check_load_complete(line)
                    else:
                        _, _, message = re.search(
                            ":(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)", line
                        ).groups()
                        self.map_chat_to_input(message)

    def check_load_complete(self, line):
        if "End of /NAMES list" not in line:
            return False
        print(f"{self.BOT_NAME} joined {self.CHANNEL}'s channel")
        return True

    def get_access_token(self):
        webbrowser.open(
            f"https://id.twitch.tv/oauth2/authorize?client_id={self.CLIENT_ID}&redirect_uri=http://localhost:3000&response_type=code&scope=chat:read+chat:edit"
        )
        while not self.callback_completed:
            time.sleep(1)
        self.callback_completed = False
        CODE = os.getenv("CODE")
        token_URL = "https://id.twitch.tv/oauth2/token"
        validate_URL = "https://id.twitch.tv/oauth2/validate"
        token_params = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:3000",
            "code": CODE,
        }
        token_call = requests.post(url=token_URL, params=token_params)
        access_token = token_call.json()["access_token"]
        validate_headers = {"Authorization": f"OAuth {access_token}"}
        validate_call = requests.get(url=validate_URL, headers=validate_headers)
        if validate_call.status_code == 200:
            return access_token
        return None

    def run_bot(self):
        print("Running bot")
        access_token = self.get_access_token()
        try:
            if access_token:
                oauth_access_token = f"oauth:{access_token}"
                self.sock.send(f"PASS {oauth_access_token}\n".encode("utf-8"))
                self.sock.send(f"NICK {self.BOT_NAME}\n".encode("utf-8"))
                self.sock.send(f"JOIN {self.CHANNEL}\n".encode("utf-8"))
                self.join_chat()
            else:
                self.sock.close()
        except Exception as e:
            print(e)
            self.sock.close()

    def map_chat_to_input(self, message):
        if message.strip().lower() == "a":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "b":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "x":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "y":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "ll":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.gamepad.update()
            time.sleep(0.5)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "lr":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.update()
            time.sleep(0.5)
            self.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "right":
            self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=0.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "left":
            self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=0.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "up":
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "down":
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "dld":
            self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "dlu":
            self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "drd":
            self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "dru":
            self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=1.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "ql":
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.left_joystick_float(x_value_float=-1.0, y_value_float=0.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "qr":
            self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=-1.0)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.left_joystick_float(x_value_float=1.0, y_value_float=0.0)
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "rb":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(
                button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER
            )
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "rbl":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            self.gamepad.update()
            time.sleep(1.0)
            self.gamepad.release_button(
                button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER
            )
            self.gamepad.update()
            time.sleep(0.1)
        elif message.strip().lower() == "lb":
            self.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(
                button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER
            )
            self.gamepad.update()
            time.sleep(0.1)
        else:
            print("Button not found")
        print("Updating gamepad choice...")
        self.gamepad.reset()
        self.gamepad.update()


def run_flask_app():
    if __name__ == "__main__":
        app.run(host="localhost", port=3000)


@app.route("/", methods=["GET"])
def callback():
    code = request.args.get("code")
    print(f"Callback received with code: {code}")
    if code:
        os.environ["CODE"] = code
        bot.callback_completed = True
        return {"success": True}
    else:
        return {"success": False}


bot = TwitchBot()

flask_thread = threading.Thread(target=run_flask_app)
flask_thread.start()
bot_thread = threading.Thread(target=bot.run_bot)
bot_thread.start()

flask_thread.join()
bot_thread.join()
