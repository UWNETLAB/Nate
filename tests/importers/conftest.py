import pytest
import pandas as pd

@pytest.fixture(scope="module")
def df():
    df = pd.read_csv("tests/ira_data/IRAhandle_tweets_1.csv")
    return df
