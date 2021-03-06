import io
import locale
import sys
import tempfile

import pytest

import boa.core as core
from boa.exception import InvalidDestinationException, InvalidSourceException

is_win = sys.platform == "win32"


def test_get_encoding():
    class Foo:
        encoding = None

    # create an object without 'encoding' property
    obj = object()
    default_encoding = locale.getpreferredencoding(False)

    # without property, returns default encoding
    assert core.get_encoding(obj) == default_encoding

    # now create an object with 'encoding' property
    obj = Foo()

    # with null or empty property, returns default encoding
    obj.encoding = None
    assert core.get_encoding(obj) == default_encoding

    obj.encoding = ""
    assert core.get_encoding(obj) == default_encoding

    # with set property, returns it
    enc = "foo"
    obj.encoding = enc
    assert core.get_encoding(obj) == enc


def test_source_bytes():
    msg = "Hello"
    bmsg = msg.encode()

    source = core.BytesSource(bmsg)
    assert bytes(source) == bmsg


def test_source_file():
    msg = "Hello world!"
    bmsg = msg.encode("utf-8")  # b'Hello world!'

    # Test filestream
    # bytes
    with tempfile.TemporaryFile() as fp:
        fp.write(bmsg)
        fp.seek(0)
        source = core.FileStreamSource(fp)
        assert bytes(source) == bmsg

    # text (str)
    with tempfile.TemporaryFile("w+t") as fp:
        fp.write(msg)
        fp.seek(0)
        source = core.FileStreamSource(fp)
        assert bytes(source) == bmsg

    # Test filepath
    # bytes
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(bmsg)
    source = core.FilePathSource(fp.name)
    assert bytes(source) == bmsg

    # text (str)
    with tempfile.NamedTemporaryFile("w+t", delete=False) as fp:
        fp.write(msg)
    source = core.FilePathSource(fp.name)
    assert bytes(source) == bmsg

    # test exausted stream
    stream = io.StringIO("foo")
    stream.read()  # exaust
    source = core.FileStreamSource(stream)
    assert bytes(source) == b""


def test_source_command():
    # setup message and command
    msg = "foo"
    bmsg = msg.encode()
    cmd = ["echo", msg]

    # on windows shell must be true
    shell = bool(is_win)

    # with null destination, bytes will return stdout
    source = core.CommandSource(cmd, shell=shell)
    assert bytes(source).strip() == bmsg

    # with destination set, bytes method will return its content
    with tempfile.NamedTemporaryFile() as dst:
        source = core.CommandSource(cmd, destination=dst.name, shell=shell)
    assert bytes(source).strip() == bmsg


def test_destination_filepath():
    msg = "foo"
    bmsg = msg.encode()

    # test text file
    fp = tempfile.NamedTemporaryFile("w+t", delete=False)
    dst = core.FilePathDestination(fp.name)
    dst.write(bmsg)
    assert fp.read() == msg

    # test binary file
    fp = tempfile.NamedTemporaryFile("w+b", delete=False)
    dst = core.FilePathDestination(fp.name)
    dst.write(bmsg)
    assert fp.read() == bmsg


@pytest.mark.parametrize(
    "src, dst, src_expected, dst_expected",
    [
        [
            tempfile.NamedTemporaryFile("w+t", delete=False).name,
            "bar",
            core.FilePathSource,
            core.FilePathDestination,
        ],
        [
            io.StringIO(),
            io.BytesIO(),
            core.FileStreamSource,
            core.FileStreamDestination,
        ],
    ],
)
def test_get(src, dst, src_expected, dst_expected):
    src = core.get_source(src)
    dst = core.get_destination(dst)
    assert isinstance(src, src_expected)
    assert isinstance(dst, dst_expected)


def test_get_multiple():
    srcs = core.get_sources([io.StringIO(), io.BytesIO()])
    dsts = core.get_destinations([io.BytesIO()])
    assert all(isinstance(src, core.Source) for src in srcs)
    assert all(isinstance(dst, core.Destination) for dst in dsts)


def test_get_wrong_expected():
    with pytest.raises(ValueError):
        core._get("foo", str)

    with pytest.raises(ValueError):
        core._get_any("bar", str)

    with pytest.raises(InvalidSourceException):
        core.get_source("foobar.txt")

    with pytest.raises(InvalidDestinationException):
        core.get_destination(123)


def test_buffered():
    msg = b"hello world"
    tries = 3

    # filepath
    with tempfile.NamedTemporaryFile("w+b", delete=False) as fp:
        fp.write(msg)

    source = core.Buffer(core.FilePathSource(fp.name))

    # test against exahustation with for loop
    for _ in range(tries):
        assert bytes(source) == msg

    # filestream
    source = core.Buffer(core.FileStreamSource(io.BytesIO(msg)))

    for _ in range(tries):
        assert bytes(source) == msg

    # command
    # setup message and command
    msg = "foo"
    bmsg = msg.encode()
    cmd = ["echo", msg]

    # on windows shell must be true
    shell = bool(is_win)

    source = core.Buffer(core.CommandSource(cmd, shell=shell))

    for _ in range(tries):
        assert bytes(source).strip() == bmsg
