#from graph_tool.all import *



tuples = [tuple(x) for x in df.values]


auth_list = G.vs['name']



centralities = pd.DataFrame()

centralities['author'] = auth_list
centralities['eigenvector'] = eigen_list
centralities['betweenness'] = between_list
centralities['closeness'] = close_list
centralities['constraint'] = constraint_list
