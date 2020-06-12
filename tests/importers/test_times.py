import nate.importers.timestamp_process  as tst
import pytest
import pandas as pd
from datetime import timezone, timedelta

# fixtures to test convert_time
@pytest.fixture
def time_0():
    return "1/1/1970 00:00"

@pytest.fixture
def time_1():
    return "11/12/2019 13:35"


# fixtures to test convert_times
@pytest.fixture
def times_empty():
    return []

@pytest.fixture
def times_0():
    return ["1/1/1970 00:00", "1/1/1970 00:02", "1/1/1970 01:01"]

@pytest.fixture
def times_1(df):
    return df["publish_date"][0:3]

# tests for convert_time
def test_convert_time_0(time_0):
    assert tst.convert_time(time_0) == 0

def test_convert_time_1(time_1):
    assert tst.convert_time(time_1) == 1573565700

def test_convert_time_timezone(time_0):
    assert tst.convert_time(time_0, timezone(timedelta(hours=-3))) == 10800

# tests for convert_times
def test_convert_times_empty(times_empty):
    assert tst.convert_times(times_empty) == []
    
def test_convert_times_0(times_0):
    assert tst.convert_times(times_0) == [0,120,3660]
    
def test_convert_times_1(times_1):
    assert tst.convert_times(times_1) == [1506887880, 1506897780, 1506898200]

def test_convert_times_timezone(times_0):
    assert tst.convert_times(times_0,
                         timezone(timedelta(hours=-3))) == [0+10800, 120+10800, 3660+10800]
