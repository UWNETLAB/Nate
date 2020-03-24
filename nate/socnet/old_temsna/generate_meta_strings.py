import pandas as pd
import pickle

with open('../input/author_metadata.pkl', "rb") as pkl:
    author_dict = pickle.load(pkl)

meta_string_dict = {}

for author in author_dict:

    meta_string = ""
    journals = ""

    try:
        for title in author_dict[author]["title"]:
            meta_string = meta_string + title + " "
    except TypeError:
        pass
    try:
        for keyword in author_dict[author]["keywords"]:
            meta_string = meta_string + keyword + " "
    except TypeError:
        pass
    try:
        for abstract in author_dict[author]["abstract"]:
            meta_string = meta_string + abstract + " "
    except TypeError:
        pass
    try:
        for journal in author_dict[author]["journal"]:
            journals = journals + journal + " "
    except TypeError:
        pass

    meta_string_dict[author] = {
        "meta_string": meta_string,
        "journals": journals,
    }

with open("../output/generated_meta_strings.pkl", "wb") as pkl:
    pickle.dump(meta_string_dict, pkl)
