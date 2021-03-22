import abc
import configparser
import os
import pathlib
from typing import Union

from telegram.ext import Updater

import boa.core as core


class TelegramDestination(core.Destination, abc.ABC):
    def __init__(
        self, config_filepath: Union[str, os.PathLike, None] = None, section: str = None
    ):
        if not config_filepath:
            config_filepath = "boa.cfg"

        if not section:
            section = "telegram"

        config = configparser.ConfigParser()

        if not pathlib.Path(config_filepath).exists():
            raise FileNotFoundError(f"{config_filepath} doesn't exist")

        # read config from file and load into parser obj
        config.read(config_filepath)

        # check if given section is valid
        if not config.has_section(section):
            raise ValueError(f"Section '{section}' not found in {config_filepath}")

        token = config[section].get("token")
        if not token:
            raise ValueError("Missing token!")
        updater = Updater(token, use_context=True)

        self.config_filepath = config_filepath
        self.section = section

        self.config = config
        self.updater = updater


class TelegramBotDestination(TelegramDestination):
    def __init__(
        self,
        filename: str = None,
        message: str = None,
        config_filepath: Union[str, os.PathLike, None] = None,
        section: str = None,
    ):
        super().__init__(config_filepath=config_filepath, section=section)

        self.message = message
        self.filename = filename

        chat_ids = self.config[self.section].get("chat_ids")
        # if not empty string, get array
        if chat_ids:
            chat_ids = [line for line in chat_ids.split() if line]
        # if empty array, error
        if not chat_ids:
            raise ValueError("Missing chat ids!")

        self.chat_ids = chat_ids

    def write(self, content: bytes):
        for chat_id in self.chat_ids:
            self.updater.bot.send_document(
                chat_id=chat_id,
                document=content,
                filename=self.filename,
                caption=self.message,
            )
