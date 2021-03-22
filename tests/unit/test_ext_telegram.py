import configparser

import pytest
from telegram.error import InvalidToken

import boa.core as core
from boa.ext.telegram import TelegramBotDestination


def test_cfg():
    parser = configparser.ConfigParser()
    parser.read("this file doesn't exist")
    assert parser.sections() == []

    parser.read("boa.cfg.example")
    assert len(parser.sections()) > 0

    assert parser["telegram"].get("token")
    assert parser["telegram"].get("chat_ids")
    chat_ids = parser["telegram"].get("chat_ids")
    chat_ids = [line for line in chat_ids.splitlines() if line]
    assert len(chat_ids) == 3
    assert chat_ids == ["123", "456", "789"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"section": "foo"},
        {"section": "telegram:no_token"},
        {"section": "telegram:no_token_val"},
        {"section": "telegram:no_chats"},
        {"section": "telegram:no_chats_val"},
    ],
)
def test_class_init(kwargs):
    with pytest.raises(ValueError):
        TelegramBotDestination(**kwargs)


def test_init_invalidtoken():
    with pytest.raises(InvalidToken):
        TelegramBotDestination(section="telegram:invalid_token")


def test_class_init_nofile():
    with pytest.raises(FileNotFoundError):
        TelegramBotDestination(config_filepath="this file doesn't exist!")


def test_send_ok():
    src = core.FilePathSource("boa.cfg.example")
    dst = TelegramBotDestination(
        filename="example_config.txt",
        message="Sample message, even emojis are supported! ❤😁👍🙌😎🐱‍🚀✔👀",
    )
    dst.write(bytes(src))
