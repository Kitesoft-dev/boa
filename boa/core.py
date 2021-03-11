import subprocess
import typing
import locale
import enum
import abc
import os
import io


class Status(enum.Flag):
    """The status returned after a backup operation"""
    OK = enum.auto()

    UNAUTHORIZED = enum.auto()
    TIMEOUT = enum.auto()
    INTERNAL_ERROR = enum.auto()

    USER_ERROR = enum.auto()

    FAILED = UNAUTHORIZED | TIMEOUT | INTERNAL_ERROR | USER_ERROR


def is_status_failed(status: Status) -> bool:
    return bool(status & Status.FAILED)


class Source(abc.ABC):
    """Interface for backuppable classes"""
    def __bytes__(self) -> bytes:
        raise NotImplementedError


class FileSource(Source, abc.ABC):
    """Interface for File objects"""


class FilePathSource(FileSource):
    """Interface for FilePath objects (path-likes)"""

    def __init__(self, filepath: typing.Union[str, os.PathLike]):
        self.filepath = filepath

    def __bytes__(self) -> bytes:
        return open(self.filepath, 'rb').read()


class FileStreamSource(FileSource):
    """Interface for FileStream objects (text like)"""
    def __init__(self, stream: typing.Union[io.RawIOBase, io.BufferedIOBase, io.TextIOBase]):
        # set stream position to start
        # stream.seek(0)
        self.stream = stream

    def __bytes__(self) -> bytes:
        content = self.stream.read()
        if isinstance(content, str):
            if hasattr(self.stream, 'encoding'):
                encoding = self.stream.encoding
            else:
                encoding = locale.getpreferredencoding()
            return bytes(content, encoding=encoding)
        else:
            return bytes(content)


class CommandSource(Source):
    """Interface for Command objects (generating an output to backup)"""
    def __init__(self, *args, destination: typing.Optional[os.PathLike] = None):
        """Constructor for Command object

        :param args: The iterable command to launch
        :param destination: The destionation of the command. If None, stdout will be used.
        """
        self.args = args
        self.destination = destination

    def __bytes__(self) -> bytes:
        dst = self.destination
        # if dst is not set, the stdout will be used
        capture_output = not bool(dst)
        status = subprocess.run(*self.args, capture_output=capture_output)

        if capture_output:
            raw = status.stdout
        else:
            raw = open(self.destination, 'rb').read()
        return raw


class Destination(abc.ABC):
    """Interface for destination of backup"""
