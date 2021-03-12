import subprocess
import typing
import locale
import enum
import abc
import os
import io


def get_encoding(obj: typing.Any):
    if hasattr(obj, 'encoding') and obj.encoding:
        encoding = obj.encoding
    else:
        encoding = locale.getpreferredencoding(False)
    return encoding


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
        if not content:
            return b''
        if isinstance(content, str):
            encoding = get_encoding(self.stream)
            raw = bytes(content, encoding=encoding)
        else:
            raw = bytes(content)
        return raw


class CommandSource(Source):
    """Interface for Command objects (generating an output to backup)"""
    def __init__(
            self,
            args: typing.Union[typing.List, typing.Tuple],
            destination: typing.Union[None, str, os.PathLike] = None,
            **kwargs):
        """Constructor for Command object. It follows the structure of subprocess.run() call

        :param args: The command to launch, must be list-like
        :param destination: The filepath destionation of the command. If None, stdout will be used
        :param kwargs: Keyword arguments to pass to subprocess.run() call
        """
        self.args = args
        self.kwargs = kwargs
        self.destination = destination

    def __bytes__(self) -> bytes:
        kwargs = self.kwargs.copy()
        # delete these keys from kwargs, if they exist
        for key in ('capture_output', 'stdout', 'stderr'):
            kwargs.pop(key, None)

        status = subprocess.run(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

        if self.destination:
            raw = open(self.destination, 'r+b').read()
        else:
            raw = status.stdout
        return raw


class Destination(abc.ABC):
    """Interface for destination of backup"""
    def write(self, content: bytes) -> Status:
        raise NotImplementedError


class FilePathDestination(Destination):
    """Interface for destination of backup on filesystem"""
    def __init__(self, filepath: typing.Union[str, os.PathLike]):
        self.filepath = filepath

    def write(self, content: bytes) -> Status:
        with open(self.filepath, 'wb') as f:
            f.write(content)
        return Status.OK


class FileStreamDestination(Destination):
    """Interface for destination of backup on in-memory stream"""
    def __init__(self, filestream: typing.Union[io.BytesIO, io.StringIO]):
        self.filestream = filestream

    def write(self, content: bytes) -> Status:
        if isinstance(self.filestream, io.StringIO):
            encoding = get_encoding(self.filestream)
            content = str(content, encoding=encoding)
        self.filestream.write(content)
        return Status.OK
