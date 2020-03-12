import networkx as nx

def save_svo_graph(svo_list, file_name = "test"):

    G = nx.DiGraph()
    
    for entry in svo_list:
        G.add_edge(entry[0], entry[2], label = " "+ entry[1])

    for entry in G:
        G.nodes[entry]['style'] = 'filled'
        G.nodes[entry]['fillcolor'] = 'cadetblue2'


    toPdot = nx.drawing.nx_pydot.to_pydot
    N = toPdot(G)

    N.write(file_name + ".png", prog='dot', format='png')