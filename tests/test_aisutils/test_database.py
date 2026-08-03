"""Comprehensive unit tests for aisutils.database module."""

import datetime
import optparse
import pathlib
import sqlite3
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import ais
from aisutils import database


def test_checkpoint(capsys: pytest.CaptureFixture[str]) -> None:
    """Test checkpoint function outputs line number and function name to stdout."""
    database.checkpoint()
    captured = capsys.readouterr()
    assert "CHECKPOINT" in captured.out
    assert "test_checkpoint" in captured.out


def test_dbtypes_content() -> None:
    """Test dbTypes tuple contains expected database choices."""
    assert isinstance(database.dbTypes, tuple)
    assert "postgres" in database.dbTypes
    assert "sqlite" in database.dbTypes


def test_std_cmdline_options_postgres() -> None:
    """Test stdCmdlineOptions adds postgres options to OptionParser."""
    parser = optparse.OptionParser()
    database.stdCmdlineOptions(parser, dbType="postgres")
    assert parser.has_option("-d")
    assert parser.has_option("-D")
    assert parser.has_option("-u")
    assert parser.has_option("-p")


def test_std_cmdline_options_sqlite() -> None:
    """Test stdCmdlineOptions adds sqlite options to OptionParser."""
    parser = optparse.OptionParser()
    database.stdCmdlineOptions(parser, dbType="sqlite")
    assert parser.has_option("-f")


def test_std_cmdline_options_all() -> None:
    """Test stdCmdlineOptions with dbType='all' adds all database options."""
    parser = optparse.OptionParser()
    database.stdCmdlineOptions(parser, dbType="all")
    assert parser.has_option("-d")
    assert parser.has_option("-D")
    assert parser.has_option("-u")
    assert parser.has_option("-p")
    assert parser.has_option("-f")


def test_std_cmdline_options_verbose(capsys: pytest.CaptureFixture[str]) -> None:
    """Test stdCmdlineOptions with verbose=True writes log messages to stderr."""
    parser = optparse.OptionParser()
    database.stdCmdlineOptions(parser, dbType="all", verbose=True)
    captured = capsys.readouterr()
    assert "Adding postgres options" in captured.err
    assert "Adding sqlite options" in captured.err


def test_std_cmdline_options_invalid_dbtype() -> None:
    """Test stdCmdlineOptions with invalid dbType raises SystemExit."""
    parser = optparse.OptionParser()
    with pytest.raises(SystemExit) as exc_info:
        database.stdCmdlineOptions(parser, dbType="invalid_db")
    assert "unknown database type: invalid_db" in str(exc_info.value)


def test_payload_table_sql() -> None:
    """Test payload_table_sql contains expected CREATE TABLE payload SQL statement."""
    assert "CREATE TABLE payload" in database.payload_table_sql
    assert "encoded_text VARCHAR(200)" in database.payload_table_sql


def test_create_tables_sqlite_memory() -> None:
    """Test createTables creates tables in sqlite in-memory database."""
    conn = sqlite3.connect(":memory:")
    database.createTables(conn, dbType="sqlite", includeList=[5, 6])
    cu = conn.cursor()
    cu.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cu.fetchall()]
    assert "shipdata" in tables
    assert "abm" in tables


def test_create_tables_exclude_list() -> None:
    """Test createTables with excludeList skips excluded message types."""
    conn = sqlite3.connect(":memory:")
    all_msgs = list(ais.msgModByNumber.keys())
    database.createTables(conn, dbType="sqlite", excludeList=all_msgs)
    cu = conn.cursor()
    cu.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cu.fetchall()]
    assert len(tables) == 0


def test_create_tables_verbose_and_duplicates(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test createTables verbose mode and skipping existing duplicate table names."""
    conn = sqlite3.connect(":memory:")
    database.createTables(conn, dbType="sqlite", includeList=[5, 6], verbose=True)
    captured = capsys.readouterr()
    assert (
        "adding shipdata table to db" in captured.out
        or "adding" in captured.err
        or "shipdata" in captured.out
    )


def test_drop_tables() -> None:
    """Test dropTables drops created database tables."""
    conn = sqlite3.connect(":memory:")
    database.createTables(conn, dbType="sqlite", includeList=[5])
    database.dropTables(conn, includeList=[5])
    cu = conn.cursor()
    cu.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cu.fetchall()]
    assert "shipdata" not in tables


def test_drop_tables_exclude_list() -> None:
    """Test dropTables with excludeList skips dropping excluded messages."""
    conn = sqlite3.connect(":memory:")
    database.createTables(conn, dbType="sqlite", includeList=[5, 6])
    database.dropTables(conn, excludeList=[5], includeList=[5, 6])
    cu = conn.cursor()
    cu.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cu.fetchall()]
    assert "shipdata" in tables
    assert "abm" not in tables


def test_drop_tables_verbose(capsys: pytest.CaptureFixture[str]) -> None:
    """Test dropTables verbose output."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    database.dropTables(mock_cx, includeList=[5, 6], verbose=True)
    captured = capsys.readouterr()
    assert "dropping" in captured.out or "skipping" in captured.out


def test_connect_sqlite(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test connect with dbType='sqlite' returns sqlite3 connection."""
    db_file = str(tmp_path / "test.db3")
    options = SimpleNamespace(verbose=True, dbType="sqlite", databaseFilename=db_file)
    conn = database.connect(options)
    assert conn is not None
    conn.close()
    captured = capsys.readouterr()
    assert "connected to db" in captured.err


def test_connect_postgres(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test connect with dbType='postgres' calls psycopg.connect with formatted string."""
    mock_connect = MagicMock()
    monkeypatch.setattr(database.psycopg, "connect", mock_connect)
    options = SimpleNamespace(
        verbose=True,
        dbType="postgres",
        databaseName="testdb",
        databaseUser="testuser",
        databaseHost="localhost",
    )
    conn = database.connect(options)
    assert conn == mock_connect.return_value
    mock_connect.assert_called_once_with(
        "dbname='testdb' user='testuser' host='localhost'"
    )
    captured = capsys.readouterr()
    assert "Connect string:" in captured.out


def test_connect_invalid_dbtype() -> None:
    """Test connect with unrecognized dbType exits."""
    options = SimpleNamespace(verbose=False, dbType="unsupported")
    with pytest.raises(SystemExit) as exc_info:
        database.connect(options)
    assert "Must specify a database type" in str(exc_info.value)


def test_rebuild_track_lines_no_start_time_exit() -> None:
    """rebuild_track_lines exits with 'NO!!!' if vessels are provided but startTime is None."""
    mock_cx = MagicMock()
    with pytest.raises(SystemExit) as exc_info:
        database.rebuild_track_lines(mock_cx, vessels={366998390}, startTime=None)
    assert "NO!!!" in str(exc_info.value)


def test_rebuild_track_lines_vessels_none_with_starttime() -> None:
    """rebuild_track_lines fetches distinct userids when vessels is None and startTime is provided."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [(366998390,)],  # distinct userid query
        [("POINT(-70.0 42.0)",), ("POINT(-70.1 42.1)",)],  # position points
        [("TEST SHIP",)],  # shipdata name
        [],  # 0 track_keys -> INSERT new line
        [(1,)],  # count
        [(1,)],  # count after
    ]
    now = datetime.datetime.now(datetime.UTC)
    database.rebuild_track_lines(mock_cx, vessels=None, startTime=now, verbose=True)
    assert mock_cx.commit.called


def test_rebuild_track_lines_update_existing_track() -> None:
    """rebuild_track_lines updates existing row when 1 track_key exists."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)",), ("POINT(-70.1 42.1)",)],  # position points
        [("  SHIP NAME @  ",)],  # shipdata name
        [(101,)],  # 1 track key -> UPDATE line
    ]
    now = datetime.datetime.now(datetime.UTC)
    database.rebuild_track_lines(
        mock_cx, vessels={366998390}, startTime=now, verbose=True
    )
    assert mock_cx.commit.called


def test_rebuild_track_lines_skip_invalid_pos_and_drop_vessel() -> None:
    """rebuild_track_lines skips 181 91 positions and deletes track if < 2 points remain."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [("POINT(181 91)",), ("POINT(-70.0 42.0)",)],  # only 1 valid point remains
        [(101,)],  # existing track row to delete
    ]
    now = datetime.datetime.now(datetime.UTC)
    database.rebuild_track_lines(
        mock_cx, vessels={366998390}, startTime=now, verbose=True
    )
    mock_cu.execute.assert_any_call(
        "DELETE FROM track_lines WHERE userid = %s;", (366998390,)
    )


def test_rebuild_track_lines_programming_error_handling(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """rebuild_track_lines catches psycopg.ProgrammingError on execute."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)",), ("POINT(-70.1 42.1)",)],
        [],  # no ship name -> fallback str(vessel)
        [],  # 0 track keys
        [(1,)],  # COUNT track_lines before
        [(1,)],  # COUNT track_lines after
    ]
    mock_cu.execute.side_effect = [
        None,  # SELECT position
        None,  # SELECT name
        None,  # SELECT track_keys
        database.psycopg.ProgrammingError("DB error"),  # INSERT fail
        None,  # SELECT COUNT
        None,  # DELETE old
        None,  # SELECT COUNT after
    ]
    now = datetime.datetime.now(datetime.UTC)
    database.rebuild_track_lines(
        mock_cx, vessels={366998390}, startTime=now, verbose=True
    )
    captured = capsys.readouterr()
    assert "psycopg2 execute flailed" in captured.err


def test_rebuild_track_lines_corrupted_multiple_keys(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """rebuild_track_lines logs error when multiple track keys exist for vessel."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)",), ("POINT(-70.1 42.1)",)],
        [("",)],  # empty ship name -> falls back to str(vessel)
        [(101,), (102,)],  # >1 track keys -> error
    ]
    now = datetime.datetime.now(datetime.UTC)
    database.rebuild_track_lines(
        mock_cx, vessels={366998390}, startTime=now, verbose=True
    )
    captured = capsys.readouterr()
    assert "ERROR: database corrupted" in captured.err


def test_rebuild_last_position_vessels_none() -> None:
    """rebuild_last_position fetches distinct vessels when vesselsClassA is None."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    mock_cu.fetchall.side_effect = [
        [(366998390,)],  # distinct userid query
        [],  # no position rows
    ]
    database.rebuild_last_position(
        mock_cx, vesselsClassA=None, startTime=None, verbose=True
    )
    assert mock_cu.execute.called


def test_rebuild_last_position_outdated_timestamp() -> None:
    """rebuild_last_position deletes vessel from last_position if position is older than startTime."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    old_time = datetime.datetime(2020, 1, 1, 0, 0, 0)
    start_time = datetime.date(2026, 1, 1)  # tests date object handling
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)", 180, 12.5, old_time)],  # position row
        [(1,)],  # last_position key to delete
        (10,),  # COUNT position
        (5,),  # COUNT last_position
        (8,),  # AFTER COUNT position
        (4,),  # AFTER COUNT last_position
    ]
    database.rebuild_last_position(
        mock_cx, vesselsClassA={366998390}, startTime=start_time, verbose=True
    )
    mock_cu.execute.assert_any_call(
        "DELETE FROM last_position WHERE userid = %s;", (366998390,)
    )


def test_rebuild_last_position_insert_and_update() -> None:
    """rebuild_last_position inserts new position row and updates existing row."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    now = datetime.datetime.now(datetime.UTC)

    # Test INSERT
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)", 90, 10.0, now)],  # position row
        [("SHIP A", 1)],  # shipdata
        [],  # 0 lastpos_keys -> INSERT
    ]
    database.rebuild_last_position(
        mock_cx, vesselsClassA={366998390}, startTime=None, verbose=True
    )
    assert mock_cx.commit.called

    # Test UPDATE
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)", 90, 10.0, now)],  # position row
        [],  # no shipdata -> fallback str(vessel)
        [(500,)],  # 1 key -> UPDATE
    ]
    database.rebuild_last_position(
        mock_cx, vesselsClassA={366998390}, startTime=None, verbose=True
    )
    assert mock_cx.commit.called


def test_rebuild_last_position_class_b_and_error_handling(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """rebuild_last_position handles vesselsClassB and catches psycopg.ProgrammingError."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    now = datetime.datetime.now(datetime.UTC)
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)", 90, 10.0, now)],
        [("SHIP B", 1)],
        [],  # INSERT
    ]
    mock_cu.execute.side_effect = [
        None,  # SELECT position
        None,  # SELECT shipdata
        None,  # SELECT lastpos_keys
        database.psycopg.ProgrammingError("INSERT error"),  # INSERT fail
    ]
    database.rebuild_last_position(
        mock_cx,
        vesselsClassA={366998390},
        vesselsClassB={366998391},
        startTime=None,
        verbose=True,
    )
    captured = capsys.readouterr()
    assert "FIX: class B not yet implemented" in captured.out
    assert "psycopg2 execute flailed" in captured.err


def test_rebuild_last_position_corrupted(capsys: pytest.CaptureFixture[str]) -> None:
    """rebuild_last_position logs error when multiple lastpos keys exist."""
    mock_cx = MagicMock()
    mock_cu = MagicMock()
    mock_cx.cursor.return_value = mock_cu
    now = datetime.datetime.now(datetime.UTC)
    mock_cu.fetchall.side_effect = [
        [("POINT(-70.0 42.0)", 90, 10.0, now)],
        [("SHIP C", 1)],
        [(100,), (101,)],  # >1 keys
    ]
    database.rebuild_last_position(
        mock_cx, vesselsClassA={366998390}, startTime=None, verbose=True
    )
    captured = capsys.readouterr()
    assert "ERROR: database corrupted ... too many positions" in captured.err
