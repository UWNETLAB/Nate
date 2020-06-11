from nate.importers.timestamp_process import convert_time, convert_times
import pytest
import pandas as pd

@pytest.fixture
def time_1():
    return "11/12/2019 13:35"

@pytest.fixture
def times_1(df):
    return df["publish_date"][0:3]

def test_convert_time_1(time_1):
    timestamp = convert_time(time_1)
    assert timestamp == 1573565700


def test_convert_times_1(times_1):
    timestamps = convert_times(times_1)
    assert timestamps == [1506887880, 1506897780, 1506898200]
