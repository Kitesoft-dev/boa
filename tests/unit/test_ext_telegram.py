import os

import dotenv
import pytest
from telegram.error import InvalidToken

import boa.core as core
from boa.ext.telegram import TelegramBotDestination
from tests.utility import set_env

KEY_TOKEN = "TELEGRAM_TOKEN"
KEY_CHATS = "TELEGRAM_CHAT_IDS"


def test_missing_token():
    with set_env({KEY_TOKEN: ""}):
        with pytest.raises(ValueError):
            TelegramBotDestination()


def test_invalid_token():
    with set_env({KEY_TOKEN: "foobar"}):
        with pytest.raises(InvalidToken):
            TelegramBotDestination()


def test_invalid_chat():
    # get valid token and chats, but invalidate chats
    dotenv.load_dotenv(override=True)
    os.environ.update({KEY_CHATS: ""})

    with pytest.raises(ValueError):
        TelegramBotDestination()


def test_send_ok():
    # get token and chat ids from .env
    dotenv.load_dotenv(override=True)

    # do the actual backup
    src = core.FilePathSource("setup.py")
    dst = TelegramBotDestination(
        filename="setup.py",
        message="Sample message, even emojis are supported! ❤😁👍🙌😎🐱‍🚀✔👀",
    )
    dst.write(bytes(src))
