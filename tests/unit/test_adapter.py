import pytest

from boa.adapters import *


def test_adapters():
    valid = "telegram"
    invalid = "foo"

    # valid adapter
    adapter = get_adapter(valid)
    assert isinstance(adapter, TelegramAdapter)
    assert isinstance(adapter, BaseAdapter)

    # invalid adapter
    with pytest.raises(ValueError):
        get_adapter(invalid)
