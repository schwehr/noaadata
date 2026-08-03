"""Comprehensive unit tests for aisutils.server module."""

import datetime
import os
import resource
import time
from unittest.mock import MagicMock, call, patch

import pytest
from aisutils import server
from aisutils.server import LogFileWithRotate, SERIAL_SPEEDS, create_daemon


# -----------------------------------------------------------------------------
# Tests for SERIAL_SPEEDS constant
# -----------------------------------------------------------------------------


def test_serial_speeds_constant() -> None:
    """Verify SERIAL_SPEEDS contains expected baud rate integer values."""
    assert isinstance(SERIAL_SPEEDS, list)
    assert len(SERIAL_SPEEDS) > 0
    expected_speeds = [
        300,
        600,
        1200,
        1800,
        2400,
        4800,
        9600,
        19200,
        38400,
        57600,
        115200,
        230400,
    ]
    assert SERIAL_SPEEDS == expected_speeds
    for speed in SERIAL_SPEEDS:
        assert isinstance(speed, int)
        assert speed > 0


# -----------------------------------------------------------------------------
# Tests for create_daemon function
# -----------------------------------------------------------------------------


@patch("os.dup2")
@patch("os.open")
@patch("os.close")
@patch("resource.getrlimit")
@patch("os.setsid")
@patch("os.fork")
def test_create_daemon_success_child(
    mock_fork: MagicMock,
    mock_setsid: MagicMock,
    mock_getrlimit: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_dup2: MagicMock,
) -> None:
    """Test create_daemon executing fully in the grandchild process."""
    mock_fork.side_effect = [0, 0]  # First child, then second child
    mock_getrlimit.return_value = (1024, 1024)
    mock_open.return_value = 0

    server.create_daemon()

    assert mock_fork.call_count == 2
    mock_setsid.assert_called_once()
    mock_getrlimit.assert_called_once_with(resource.RLIMIT_NOFILE)
    assert mock_close.call_count == 1024
    mock_open.assert_called_once_with("/dev/null", os.O_RDWR)
    assert mock_dup2.call_args_list == [call(0, 1), call(0, 2)]


@patch("os._exit")
@patch("os.fork")
def test_create_daemon_first_parent_exit(
    mock_fork: MagicMock, mock_exit: MagicMock
) -> None:
    """Test create_daemon exiting immediately in the initial parent process."""
    mock_fork.return_value = 1234  # Non-zero PID for first parent
    mock_exit.side_effect = SystemExit(0)

    with pytest.raises(SystemExit) as exc_info:
        server.create_daemon()

    assert exc_info.value.code == 0
    mock_fork.assert_called_once()
    mock_exit.assert_called_once_with(0)


@patch("os._exit")
@patch("os.setsid")
@patch("os.fork")
def test_create_daemon_second_parent_exit(
    mock_fork: MagicMock, mock_setsid: MagicMock, mock_exit: MagicMock
) -> None:
    """Test create_daemon exiting in the intermediate (first child) parent process."""
    mock_fork.side_effect = [0, 5678]  # First child (0), then second parent (5678)
    mock_exit.side_effect = SystemExit(0)

    with pytest.raises(SystemExit) as exc_info:
        server.create_daemon()

    assert exc_info.value.code == 0
    assert mock_fork.call_count == 2
    mock_setsid.assert_called_once()
    mock_exit.assert_called_once_with(0)


@patch("os.fork")
def test_create_daemon_first_fork_oserror(mock_fork: MagicMock) -> None:
    """Test create_daemon handling OSError during first os.fork call."""
    err = OSError(13, "Permission denied")
    mock_fork.side_effect = err

    with pytest.raises(Exception) as exc_info:
        server.create_daemon()

    assert "Permission denied [13]" in str(exc_info.value)


@patch("os.setsid")
@patch("os.fork")
def test_create_daemon_second_fork_oserror(
    mock_fork: MagicMock, mock_setsid: MagicMock
) -> None:
    """Test create_daemon handling OSError during second os.fork call."""
    err = OSError(2, "No such file or directory")
    mock_fork.side_effect = [0, err]

    with pytest.raises(Exception) as exc_info:
        server.create_daemon()

    mock_setsid.assert_called_once()
    assert "No such file or directory [2]" in str(exc_info.value)


@patch("os.dup2")
@patch("os.open")
@patch("os.close")
@patch("resource.getrlimit")
@patch("os.setsid")
@patch("os.fork")
def test_create_daemon_rlim_infinity(
    mock_fork: MagicMock,
    mock_setsid: MagicMock,
    mock_getrlimit: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_dup2: MagicMock,
) -> None:
    """Test create_daemon fallback when maxfd is RLIM_INFINITY."""
    mock_fork.side_effect = [0, 0]
    mock_getrlimit.return_value = (1024, resource.RLIM_INFINITY)
    mock_open.return_value = 0

    server.create_daemon()

    assert mock_close.call_count == 1024


@patch("os.dup2")
@patch("os.open")
@patch("os.close")
@patch("resource.getrlimit")
@patch("os.setsid")
@patch("os.fork")
def test_create_daemon_ignore_close_oserror(
    mock_fork: MagicMock,
    mock_setsid: MagicMock,
    mock_getrlimit: MagicMock,
    mock_close: MagicMock,
    mock_open: MagicMock,
    mock_dup2: MagicMock,
) -> None:
    """Test create_daemon ignoring OSError when attempting to close unopened file descriptors."""
    mock_fork.side_effect = [0, 0]
    mock_getrlimit.return_value = (10, 10)
    mock_close.side_effect = OSError("Bad file descriptor")
    mock_open.return_value = 0

    server.create_daemon()

    assert mock_close.call_count == 10


# -----------------------------------------------------------------------------
# Tests for LogFileWithRotate class
# -----------------------------------------------------------------------------


def test_logfile_init_default(tmp_path: pytest.TempPathFactory) -> None:
    """Test LogFileWithRotate initialization with default arguments."""
    prefix = str(tmp_path / "log-")
    logger = LogFileWithRotate(prefix=prefix)

    assert logger.prefix == prefix
    assert logger.station == "runknown"
    assert logger.uscg_format is True
    assert logger.v is False
    assert logger.log_file is not None
    assert not logger.log_file.closed

    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    assert logger.log_filename == f"{prefix}{today_str}"
    assert os.path.exists(logger.log_filename)

    logger.log_file.flush()
    with open(logger.log_filename, "r") as f:
        content = f.read()
    assert "# START LOGGING" in content

    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_init_custom(tmp_path: pytest.TempPathFactory) -> None:
    """Test LogFileWithRotate initialization with custom arguments."""
    prefix = str(tmp_path / "custom_log_")
    logger = LogFileWithRotate(
        prefix=prefix, station="STATION_01", uscg_format=False, verbose=True
    )

    assert logger.prefix == prefix
    assert logger.station == "STATION_01"
    assert logger.uscg_format is False
    assert logger.v is True

    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


@patch("time.time")
def test_logfile_write_uscg_format(
    mock_time: MagicMock, tmp_path: pytest.TempPathFactory
) -> None:
    """Test write method using USCG format with timestamp and station suffix."""
    mock_time.return_value = 1700000000.0
    prefix = str(tmp_path / "uscg_log_")
    logger = LogFileWithRotate(
        prefix=prefix, station="BOS", uscg_format=True, verbose=False
    )

    logger.write("!AIVDM,1,1,,A,13u?&00P0000000,0*00\n", rotate=False)
    logger.write_tail()
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()

    with open(logger.log_filename, "r") as f:
        lines = f.readlines()

    assert len(lines) == 3
    assert lines[0] == "# START LOGGING,BOS,1700000000.0\n"
    assert lines[1] == "!AIVDM,1,1,,A,13u?&00P0000000,0*00,BOS,1700000000.0\n"
    assert lines[2] == "# STOP LOGGING,BOS,1700000000.0\n"


@patch("time.time")
def test_logfile_write_uscg_format_carriage_return(
    mock_time: MagicMock, tmp_path: pytest.TempPathFactory
) -> None:
    """Test write method in USCG format strips carriage return before appending tags."""
    mock_time.return_value = 1700000000.0
    prefix = str(tmp_path / "uscg_cr_log_")
    logger = LogFileWithRotate(
        prefix=prefix, station="NYC", uscg_format=True, verbose=False
    )

    logger.write("!AIVDM,1,1,,A,13u?&00P0000000,0*00\r", rotate=False)
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()

    with open(logger.log_filename, "r") as f:
        lines = f.readlines()

    assert lines[1] == "!AIVDM,1,1,,A,13u?&00P0000000,0*00,NYC,1700000000.0\n"


def test_logfile_write_non_uscg_format(tmp_path: pytest.TempPathFactory) -> None:
    """Test write method without USCG format."""
    prefix = str(tmp_path / "raw_log_")
    logger = LogFileWithRotate(prefix=prefix, uscg_format=False, verbose=False)

    logger.write("Sample raw line", rotate=False)
    logger.write("\n", rotate=False)
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()

    with open(logger.log_filename, "r") as f:
        lines = f.readlines()

    assert lines[1] == "Sample raw line\n"
    assert lines[2] == "\n"


def test_logfile_write_verbose(
    capsys: pytest.CaptureFixture[str], tmp_path: pytest.TempPathFactory
) -> None:
    """Test write method with verbose printing enabled."""
    prefix = str(tmp_path / "verbose_log_")
    logger = LogFileWithRotate(prefix=prefix, uscg_format=False, verbose=False)

    logger.write("Verbose line", verbose=True, rotate=False)
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()

    captured = capsys.readouterr()
    assert "Verbose line\n" in captured.out


def test_logfile_needs_rotate(tmp_path: pytest.TempPathFactory) -> None:
    """Test needs_rotate returns False for same day and True when current_date day differs."""
    prefix = str(tmp_path / "rotate_check_")
    logger = LogFileWithRotate(prefix=prefix)

    assert logger.needs_rotate() is False

    # Simulate log opened yesterday
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    logger.current_date = yesterday
    assert logger.needs_rotate() is True

    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_rotate_forced(tmp_path: pytest.TempPathFactory) -> None:
    """Test rotate with force=True closes current file and opens new log file."""
    prefix = str(tmp_path / "force_rotate_")
    logger = LogFileWithRotate(prefix=prefix, verbose=True)
    first_filename = logger.log_filename

    logger.rotate(force=True)

    with open(first_filename, "r") as f:
        content = f.read()

    assert "# STOP LOGGING" in content
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_rotate_when_needed(tmp_path: pytest.TempPathFactory) -> None:
    """Test rotate automatically triggers during write when date changes."""
    prefix = str(tmp_path / "auto_rotate_")
    logger = LogFileWithRotate(prefix=prefix, uscg_format=False)

    logger.current_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    logger.write("Line after day change", rotate=True)

    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_rotate_not_needed(tmp_path: pytest.TempPathFactory) -> None:
    """Test rotate does nothing when force=False and date has not changed."""
    prefix = str(tmp_path / "no_rotate_")
    logger = LogFileWithRotate(prefix=prefix)
    log_file_before = logger.log_file

    logger.rotate(force=False)
    assert logger.log_file is log_file_before

    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_open_closes_previous(tmp_path: pytest.TempPathFactory) -> None:
    """Test calling open() explicitly closes existing open log file with tail."""
    prefix = str(tmp_path / "reopen_")
    logger = LogFileWithRotate(prefix=prefix, verbose=True)
    first_filename = logger.log_filename

    logger.open()

    with open(first_filename, "r") as f:
        content = f.read()

    assert "# STOP LOGGING" in content
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()


def test_logfile_del_safety() -> None:
    """Test __del__ handles cases where log_file is None or already closed without exception."""
    logger = LogFileWithRotate.__new__(LogFileWithRotate)
    logger.log_file = None
    # Should not raise exception
    if logger.log_file and not logger.log_file.closed:
        logger.log_file.close()
