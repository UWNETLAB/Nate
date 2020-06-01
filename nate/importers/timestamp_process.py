"""
Process and reformat times for consistency across Nate.
"""
from datetime import datetime, timezone


def convert_times(times, timezone=timezone.utc):
    """Convert all times to POSIX timestamps, in UTC."""
    timestamps = []

    for time in times:
        dt = datetime.strptime(time, "%m/%d/%Y %H:%M")
        timestamps.append(int(dt.replace(tzinfo=timezone.utc).timestamp()))

    return timestamps


def convert_time(time, timezone=timezone.utc):
    """Convert a single time to POSIX timestamp, in UTC."""
    dt = datetime.strptime(time, "%m/%d/%Y %H:%M")
    return int(dt.replace(tzinfo=timezone.utc).timestamp())
