import typing

import boa.adapters as adapters
import boa.core as core


class Boa:
    """Boa is the main entry for the application"""

    def __init__(self, adapter: typing.Union[None, str, adapters.BaseAdapter] = None):
        if isinstance(adapter, str):
            adapter = adapters.get_adapter(adapter)
        self.adapter = adapter

    def backup_single_in_single_out(
        self, source: core.Source, destination: core.Destination
    ) -> core.Status:
        """
        Backup the selected source into the destination.

        :param source: The file to backup or the command to run.
        :param destination: The destination of backup.
        :return: Status code of backup.
        """
        raw = bytes(source)
        if self.adapter:
            status = self.adapter.backup(raw, destination)
        else:
            destination.write(raw)
            status = core.Status.OK
        return status

    def backup_siso(
        self, source: core.Source, destination: core.Destination
    ) -> core.Status:
        """
        Backup the selected source into the destination.

        :param source: The file to backup or the command to run.
        :param destination: The destination of backup.
        :return: Status code of backup.
        """
        return self.backup_single_in_single_out(source, destination)

    def backup_multiple_in_single_out(
        self,
        sources: typing.Sequence[core.Source],
        destination: core.Destination,
    ) -> core.Status:
        """
        Backup the selected sources into the destination.

        The content will be merged across sources into
        a single destination.

        :param sources: The sources to backup.
        :param destination: The destination of backup.
        :return: Status code of backup.
        """
        raws = [bytes(source) for source in sources]
        raw = b"".join(raws)
        source = core.BytesSource(raw)
        return self.backup_siso(source, destination)

    def backup_miso(
        self,
        sources: typing.Sequence[core.Source],
        destination: core.Destination,
    ) -> core.Status:
        """
        Backup the selected sources into the destination.

        The content will be merged across sources into
        a single destination.

        :param sources: The sources to backup.
        :param destination: The destination of backup.
        :return: Status code of backup.
        """
        return self.backup_multiple_in_single_out(sources, destination)

    def backup_single_in_multiple_out(
        self,
        source: core.Source,
        destinations: typing.Sequence[core.Destination],
    ) -> typing.Sequence[core.Status]:
        """
        Backup the selected source into the destinations provided.

        A broadcast strategy will be used: the content
        of a single source will flow into every destination
        provided.

        :param source: The sources to backup.
        :param destinations: The destinations of backup.
        :return: Status codes of backup.
        """
        raw = bytes(source)
        bytesource = core.BytesSource(raw)
        return [
            self.backup_siso(bytesource, destination) for destination in destinations
        ]

    def backup_simo(
        self,
        source: core.Source,
        destinations: typing.Sequence[core.Destination],
    ) -> typing.Sequence[core.Status]:
        """
        Backup the selected source into the destinations provided.

        A broadcast strategy will be used: the content
        of a single source will flow into every destination
        provided.

        :param source: The sources to backup.
        :param destinations: The destinations of backup.
        :return: Status codes of backup.
        """
        return self.backup_single_in_multiple_out(source, destinations)

    def backup_multiple_in_multiple_out(
        self,
        sources: typing.Sequence[core.Source],
        destinations: typing.Sequence[core.Destination],
    ) -> typing.Sequence[core.Status]:
        """
        Backup the selected sources into the destinations provided.

        Provide a 1:1 match between sources and destinations;
        if there is a length mismatch, ValueError is raised.

        :param sources: The sources to backup.
        :param destinations: The destinations of backup.
        :return: Status codes of backup.
        """
        if len(sources) != len(destinations):
            raise ValueError("Length mismatch between source and destination!")

        return [
            self.backup_siso(source, destination)
            for (source, destination) in zip(sources, destinations)
        ]

    def backup_mimo(
        self,
        sources: typing.Sequence[core.Source],
        destinations: typing.Sequence[core.Destination],
    ) -> typing.Sequence[core.Status]:
        """
        Backup the selected sources into the destinations provided.

        Provide a 1:1 match between sources and destinations;
        if there is a length mismatch, ValueError is raised.

        :param sources: The sources to backup.
        :param destinations: The destinations of backup.
        :return: Status codes of backup.
        """
        return self.backup_multiple_in_multiple_out(sources, destinations)

    def backup(
        self,
        source: typing.Union[core.Source, typing.Sequence[core.Source]],
        destination: typing.Union[core.Destination, typing.Sequence[core.Destination]],
    ) -> typing.Union[core.Status, typing.Sequence[core.Status]]:
        """
        Backup the selected source(s) into the destination(s) provided.

        The correct strategy is selected based on the input.

        :param source: The source(s) to backup.
        :param destination: The destination(s) of backup.
        :return: Status code(s) of backup.
        """
        if isinstance(source, core.Source):
            if isinstance(destination, core.Destination):
                return self.backup_siso(source, destination)
            else:
                return self.backup_simo(source, destination)
        else:
            if isinstance(destination, core.Destination):
                return self.backup_miso(source, destination)
            else:
                return self.backup_mimo(source, destination)


def backup(source, destination, *, return_wrappers=False):
    """
    Backup the selected source(s) into the destination(s) provided.

    Source and destination will be converted into ``Source`` and
    ``Destination`` respectively. If this conversion fails,
    an exception will be raised.

    :param return_wrappers: If True, the ``Source`` and
    ``Destination`` objects will be returned after the status.
    :param source: The source to backup.
    :param destination: The destination of backup.
    :return: Status code of backup.
    """
    boa = Boa()
    _source = core.get_source(source)
    _destination = core.get_destination(destination)
    status = boa.backup(_source, _destination)
    if return_wrappers:
        return status, _source, _destination
    else:
        return status
