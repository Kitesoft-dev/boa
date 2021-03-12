import boa.core as core
import tempfile
import locale
import io


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

    obj.encoding = ''
    assert core.get_encoding(obj) == default_encoding

    # with set property, returns it
    enc = 'foo'
    obj.encoding = enc
    assert core.get_encoding(obj) == enc


def test_backup_status():
    status_dict = {name: status for name, status in [(s.name, s) for s in core.Status]}

    for key, status in status_dict.items():
        is_expected_failed = True
        if key == 'OK':
            is_expected_failed = False

        if is_expected_failed:
            assert core.is_status_failed(status)
        else:
            assert not core.is_status_failed(status)


def test_source_file():
    msg = 'Hello world!'
    bmsg = msg.encode('utf-8')  # b'Hello world!'

    # Test filestream
    # bytes
    with tempfile.TemporaryFile() as fp:
        fp.write(bmsg)
        fp.seek(0)
        source = core.FileStreamSource(fp)
        assert bytes(source) == bmsg

    # text (str)
    with tempfile.TemporaryFile('w+t') as fp:
        fp.write(msg)
        fp.seek(0)
        source = core.FileStreamSource(fp)
        assert bytes(source) == bmsg

    # Test filepath
    # bytes
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(bmsg)
        fname = fp.name
    source = core.FilePathSource(fname)
    assert bytes(source) == bmsg

    # text (str)
    with tempfile.NamedTemporaryFile('w+t', delete=False) as fp:
        fp.write(msg)
        fname = fp.name
    source = core.FilePathSource(fname)
    assert bytes(source) == bmsg

    # test exausted stream
    stream = io.StringIO('foo')
    stream.read()  # exaust
    source = core.FileStreamSource(stream)
    assert bytes(source) == b''
