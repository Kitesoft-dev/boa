import io
import locale
import sys
import tempfile

import boa.core as core

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


def test_backup_status():
    status_dict = {name: status for name, status in [(s.name, s) for s in core.Status]}

    for key, status in status_dict.items():
        is_expected_failed = True
        if key == "OK":
            is_expected_failed = False

        if is_expected_failed:
            assert status.is_failed()
        else:
            assert not status.is_failed()


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
