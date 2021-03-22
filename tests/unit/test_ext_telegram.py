import dotenv
import pytest
from telegram.error import InvalidToken

import boa.core as core
from boa.ext.telegram import TelegramBotDestination
from tests.utility import set_env

TOKEN = "TELEGRAM_TOKEN"
CHAT_IDS = "TELEGRAM_CHAT_IDS"

dotenv.load_dotenv()


def test_missing_token():
    with set_env({TOKEN: ""}):
        with pytest.raises(ValueError):
            TelegramBotDestination()


def test_invalid_token():
    with set_env({TOKEN: "foobar"}):
        with pytest.raises(InvalidToken):
            TelegramBotDestination()


def test_invalid_chat():
    with set_env({CHAT_IDS: ""}):
        with pytest.raises(ValueError):
            TelegramBotDestination()


def test_send_ok():
    # do the actual backup
    src = core.FilePathSource("setup.py")
    dst = TelegramBotDestination(
        filename="setup.py",
        message="Sample message, even emojis are supported! ❤😁👍🙌😎🐱‍🚀✔👀",
    )
    dst.write(bytes(src))
