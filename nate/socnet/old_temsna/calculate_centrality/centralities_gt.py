from graph_tool.all import *
import time
import pandas as pd
import igraph as ig


H = load_graph_from_csv("../input/coauthorship_edgeList.csv", string_vals = True, directed=False, skip_first=True)
H.save("gml", fmt='graphml')
G = ig.Graph.Read_GraphML("gml")



#following three lines aren't currently needed - we extract giant component earlier

#l = label_largest_component(H)

#G = GraphView(H, vfilt=l)

#G = Graph(G, prune=True)

auth_list = [H.vp.name[v] for v in H.vertices()]

vertex_between, edge_between = betweenness(H)

between_list = [vertex_between[v] for v in H.vertices()]

vertex_closeness = closeness(H)

close_list = [vertex_closeness[v] for v in H.vertices()]

eigen_value, eigen_vector = eigenvector(H)

eigen_list = [eigen_vector[v] for v in H.vertices()]

constraint_list = G.constraint()



centralities = pd.DataFrame()

centralities['author'] = auth_list
centralities['eigenvector'] = eigen_list
centralities['betweenness'] = between_list
centralities['closeness'] = close_list
centralities['constraint'] = constraint_list

centralities.to_csv('../output/centralities.csv')