import pandas as pd
import metaknowledge as mk
import networkx as nx
import pickle

node_covariates = pd.read_csv("../input/node_covariates.csv")
sim_scores = pd.read_csv("../input/sim_scores.csv")
centralities = pd.read_csv("../input/centralities.csv")

node_covariates.rename(columns={'Unnamed: 0': 'author'}, inplace=True)

node_covariates.head()

sim_scores.head()

sim_scores = sim_scores.merge(node_covariates, left_on="author", right_on="author")

sim_scores.columns = ["author", "dissim_alters", "dissim_alters_2", "alter_dissim_avg", "bridge_dissim_avg", "first_ring_dissim_avg", "num_citations", "num_papers", "career_start", "num_alter1", "num_alter2"]


sim_scores = sim_scores.merge(centralities, left_on="author", right_on="author")

sim_scores.to_csv("../output/author_covariates.csv", index=False)