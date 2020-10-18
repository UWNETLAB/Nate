"""
This is a MODULE docstring
"""

import pandas as pd
import networkx as nx
from collections import namedtuple

alter_tuple = namedtuple('alters', ['vertex', 'betweenness', 'closeness', 'eigenvector'])


def find_alters(edgelist) -> dict:
    G = nx.Graph()

    G = nx.from_pandas_edgelist(pd.DataFrame(edgelist, columns = ['From', 'To']), source='From', target='To')

    authorlist = [entry.From for entry in edgelist]
    authorlist.extend([entry.To for entry in edgelist])
    author_dict = {item: [] for item in set(authorlist)}

    for author in author_dict:
        alter_list = list(G.neighbors(author))
        alter_2_list = []
        for alter in alter_list:
            alters_2 = list(G.neighbors(alter))
            alter_2_list.extend(alters_2)

        alter_list = list(set(alter_list))
        alter_2_list = list(set(alter_2_list))

        alter_2_list.remove(author)
        for alter in alter_list:
            if alter in alter_2_list:
                alter_2_list.remove(alter)

        author_dict[author] = [alter_list, alter_2_list]

    return author_dict
