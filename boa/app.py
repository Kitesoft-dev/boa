import typing
from .adapters import BaseAdapter, get_adapter
from .core import BackupStatus
from pathlib import Path


class Boa:
    """Boa is the main entry for the application"""

    def __init__(self, adapter: typing.Union[str, BaseAdapter]):
        if isinstance(adapter, str):
            adapter = get_adapter(adapter)
        self.adapter = adapter

    def backup(self, file: typing.Union[str, Path]) -> BackupStatus:
        """Backup the selected file

        Parameters
        ----------
        file:
            The file to backup; can be either a path-like object, or a bytestream
        Returns
        -------
        BackupStatus
            the status of backup
        """
        if self._type_checker(file, [str, Path]):
            return self._backup_fp(file)
        elif self._type_checker(file, []):
            pass

    def _backup_fp(self, filepath: typing.Union[str, Path]) -> BackupStatus:

        return BackupStatus.OK

    @staticmethod
    def _type_checker(obj: typing.Any, types: typing.Iterable) -> bool:
        if not types:
            raise ValueError("types can't be empty")
        return any(isinstance(obj, t) for t in types)
