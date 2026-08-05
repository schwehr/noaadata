import datetime

from noaadata.cli.find_missing_logs import date_generator


def test_date_generator_standard():
    start = datetime.datetime(2023, 1, 1)
    end = datetime.datetime(2023, 1, 4)
    expected = [
        datetime.datetime(2023, 1, 1),
        datetime.datetime(2023, 1, 2),
        datetime.datetime(2023, 1, 3),
    ]
    assert list(date_generator(start, end)) == expected


def test_date_generator_same_day():
    start = datetime.datetime(2023, 1, 1)
    end = datetime.datetime(2023, 1, 1)
    assert list(date_generator(start, end)) == []


def test_date_generator_end_before_start():
    start = datetime.datetime(2023, 1, 4)
    end = datetime.datetime(2023, 1, 1)
    assert list(date_generator(start, end)) == []
