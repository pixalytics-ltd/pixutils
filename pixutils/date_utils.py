from typing import Union, Iterable
from datetime import datetime, date, timedelta


def first_day_of_prev_month(d: Union[str, date, datetime]) -> datetime:
    """
    Accepts a date and returns the first day of the previous month
    :param d: a date, this can be passed as a string (YYYYMMDD) or using datetime module date or datetime objects
    :return: a date object representing the first day of the previous month
    """
    if isinstance(d, str):
        d = d.replace("-", "")
        d = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]))

    return last_day_of_prev_month(d).replace(day=1)


def last_day_of_prev_month(d: Union[str, date, datetime]) -> datetime:
    """
    Accepts a date and returns the final day of the previous month
    :param d: a date, this can be passed as a string (YYYYMMDD) or using datetime module date or datetime objects
    :return: a date object representing the last day of the previous month
    """
    if isinstance(d, str):
        d = d.replace("-", "")
        d = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]))

    return d.replace(day=1) - timedelta(days=1)


def date_iterator(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> Iterable[date]:
    """
    Yields a list of dates as a daily series between the specified start and end date
    :param start_date: the first date in the sequence
    :param end_date: the last date in the sequence
    :return: a datetime.date object
    """
    _date = start_date
    while _date <= end_date:
        yield _date
        _date += timedelta(days=1)
    return _date
