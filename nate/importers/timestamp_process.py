import pickle
from datetime import datetime, timezone
  
 
def convert_times(times, timezone = timezone.utc):
    """
    This is a docstring
    """ 
    timestamps = []

    for time in times:
        dt = datetime.strptime(time, "%m/%d/%Y %H:%M")
        timestamps.append(int(dt.replace(tzinfo=timezone.utc).timestamp()))

    return timestamps