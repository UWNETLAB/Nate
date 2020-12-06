import nate.importers.named_tuple_generator as tst
from collections import namedtuple
import pytest

# fixtures for create_observation_list
@pytest.fixture
def list_of_lists():
    return [["January", "February", "March"],
            [1, 2, 3],
            ["JA", "FE", "MR"]]

@pytest.fixture
def created_obs_list(list_of_lists):
    return tst.create_observation_list("Month", name=list_of_lists[0],
                                       number=list_of_lists[1],
                                       abbr=list_of_lists[2])
@pytest.fixture
def uneven_list_of_lists():
    return [["January", "February", "March", "April"],
            [1, 2],
            ["JA", "FE", "MR"]]

# fixtures for tupleize
@pytest.fixture
def series_dict(list_of_lists):
    return {"name":list_of_lists[0], "number":list_of_lists[1], "abbr":list_of_lists[2]}

@pytest.fixture
def series_dict_tuple(series_dict):
    return {k: tuple(v) for k, v in series_dict.items()}

# tests for create_observation_list
def test_create_observation_list_names(created_obs_list):
    assert created_obs_list[0]._fields == ("name", "number", "abbr")
    assert created_obs_list[0].name == "January"

def test_create_observation_list_contents(created_obs_list):
    assert created_obs_list == [("January", 1, "JA"),
                                ("February", 2, "FE"),
                                ("March", 3, "MR")]

def test_create_observation_list_exn(uneven_list_of_lists):
    try:
        tst.create_observation_list("Month", name=uneven_list_of_lists[0],
                                       number=uneven_list_of_lists[1],
                                       abbr=uneven_list_of_lists[2])
    except Exception as exn:
        assert exn.args[0] == "Not all of the input data is the same length."


# tests for tupleize
def test_tupleize_names(series_dict):
    obs_list = tst.tupleize(series_dict)
    assert obs_list[0]._fields == ("name", "number", "abbr")
    assert obs_list[0].name == "January"

def test_tupleize_lists(series_dict):
    obs_list = tst.tupleize(series_dict)
    assert obs_list[1].name == "February"
    assert obs_list == [("January", 1, "JA"),
                        ("February", 2, "FE"),
                        ("March", 3, "MR")]

def test_tupleize_tuples(series_dict_tuple):
    obs_list = tst.tupleize(series_dict_tuple)
    assert obs_list[1].name == "February"
    assert obs_list == [("January", 1, "JA"),
                        ("February", 2, "FE"),
                        ("March", 3, "MR")]
