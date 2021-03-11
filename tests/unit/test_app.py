from boa import Boa
from boa.core import FileStreamSource, FileStreamDestination
import io
import pytest


def test_boa():
    boa = Boa("telegram")
    src, dst = io.StringIO('Hello world!'), io.StringIO()

    # TODO remove when telegram adapter is done
    with pytest.raises(NotImplementedError):
        boa.backup(FileStreamSource(src), FileStreamDestination(dst))
