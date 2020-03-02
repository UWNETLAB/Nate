import pandas as pd
import networkx as nx


def find_alters(tuples):
    network = nx.Graph() 

    pass




edgelist = pd.read_csv("../input/coauthorship_edgeList.csv")
network = nx.from_pandas_edgelist(edgelist, source='From', target='To')

author_dict = {}

authorlist = []

for entry in edgelist["From"]:
    authorlist.append(entry)
for entry in edgelist["To"]:
    authorlist.append(entry)

author_dict = {item: [] for item in list(set(authorlist))}

for author in author_dict:
    alter_list = list(network.neighbors(author))
    alter_2_list = []
    for alter in alter_list:
        alters_2 = list(network.neighbors(alter))
        alter_2_list.extend(alters_2)
    
    alter_list = list(set(alter_list))
    alter_2_list = list(set(alter_2_list))
    

    alter_2_list.remove(author)
    for alter in alter_list:
        if alter in alter_2_list:
            alter_2_list.remove(alter)

    author_dict[author]= [alter_list, alter_2_list]

author_dataframe = pd.DataFrame.from_dict(author_dict, orient='index').reset_index()
author_dataframe.columns = ['author', 'alter', 'alter_2']
author_dataframe.to_pickle("../output/alter_lists.pkl")