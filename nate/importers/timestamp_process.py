"""
Process and reformat times for consistency across Nate.
"""
from datetime import datetime, timezone


def convert_times(times, timezone=timezone.utc):
    """Convert all times to POSIX timestamps."""
    timestamps = []

    for time in times:
        dt = datetime.strptime(time, "%m/%d/%Y %H:%M")
        timestamps.append(int(dt.replace(tzinfo=timezone).timestamp()))

    return timestamps


def convert_time(time, timezone=timezone.utc):
    """Convert a single time to POSIX timestamp."""
    dt = datetime.strptime(time, "%m/%d/%Y %H:%M")
    return int(dt.replace(tzinfo=timezone).timestamp())
