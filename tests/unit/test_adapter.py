from boa.adapters import *
import pytest


def test_adapters():
    # valid adapter
    assert isinstance(get_adapter("telegram"), TelegramAdapter)

    # invalid adapter
    with pytest.raises(ValueError):
        get_adapter("foobar")
