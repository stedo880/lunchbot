import asyncio
import json
import logging
import os
import random
from datetime import date
from datetime import datetime

import discord
import pytz


class LunchBotConfig:
    TIMEZONE = "Europe/Stockholm"
    ANNOUNCEMENT_HOUR = 9
    CHANNEL_ID = 540608386299985940  # Highly Unprofessional / lunch


class LunchBot(discord.Client):
    CMD_OW = "!ow"
    CMD_LUNCH = "!lunch"
    CMD_TEST_LUNCH = "!testlunch"
    CMD_ANNOUNCEMENTS = "!announcements"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init stuff
        self.lunch_message: str = ""
        self.config: dict = {}
        self.ow_char_classes: dict = {}
        self.last_announcement_date = ""
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")

    async def load_config(self):
        with open("config.json") as json_data_file:
            self.config = json.load(json_data_file)

        # read lunch options
        self.lunch_message = ""
        for option in self.config["lunch_options"]:
            self.lunch_message += option["emoji"] + " " + option["label"] + "\n"

        # read overwatch characters
        self.ow_char_classes = self.config["ow_char_classes"]

    async def write_config(self):
        print("Writing config data")
        print(self.config)
        with open("config.json", "w") as outfile:
            json.dump(self.config, outfile)
        print("Done")

    async def on_ready(self):
        await self.load_config()
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("Announcements are " + str(self.announcements_enabled))
        print("------")
        self.loop.create_task(self.lunch_task())

    async def on_message(self, message):
        if message.content == self.CMD_LUNCH:
            await self.send_lunch_message()
        elif message.content == self.CMD_TEST_LUNCH:
            await self.send_test_message(message)
        elif message.content == self.CMD_ANNOUNCEMENTS:
            await self.send_announcements(message)
        elif message.content.startswith(self.CMD_OW):
            await self.send_ow_message(message)

    async def send_lunch_message(self):
        channel = self.get_channel(LunchBotConfig.CHANNEL_ID)
        await channel.send(self.lunch_message)

    async def send_test_message(self, message=None):
        await message.author.send(self.lunch_message)

    async def send_announcements(self, message):
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")
        await message.author.send(
            "Announcements are " + str(self.announcements_enabled)
        )
        await message.author.send("This can be changed in the Heroku Config Vars")

    async def send_ow_message(self, message):
        # eg get "tank" from "!ow tank"
        char_class = message.content.strip(f" {self.CMD_OW}")

        if char_class in self.ow_char_classes:
            chars_to_choose_from = self.ow_char_classes[char_class]
        else:
            all_chars = [
                char
                for char_class in self.ow_char_classes.values()
                for char in char_class
            ]
            chars_to_choose_from = all_chars

        random_char = random.choice(chars_to_choose_from)
        await message.channel.send(random_char)

    async def lunch_task(self):
        print("Entering background_task")
        await self.wait_until_ready()

        print("Checking not self.is_closed")
        while not self.is_closed():
            # check if announcements are enabled
            print("Checking self.announcements")
            if self.announcements_enabled:
                # check if we already sent a message today
                print("Checking self.last_announcement_date")
                todays_date = date.today()
                has_announced_today = todays_date == self.last_announcement_date

                if not has_announced_today:
                    # check if it's time to send the voting message
                    current_datetime = datetime.now(
                        pytz.timezone(LunchBotConfig.TIMEZONE)
                    )

                    print("Checking weekday and hour")
                    is_workingday = current_datetime.weekday() < 5
                    is_time_for_announcement = (
                        current_datetime.hour == LunchBotConfig.ANNOUNCEMENT_HOUR
                    )

                    if is_workingday and is_time_for_announcement:
                        print("Setting self.last_annoucement")
                        self.last_announcement_date = todays_date

                        print("Sending lunch message")
                        await self.send_lunch_message()

            print("Sleep for 60 seconds")
            await asyncio.sleep(60)  # task runs every 60 seconds


def setup_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


if __name__ == "__main__":
    setup_logging()

    bot = LunchBot()
    api_token = os.getenv("LUNCHBOT_TOKEN")
    bot.run(api_token)
