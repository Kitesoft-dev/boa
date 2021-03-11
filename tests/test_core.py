import boa.core as core
import tempfile


def test_backup_status():
    backup_status = {
        'OK': core.Status.OK,
        'UNAUTHORIZED': core.Status.UNAUTHORIZED,
        'TIMEOUT': core.Status.TIMEOUT,
        'INTERNAL_ERROR': core.Status.INTERNAL_ERROR,
        'USER_ERROR': core.Status.USER_ERROR,
        'FAILED': core.Status.FAILED,
    }

    for key, status in backup_status.items():
        is_expected_failed = True
        if key == 'OK':
            is_expected_failed = False

        if is_expected_failed:
            assert core.is_status_failed(status)
        else:
            assert not core.is_status_failed(status)


def test_file():
    msg = 'Hello world!'
    bmsg = msg.encode('utf-8')  # b'Hello world!'

    # Test filestream
    # bytes
    with tempfile.TemporaryFile() as fp:
        fp.write(bmsg)
        fp.seek(0)
        backuppable = core.FileStream(fp)
        assert bytes(backuppable) == bmsg

    # text (str)
    with tempfile.TemporaryFile('w+t') as fp:
        fp.write(msg)
        fp.seek(0)
        backuppable = core.FileStream(fp)
        assert bytes(backuppable) == bmsg

    # Test filepath
    # bytes
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(bmsg)
        fname = fp.name
    backuppable = core.FilePath(fname)
    assert bytes(backuppable) == bmsg

    # text (str)
    with tempfile.NamedTemporaryFile('w+t', delete=False) as fp:
        fp.write(msg)
        fname = fp.name
    backuppable = core.FilePath(fname)
    assert bytes(backuppable) == bmsg
