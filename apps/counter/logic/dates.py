import calendar
import datetime


def month_end(date: datetime.date) -> datetime.date:
    """
    Returns the last day in a month
    :param date:
    :return:
    """
    wd, last = calendar.monthrange(date.year, date.month)
    return datetime.date(date.year, date.month, last)
