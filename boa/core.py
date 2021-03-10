import enum
import abc


class BackupStatus(enum.Flag):
    """The status returned after a backup operation"""
    OK = enum.auto()

    UNAUTHORIZED = enum.auto()
    TIMEOUT = enum.auto()
    INTERNAL_ERROR = enum.auto()
    FAILED = UNAUTHORIZED | TIMEOUT | INTERNAL_ERROR


def is_status_failed(status: BackupStatus) -> bool:
    return bool(status & BackupStatus.FAILED)


class Backuppable(abc.ABC):
    """Interface for backuppable classes"""


class File(Backuppable):
    """Interface for File objects"""


class FilePath(File):
    """Interface for FilePath objects (path-likes)"""


class FileStream(File):
    """Interface for FileStream objects (byte-likes)"""


class Command(Backuppable):
    """Interface for Command objects (generating an output to backup)"""
