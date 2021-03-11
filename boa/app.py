import typing
import boa.adapters as adapters
import boa.core as core


class Boa:
    """Boa is the main entry for the application"""

    def __init__(self, adapter: typing.Union[str, adapters.BaseAdapter]):
        if isinstance(adapter, str):
            adapter = adapters.get_adapter(adapter)
        self.adapter = adapter

    def backup(self, src: core.Source, dst: core.Destination) -> core.Status:
        """Backup the selected file

        :param src: The file to backup or the command to run
        :param dst: The destination of backup
        :return: Status code of backup
        """
        raw = bytes(src)
        status = self.adapter.backup(raw, dst)
        return status
