import abc
import boa.core as c


class BaseAdapter(abc.ABC):
    """Base abstract class for adapters"""

    def backup(self, raw_object: bytes, dst: c.Destination) -> c.Status:
        """Backup the bytes object with the use of the adapter

        :param raw_object: The bytes to backup
        :param dst: The destination of backup
        :return: Status code of backup
        """
        raise NotImplementedError


class TelegramAdapter(BaseAdapter):
    """Telegram adapter"""

    def backup(self, raw_object: bytes, dst: c.Destination) -> c.Status:
        raise NotImplementedError


def get_adapter(adapter: str) -> BaseAdapter:
    adapters = {'telegram': TelegramAdapter()}
    adapter = adapter.lower()
    if adapter not in adapters:
        raise ValueError('Invalid adapter provided ({}). Valid adapters are {}'.format(adapter, adapters.keys()))
    return adapters[adapter]
