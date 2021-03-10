import abc
from .core import BackupStatus, Backuppable


class BaseAdapter(abc.ABC):
    """Base abstract class for wrappers"""

    def check_env(self):
        raise NotImplementedError

    def backup_file(self, backuppable: Backuppable):
        raise NotImplementedError


class TelegramAdapter(BaseAdapter):
    """Telegram adapter"""

    def check_env(self):
        pass

    def backup_file(self, backuppable: Backuppable):
        pass


def get_adapter(adapter: str) -> BaseAdapter:
    adapters = {'telegram': TelegramAdapter()}
    adapter = adapter.lower()
    if adapter not in adapters:
        raise ValueError('Invalid adapter provided ({}). Valid adapters are {}'.format(adapter, adapters.keys()))
    return adapters[adapter]
