import abc


class BaseAdapter(abc.ABC):
    """Base abstract class for wrappers"""
    def check_env(self):
        raise NotImplementedError

    def backup_file(self, file_content: bytes):
        raise NotImplementedError


class TelegramAdapter(BaseAdapter):
    """Telegram adapter"""

    def check_env(self):
        pass

    def backup_file(self, file_content: bytes):
        pass
