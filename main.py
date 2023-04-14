import os
from dotenv import load_dotenv
import socket
import requests
import re
import webbrowser
import threading
import time
from flask import Flask, request

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
                        username, channel, message = re.search(
                            ":(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)", line
                        ).groups()
                        print(
                            f"Channel: {channel} \nUsername: {username} \nMessage: {message}"
                        )

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