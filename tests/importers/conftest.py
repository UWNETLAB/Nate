import pytest
import pandas as pd

@pytest.fixture(scope="module")
def df():
    df = pd.read_csv("tests/ira_data/IRAhandle_tweets_1.csv")
    return df

@pytest.fixture(scope="module")
def df11():
    df = pd.read_csv("tests/ira_data/IRAhandle_tweets_11.csv")
    return df

@pytest.fixture(scope="module")
def empty_df(df):
    return pd.DataFrame(columns=df.columns)

@pytest.fixture
def dict_of_dicts_text(df):
    return {df["tweet_id"][i]: {"text": df["content"][i]} for i in range(0,10)}
