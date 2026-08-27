"""
Project : Smart_Bourse

File : eitaa_bot.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Eitaa Notification Bot
"""

import requests


class EitaaBot:

    def __init__(self, token="", chat_id=""):

        self.token = token

        self.chat_id = chat_id

    # --------------------------------------------------

    def send(self, message):

        if self.token == "" or self.chat_id == "":

            print("Eitaa Bot Not Configured")

            return False

        url = f"https://eitaayar.ir/api/{self.token}/sendMessage"

        data = {

            "chat_id": self.chat_id,

            "text": message

        }

        try:

            requests.post(

                url,

                data=data,

                timeout=10

            )

            print("Message Sent")

            return True

        except Exception as error:

            print(error)

            return False

    # --------------------------------------------------

    def buy_signal(self, symbol, price):

        self.send(

            f"🟢 BUY\n{symbol}\nPrice : {price}"

        )

    # --------------------------------------------------

    def sell_signal(self, symbol, price):

        self.send(

            f"🔴 SELL\n{symbol}\nPrice : {price}"

        )
