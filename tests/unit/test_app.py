import io

import pytest

from boa import Boa
from boa.core import BytesSource, FileStreamDestination, FileStreamSource


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
    boa.backup_siso(FileStreamSource(src), FileStreamDestination(dst))
    dst.seek(0)
    assert dst.read() == msg

    # backup bytes stream
    boa.backup_siso(FileStreamSource(bsrc), FileStreamDestination(bdst))
    bdst.seek(0)
    assert bdst.read() == bmsg

    # setup boa with telegram adapter
    boa = Boa("telegram")
    src, dst = io.BytesIO(bmsg), io.BytesIO()

    # TODO remove when telegram adapter is done
    with pytest.raises(NotImplementedError):
        boa.backup_siso(FileStreamSource(src), FileStreamDestination(dst))


def test_boa_backup_siso():
    boa = Boa()
    msg = b"foo"

    source = BytesSource(msg)
    destination = FileStreamDestination(io.BytesIO())
    boa.backup(source, destination)
    destination.filestream.seek(0)
    assert destination.filestream.read() == msg


def test_boa_backup_simo():
    boa = Boa()
    msg = b"foo"
    length = 3

    source = BytesSource(msg)
    destinations = [FileStreamDestination(io.BytesIO()) for _ in range(length)]
    boa.backup(source, destinations)
    for destination in destinations:
        destination.filestream.seek(0)
        assert destination.filestream.read() == msg


def test_boa_backup_miso():
    boa = Boa()
    msg = b"foo"
    length = 3

    sources = [BytesSource(msg) for _ in range(length)]
    destination = FileStreamDestination(io.BytesIO())
    boa.backup(sources, destination)
    destination.filestream.seek(0)
    assert destination.filestream.read() == msg * length


def test_boa_backup_mimo():
    boa = Boa()
    msg = b"foo"
    length = 3

    sources = [BytesSource(msg) for _ in range(length)]
    destinations = [FileStreamDestination(io.BytesIO()) for _ in range(length)]
    boa.backup(sources, destinations)
    for message, destination in zip([msg] * length, destinations):
        destination.filestream.seek(0)
        assert destination.filestream.read() == message

    # mismatch length
    sources = [BytesSource(msg) for _ in range(length)]
    destinations = [FileStreamDestination(io.BytesIO()) for _ in range(length + 1)]
    with pytest.raises(ValueError):
        boa.backup(sources, destinations)
