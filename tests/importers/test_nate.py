import nate.importers.nate_class as tst
from nate.importers.dataframe_importers import import_dataframe
from nate.importers.raw_importers import import_dict_of_dicts
import pytest
from pprint import pformat

@pytest.fixture
def nate_empty_obj(empty_df):
    nt = import_dataframe(empty_df, "content", "tweet_id", "publish_date",
                          columns_to_keep=["account_category"])
    return nt

@pytest.fixture
def nate_full_obj(df):
    nt = import_dataframe(df, "content", "tweet_id", "publish_date",
                          columns_to_keep=["account_category"])
    return nt

@pytest.fixture
def nate_text_only(dict_of_dicts_text):
    return import_dict_of_dicts(dict_of_dicts_text, "text")
    
# test __call__
def test_call_empty(nate_empty_obj, capsys):
    nate_empty_obj()
    captured = capsys.readouterr()
    assert captured.out == "[]\n"

def test_call(nate_full_obj, capsys):
    nate_full_obj()
    captured = capsys.readouterr()
    assert captured.out == pformat(nate_full_obj.data[0:5]) + "\n"

def test_call_nums(nate_full_obj, capsys):
    nate_full_obj(2,9)
    captured = capsys.readouterr()
    assert captured.out == pformat(nate_full_obj.data[2:9]) + "\n"


# test __getitem__
def test_getitem_empty(nate_empty_obj):
    with pytest.raises(IndexError):
        nate_empty_obj[0]

def test_getitem(nate_full_obj):
    assert nate_full_obj[0] == nate_full_obj.data[0]
    assert nate_full_obj[0:5] == nate_full_obj.data[0:5]
    assert nate_full_obj[-1] == nate_full_obj.data[-1]

# test head
def test_head_empty(nate_empty_obj, capsys):
    nate_empty_obj.head()
    captured = capsys.readouterr()
    assert captured.out == "[]\n"

def test_head(nate_full_obj, capsys):
    nate_full_obj.head()
    captured = capsys.readouterr()
    assert captured.out == pformat(nate_full_obj.data[0:5]) + "\n"

def test_head_nums(nate_full_obj, capsys):
    nate_full_obj.head(2,9)
    captured = capsys.readouterr()
    assert captured.out == pformat(nate_full_obj.data[2:9]) + "\n"

# test list_texts
def test_list_texts_empty(nate_empty_obj):
    assert nate_empty_obj.list_texts() == []

def test_list_texts(nate_full_obj):
    text_list = [i.text for i in nate_full_obj.data[0:5]]
    assert nate_full_obj.list_texts() == text_lists

# test list_times
def test_list_times_empty(nate_empty_obj):
    assert nate_empty_obj.list_times() == []

def test_list_times_exn(nate_text_only):
    with pytest.raises(AttributeError):
        nate_text_only.list_times()

def test_list_times(nate_full_obj):
    times_list = [i.time for i in nate_full_obj.data[0:5]]
    assert nate_full_obj.list_times() == times_list

# test list_ids
def test_list_ids_empty(nate_empty_obj):
    assert nate_empty_obj.list_ids() == []

def test_list_ids_exn(nate_text_only):
    with pytest.raises(AttributeError):
        nate_text_only.list_ids()

def test_list_ids(nate_full_obj):
    id_list = [i.id for i in nate_full_obj.data[0:5]]
    assert nate_full_obj.list_ids() == id_list
