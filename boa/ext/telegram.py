import abc
import os

from telegram.ext import Updater

import boa.core as core


class TelegramDestination(core.Destination, abc.ABC):
    def __init__(self):
        token = os.getenv("TELEGRAM_TOKEN", None)
        if not token:
            raise ValueError("Missing token!")
        updater = Updater(token, use_context=True)
        self.updater = updater


class TelegramBotDestination(TelegramDestination):
    def __init__(
        self,
        filename: str = None,
        message: str = None,
    ):
        super().__init__()

        self.message = message
        self.filename = filename

        chat_ids = os.getenv("TELEGRAM_CHAT_IDS", None)
        # if not empty string, get array
        if chat_ids:
            chat_ids = [word for word in chat_ids.strip().split() if word.isnumeric()]
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
