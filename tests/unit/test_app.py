import io

import pytest

from boa import Boa
from boa.core import FileStreamDestination, FileStreamSource


def test_stringio():
    msg = "foobar"
    src, dst = io.StringIO(msg), io.StringIO()
    assert src.read() == msg

    dst.write(msg)  # src.read()
    dst.seek(0)
    assert dst.read() == msg


def test_boa():
    msg = "foobar"
    bmsg = msg.encode()  # b'foobar'

    # create streams of str and bytes
    src, dst = io.StringIO(msg), io.StringIO()
    bsrc, bdst = io.BytesIO(bmsg), io.BytesIO()

    # setup boa without adapters
    boa = Boa()

    # backup str stream
    boa.backup(FileStreamSource(src), FileStreamDestination(dst))
    dst.seek(0)
    assert dst.read() == msg

    # backup bytes stream
    boa.backup(FileStreamSource(bsrc), FileStreamDestination(bdst))
    bdst.seek(0)
    assert bdst.read() == bmsg

    # setup boa with telegram adapter
    boa = Boa("telegram")
    src, dst = io.BytesIO(bmsg), io.BytesIO()

    # TODO remove when telegram adapter is done
    with pytest.raises(NotImplementedError):
        boa.backup(FileStreamSource(src), FileStreamDestination(dst))
