from nate.importers.nate_class import Nate
import nate.importers.raw_importers as tst
import pytest

# fixtures for import_text
@pytest.fixture
def string():
    return "Nate is a cool package!"

@pytest.fixture
def list_of_strings(df):
    return df["content"][0:10].values.tolist()

# fixtures for import_files
@pytest.fixture
def file():
    return "tests/importers/textfiles/1.txt"

@pytest.fixture
def list_of_files():
    return ["tests/importers/textfiles/1.txt",
            "tests/importers/textfiles/2.txt",
            "tests/importers/textfiles/3.txt"]

# fixtures for import_dict_of_dicts

# see contest.py for dict_of_dicts_text

@pytest.fixture
def dict_of_dicts_cols(df):
    return {df["tweet_id"][i]: {"text": df["content"][i],
                                "account": df.author[i]} for i in range(0,10)}

# test import_texts
def test_import_text_string(string):
    nt = tst.import_text(string)
    assert nt.list_texts() == [string]

def test_import_text_strings(list_of_strings):
    nt = tst.import_text(list_of_strings)
    assert nt.list_texts() == list_of_strings

# test import_files
def test_import_files_single(file):
    nt = tst.import_files(file)
    with open(file, 'r') as stream:
        string = stream.read().replace("\n", " ")
    assert nt.list_texts() == [string]

def test_import_files_list(list_of_files):
    nt = tst.import_files(list_of_files)

    strings = []
    for file in list_of_files:
        with open(file, 'r') as stream:
            strings.append(stream.read().replace("\n", " "))

    assert nt.list_texts() == strings

# test import_dict_of_dicts
def test_dict_of_dicts_texts(dict_of_dicts_text):
    nt = tst.import_dict_of_dicts(dict_of_dicts_text, "text")
    ids = nt.list_ids()
    texts = nt.list_texts()
    for i in range(0,10):
        assert texts[i] == dict_of_dicts_text[ids[i]]["text"]


def test_dict_of_dicts_cols(dict_of_dicts_cols):
    nt = tst.import_dict_of_dicts(dict_of_dicts_cols, "text", values_to_keep=["account"])
    ids = nt.list_ids()
    texts = nt.list_texts()
    accounts = nt.list_column("account", end=10)
    for i in range(0,10):
        assert texts[i] == dict_of_dicts_cols[ids[i]]["text"]
        assert accounts[i] == dict_of_dicts_cols[ids[i]]["account"]
