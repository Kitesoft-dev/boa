import io
import tempfile

import pytest

from boa import Boa, backup
from boa.core import (
    BytesSource,
    Destination,
    FileStreamDestination,
    FileStreamSource,
    Source,
)
from boa.exception import InvalidDestinationException, InvalidSourceException


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


@pytest.mark.parametrize(
    "src",
    [
        b"foo",
        tempfile.NamedTemporaryFile("w+b", delete=False).name,
        io.StringIO("hello world"),
        BytesSource(b"hello"),
        [b"foo", b"bar"],
    ],
)
@pytest.mark.parametrize(
    "dst",
    [
        tempfile.NamedTemporaryFile("w+b", delete=False).name,
        io.BytesIO(),
        FileStreamDestination(io.BytesIO()),
        [io.BytesIO(), io.BytesIO()],
    ],
)
@pytest.mark.parametrize("return_wrappers", [True, False])
def test_backup(src, dst, return_wrappers):
    # we already know that backup works, so we
    # just need to check if conversions are working good
    result = backup(src, dst, return_wrappers=return_wrappers)

    if not return_wrappers:
        assert result is None
    else:
        assert len(result) == 2
        assert isinstance(result[0], (tuple, list, Source))
        assert isinstance(result[1], (tuple, list, Destination))


def test_backup_out():
    with open("setup.py", "rb") as f:
        src = f.read()
    dst = tempfile.NamedTemporaryFile("w+t", delete=False).name
    backup(src, dst)
    with open(dst, "rb") as f:
        assert f.read() == src


@pytest.mark.parametrize("src", ["this_file_doesnt_exist.txt", 123])
@pytest.mark.parametrize("dst", [io.BytesIO()])
def test_backup_wrong_source(src, dst):
    with pytest.raises(InvalidSourceException):
        backup(src, dst)


@pytest.mark.parametrize("src", [io.BytesIO(b"foo")])
@pytest.mark.parametrize("dst", [123, b"wrong"])
def test_backup_wrong_dest(src, dst):
    with pytest.raises(InvalidDestinationException):
        backup(src, dst)
