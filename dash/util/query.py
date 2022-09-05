from datetime import datetime, timedelta

from config import INDEX_NAME
from dash.util import elastic

import re


def get_available_index_date():
    index_pattern = INDEX_NAME + '-([\d.]+)'

    dates = []
    for index in elastic.get_available_index():
        date_string = re.search(index_pattern, index).group(1)
        dates.append(datetime.strptime(date_string, "%Y.%m.%d"))
    dates.sort(reverse=True)
    return dates


def get_queryable_date(start_time=None, end_time=None):
    possible_dates = [
        (start_time + timedelta(days=x)).replace(hour=0, minute=0, second=0, microsecond=0)
        for x in range(0, (end_time - start_time + timedelta(days=1)).days)
    ]
    index_dates = get_available_index_date()

    for date in possible_dates:
        if date not in index_dates:
            possible_dates.remove(date)

    possible_dates.sort(reverse=True)
    return possible_dates


def get_queryable_indices(start_time=None, end_time=None):
    dates_string = []
    for date in get_queryable_date(start_time=start_time, end_time=end_time):
        dates_string.append(date.strftime("logging-%Y.%m.%d"))
    return dates_string