import typing
import boa.adapters as adapters
import boa.core as core


class Boa:
    """Boa is the main entry for the application"""

    def __init__(self, adapter: typing.Union[None, str, adapters.BaseAdapter] = None):
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
        if self.adapter:
            status = self.adapter.backup(raw, dst)
        else:
            dst.write(raw)
            status = core.Status.OK
        return status
