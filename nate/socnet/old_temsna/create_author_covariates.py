import pandas as pd
import pickle


alter_list = pd.read_pickle("../input/alter_lists.pkl")
alter_list = alter_list.set_index('author').to_dict()
nodes = pd.read_csv("../input/coauthorship_nodeAttributes.csv")
with open("../input/author_metadata.pkl", "rb") as pkl:
    author_metadata = pickle.load(pkl)


num_citations = {}
num_papers = {}
career_start = {} 
num_alter1 = {}
num_alter2 = {}

for author in author_metadata:
    num_citations[author] = author_metadata[author]["wosTimesCited"] 
    num_papers[author] = author_metadata[author]["num_papers"] = len(author_metadata[author]["wosString"])
    author_metadata[author]["year"] = list(filter(None, author_metadata[author]["year"]))
    try:
        career_start[author] = min([int(i) for i in author_metadata[author]["year"]])
    except ValueError:
        career_start[author] = 2018 
    try:
        num_alter1[author] = len(alter_list['alter'][author])
    except KeyError:
        pass
    try:
        num_alter2[author] = len(alter_list['alter_2'][author])
    except KeyError:
        pass
    


covariates = pd.DataFrame.from_dict(num_citations, orient='index')

covariates['num_citations'] = pd.Series(num_citations)
covariates['num_papers'] = pd.Series(num_papers)
covariates['career_start'] = pd.Series(career_start)
covariates['num_alter1'] = pd.Series(num_alter1)
covariates['num_alter2'] = pd.Series(num_alter2)

covariates = covariates.drop(columns=[0])

covariates.to_csv("../output/node_covariates.csv")