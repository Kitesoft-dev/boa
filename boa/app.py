from typing import List, Sequence, Tuple, Union

from boa.core import (
    BytesSource,
    Destination,
    Source,
    get_any_destination,
    get_any_source,
)


class Boa:
    """Boa is the main entry for the application"""

    def backup_single_in_single_out(self, source: Source, destination: Destination):
        """
        Backup the selected source into the destination.

        :param source: The file to backup or the command to run.
        :param destination: The destination of backup.
        """
        assert isinstance(source, Source)
        assert isinstance(destination, Destination)

        raw = bytes(source)
        return destination.write(raw)

    def backup_siso(self, source: Source, destination: Destination):
        """
        Backup the selected source into the destination.

        :param source: The file to backup or the command to run.
        :param destination: The destination of backup.
        """
        return self.backup_single_in_single_out(source, destination)

    def backup_multiple_in_single_out(
        self,
        sources: Sequence[Source],
        destination: Destination,
    ):
        """
        Backup the selected sources into the destination.

        The content will be merged across sources into
        a single destination.

        :param sources: The sources to backup.
        :param destination: The destination of backup.
        """
        assert isinstance(sources, (Tuple, List))
        assert all(isinstance(source, Source) for source in sources)
        assert isinstance(destination, Destination)

        raws = [bytes(source) for source in sources]
        raw = b"".join(raws)
        source = BytesSource(raw)
        return self.backup_siso(source, destination)

    def backup_miso(
        self,
        sources: Sequence[Source],
        destination: Destination,
    ):
        """
        Backup the selected sources into the destination.

        The content will be merged across sources into
        a single destination.

        :param sources: The sources to backup.
        :param destination: The destination of backup.
        """
        return self.backup_multiple_in_single_out(sources, destination)

    def backup_single_in_multiple_out(
        self,
        source: Source,
        destinations: Sequence[Destination],
    ):
        """
        Backup the selected source into the destinations provided.

        A broadcast strategy will be used: the content
        of a single source will flow into every destination
        provided.

        :param source: The sources to backup.
        :param destinations: The destinations of backup.
        """
        assert isinstance(source, Source)
        assert isinstance(destinations, (Tuple, List))
        assert all(isinstance(destination, Destination) for destination in destinations)

        raw = bytes(source)
        bytesource = BytesSource(raw)
        return [
            self.backup_siso(bytesource, destination) for destination in destinations
        ]

    def backup_simo(
        self,
        source: Source,
        destinations: Sequence[Destination],
    ):
        """
        Backup the selected source into the destinations provided.

        A broadcast strategy will be used: the content
        of a single source will flow into every destination
        provided.

        :param source: The sources to backup.
        :param destinations: The destinations of backup.
        """
        return self.backup_single_in_multiple_out(source, destinations)

    def backup_multiple_in_multiple_out(
        self,
        sources: Sequence[Source],
        destinations: Sequence[Destination],
    ):
        """
        Backup the selected sources into the destinations provided.

        Provide a 1:1 match between sources and destinations;
        if there is a length mismatch, ValueError is raised.

        :param sources: The sources to backup.
        :param destinations: The destinations of backup.
        """
        assert isinstance(sources, (Tuple, List))
        assert all(isinstance(source, Source) for source in sources)
        assert isinstance(sources, (Tuple, List))
        assert all(isinstance(destination, Destination) for destination in destinations)

        if len(sources) != len(destinations):
            raise ValueError("Length mismatch between source and destination!")

        return [
            self.backup_siso(source, destination)
            for (source, destination) in zip(sources, destinations)
        ]

    def backup_mimo(
        self,
        sources: Sequence[Source],
        destinations: Sequence[Destination],
    ):
        """
        Backup the selected sources into the destinations provided.

        Provide a 1:1 match between sources and destinations;
        if there is a length mismatch, ValueError is raised.

        :param sources: The sources to backup.
        :param destinations: The destinations of backup.
        """
        return self.backup_multiple_in_multiple_out(sources, destinations)

    def backup(
        self,
        source: Union[Source, Sequence[Source]],
        destination: Union[Destination, Sequence[Destination]],
    ):
        """
        Backup the selected source(s) into the destination(s) provided.

        The correct strategy is selected based on the input.

        :param source: The source(s) to backup.
        :param destination: The destination(s) of backup.
        """
        if isinstance(source, Source):
            if isinstance(destination, Destination):
                return self.backup_siso(source, destination)
            else:
                return self.backup_simo(source, destination)
        else:
            if isinstance(destination, Destination):
                return self.backup_miso(source, destination)
            else:
                return self.backup_mimo(source, destination)


def backup(source, destination, *, return_wrappers=False):
    """
    Backup the selected source(s) into the destination(s) provided.

    Source and destination will be converted into ``Source`` and
    ``Destination`` respectively. If this conversion fails,
    an exception will be raised.

    :param return_wrappers: If True, the Source and
    Destination objects will be returned.
    :param source: The source(s) to backup.
    :param destination: The destination(s) of backup.
    """
    boa = Boa()

    _source = get_any_source(source)
    _destination = get_any_destination(destination)
    boa.backup(_source, _destination)

    if return_wrappers:
        return _source, _destination
