import nate.importers.dataframe_importers as tst
from nate.importers.timestamp_process import convert_times
import pytest
import pandas as pd

# fixtures for import_csv
@pytest.fixture
def csv_file():
    return "tests/ira_data/IRAhandle_tweets_1.csv"

@pytest.fixture
def csv_files():
    return ["tests/ira_data/IRAhandle_tweets_1.csv",
            "tests/ira_data/IRAhandle_tweets_11.csv"]

# fixtures for import_excel
@pytest.fixture
def excel_file():
    return "tests/ira_data/[..]"

@pytest.fixture
def excel_files():
    return ["tests/ira_data/IRAhandle_tweets_1.xlsx",
            "tests/ira_data/IRAhandle_tweets_11.xlsx"]

# tests for process_dataframe
def test_process_dataframe_empty(empty_df):
    nt = tst.process_dataframe(empty_df, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts() == [] 
    assert nt.list_ids() == []
    assert nt.list_times() == []
    assert nt.list_column("account_category") == []

def test_process_dataframe_full(df):
    nt = tst.process_dataframe(df, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts(0,5) == df["content"][0:5].tolist()
    assert nt.list_ids(0,5) == df["tweet_id"][0:5].tolist()
    assert nt.list_times(0,5) == convert_times(df["publish_date"][0:5].tolist())
    assert nt.list_column("account_category",0,5) == df["account_category"][0:5].tolist()

# tests for import_dataframe (wrapper around process_dataframe)
def test_import_dataframe_empty(empty_df):
    nt = tst.import_dataframe(empty_df, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts() == [] 
    assert nt.list_ids() == []
    assert nt.list_times() == []
    assert nt.list_column("account_category") == []

# tests for import_csv
def test_import_csv_string(csv_file, df):
    nt = tst.import_csv(csv_file, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts(0,5) == df["content"][0:5].tolist()
    assert nt.list_ids(0,5) == df["tweet_id"][0:5].tolist()
    assert nt.list_times(0,5) == convert_times(df["publish_date"][0:5].tolist())
    assert nt.list_column("account_category",0,5) == df["account_category"][0:5].tolist()

def test_import_csv_list(csv_files, df, df11):
    nt = tst.import_csv(csv_files, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts(0,5) == df["content"][0:5].tolist()
    assert nt.list_ids(0,5) == df["tweet_id"][0:5].tolist()
    assert nt.list_times(0,5) == convert_times(df["publish_date"][0:5].tolist())
    assert nt.list_column("account_category",0,5) == df["account_category"][0:5].tolist()
    assert nt.list_texts(243891, 243896) == df11["content"][0:5].tolist()
    assert nt.list_ids(243891, 243896) == df11["tweet_id"][0:5].tolist()
    assert nt.list_times(243891, 243896) == convert_times(df11["publish_date"][0:5].tolist())
    assert nt.list_column("account_category", 243891, 243896) == df11["account_category"][0:5].tolist()

# tests for import_excel
# TODO: add xlsx files. Issues saving them through python.
def test_import_excel_string(excel_file):
    nt = tst.import_excel(excel_file, "content", "tweet_id", "publish_date",
                          columns_to_keep=["account_category"])
    assert nt.list_texts(0,5) == df["content"][0:5].tolist()
    assert nt.list_ids(0,5) == df["tweet_id"][0:5].tolist()
    assert nt.list_times(0,5) == convert_times(df["publish_date"][0:5].tolist())
    assert nt.list_column("account_category",0,5) == df["account_category"][0:5].tolist()

def test_import_excel_strings(excel_files):
    nt = tst.import_excel(excel_files, "content", "tweet_id", "publish_date",
                               columns_to_keep=["account_category"])
    assert nt.list_texts(0,5) == df["content"][0:5].tolist()
    assert nt.list_ids(0,5) == df["tweet_id"][0:5].tolist()
    assert nt.list_times(0,5) == convert_times(df["publish_date"][0:5].tolist())
    assert nt.list_column("account_category",0,5) == df["account_category"][0:5].tolist()
    assert nt.list_texts(243891, 243896) == df11["content"][0:5].tolist()
    assert nt.list_ids(243891, 243896) == df11["tweet_id"][0:5].tolist()
    assert nt.list_times(243891, 243896) == convert_times(df11["publish_date"][0:5].tolist())
    assert nt.list_column("account_category", 243891, 243896) == df11["account_category"][0:5].tolist()
