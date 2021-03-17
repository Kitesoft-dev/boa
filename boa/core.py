import abc
import io
import locale
import os
import pathlib
import subprocess
from typing import List, Sequence, Tuple, Type, Union

from boa.exception import InvalidDestinationException, InvalidSourceException


def get_encoding(obj):
    if hasattr(obj, "encoding") and obj.encoding:
        encoding = obj.encoding
    else:
        encoding = locale.getpreferredencoding(False)
    return encoding


class Source(abc.ABC):
    """Interface for Source objects"""

    def __bytes__(self) -> bytes:
        raise NotImplementedError


class BytesSource(Source):
    """Interface for Bytes objects"""

    def __init__(self, raw: bytes):
        self.raw = raw

    def __bytes__(self):
        return self.raw


class FileSource(Source, abc.ABC):
    """Interface for File objects"""


class FilePathSource(FileSource):
    """Interface for FilePath objects (path-likes)"""

    def __init__(self, filepath: Union[str, os.PathLike]):
        self.filepath = filepath

    def __bytes__(self) -> bytes:
        return open(self.filepath, "rb").read()


class FileStreamSource(FileSource):
    """Interface for FileStream objects (text like)"""

    def __init__(
        self, filestream: Union[io.RawIOBase, io.BufferedIOBase, io.TextIOBase]
    ):
        self.filestream = filestream

    def __bytes__(self) -> bytes:
        content = self.filestream.read()
        if not content:
            return b""
        if isinstance(content, str):
            encoding = get_encoding(self.filestream)
            raw = bytes(content, encoding=encoding)
        else:
            raw = bytes(content)
        return raw


class CommandSource(Source):
    """Interface for Command objects (generating an output to backup)"""

    def __init__(
        self,
        args: Sequence,
        destination: Union[None, str, os.PathLike] = None,
        shell: bool = False,
    ):
        """Constructor for Command object. It follows the structure of subprocess.run() call

        :param args: The command to launch, must be sequence-like
        :param destination: The filepath destination of the command.
        If None, stdout will be used
        :param shell: Launch the command in shell mode or not
        """
        self.args = args
        self.destination = destination
        self.shell = shell

    def __bytes__(self) -> bytes:
        destination = (
            open(self.destination, "wb") if self.destination else subprocess.PIPE
        )
        status = subprocess.run(
            self.args, stdout=destination, stderr=subprocess.PIPE, shell=self.shell
        )
        raw = open(self.destination, "rb").read() if self.destination else status.stdout
        return raw


class Buffer(BytesSource):
    """Decorator for buffering Sources in memory"""

    def __init__(self, source: Source):
        raw = bytes(source)
        super().__init__(raw)


class Destination(abc.ABC):
    """Interface for destination of backup"""

    def write(self, content: bytes):
        raise NotImplementedError


class FilePathDestination(Destination):
    """Interface for destination of backup on filesystem"""

    def __init__(self, filepath: Union[str, os.PathLike]):
        self.filepath = filepath

    def write(self, content: bytes):
        with open(self.filepath, "wb") as f:
            f.write(content)


class FileStreamDestination(Destination):
    """Interface for destination of backup on in-memory stream"""

    def __init__(
        self, filestream: Union[io.RawIOBase, io.TextIOBase, io.BufferedIOBase]
    ):
        self.filestream = filestream

    def write(self, content: bytes):
        if isinstance(self.filestream, io.StringIO):
            encoding = get_encoding(self.filestream)
            content = str(content, encoding=encoding)
        self.filestream.write(content)


def _get_source(obj) -> Source:
    if isinstance(obj, Source):
        return obj
    elif isinstance(obj, bytes):
        return BytesSource(obj)
    elif isinstance(obj, (str, os.PathLike)):
        if not pathlib.Path(obj).exists():
            raise InvalidSourceException("Source path doesn't exist")
        else:
            return FilePathSource(obj)
    elif isinstance(obj, (io.RawIOBase, io.TextIOBase, io.BufferedIOBase)):
        return FileStreamSource(obj)
    else:
        raise InvalidSourceException("Unexpected source given")


def _get_destination(obj) -> Destination:
    if isinstance(obj, Destination):
        return obj
    elif isinstance(obj, (str, os.PathLike)):
        return FilePathDestination(obj)
    elif isinstance(obj, (io.RawIOBase, io.TextIOBase, io.BufferedIOBase)):
        return FileStreamDestination(obj)
    else:
        raise InvalidDestinationException("Unexpected destination given")


def _get(obj, expected: Type) -> Union[Source, Destination]:
    if expected not in (Source, Destination):
        raise ValueError(
            f"Expected class not valid ({expected.__name__}). "
            f"Allowed are {Source.__name__} and {Destination.__name__}"
        )
    if expected is Source:
        return _get_source(obj)
    else:
        return _get_destination(obj)


def get_source(source) -> Source:
    return _get(source, Source)


def get_destination(destination) -> Destination:
    return _get(destination, Destination)


def get_sources(sources) -> Sequence[Source]:
    return [get_source(source) for source in sources]


def get_destinations(destinations) -> Sequence[Destination]:
    return [get_destination(destination) for destination in destinations]


def _get_any(
    obj, expected: Type
) -> Union[Source, Destination, Sequence[Source], Sequence[Destination]]:
    if expected not in (Source, Destination):
        raise ValueError(
            f"Expected class not valid ({expected}). "
            f"Allowed are {Source.__name__} and {Destination.__name__}"
        )
    if isinstance(obj, (Tuple, List)):
        return get_sources(obj) if expected is Source else get_destinations(obj)
    else:
        return get_source(obj) if expected is Source else get_destination(obj)


def get_any_source(source) -> Union[Source, Sequence[Source]]:
    return _get_any(source, Source)


def get_any_destination(destination) -> Union[Destination, Sequence[Destination]]:
    return _get_any(destination, Destination)
