import pytest

import boa.adapters as adapters


def test_adapters():
    valid = "telegram"
    invalid = "foo"

    # valid adapter
    adapter = adapters.get_adapter(valid)
    assert isinstance(adapter, adapters.TelegramAdapter)
    assert isinstance(adapter, adapters.BaseAdapter)

    # invalid adapter
    with pytest.raises(ValueError):
        adapters.get_adapter(invalid)
