from boa.core import BackupStatus, is_status_failed


def test_backup_status():
    backup_status = {
        'OK': BackupStatus.OK,
        'UNAUTHORIZED': BackupStatus.UNAUTHORIZED,
        'TIMEOUT': BackupStatus.TIMEOUT,
        'INTERNAL_ERROR': BackupStatus.INTERNAL_ERROR,
        'FAILED': BackupStatus.FAILED
    }

    for key, status in backup_status.items():
        is_expected_failed = True
        if key == 'OK':
            is_expected_failed = False

        if is_expected_failed:
            assert is_status_failed(status)
        else:
            assert not is_status_failed(status)

