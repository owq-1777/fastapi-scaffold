from datetime import datetime, timedelta
import re


def datestr_to_datetime(datastr, time_format="%Y-%m-%dT%H:%M:%S"):
    return datetime.strptime(datastr, time_format)


def calculate_cutoff_time(retention_period: str) -> datetime:
    """
    Calculate the cutoff time based on a retention period string.
    Retention period string should be in the format of "num unit", e.g. "7 day".
    """

    units = {
        'day': timedelta(days=1),
        'hour': timedelta(hours=1),
        'minute': timedelta(minutes=1),
        'week': timedelta(weeks=1)
    }

    # Parse the retention period string and validate its format
    if not (match := re.match(r'(\d+) (\w+)', retention_period)):
        raise ValueError('Invalid retention period')
    num, unit_name = int(match.group(1)), match.group(2)
    if not (unit := units.get(unit_name)):
        raise ValueError('Invalid retention period')

    # Calculate the cutoff time and return it
    cutoff_time = datetime.now() - num * unit
    return cutoff_time
