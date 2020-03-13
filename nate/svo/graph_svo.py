import networkx as nx
import graphviz

svo_list = [
    ("Even CNN", "slamming", "the Obamas"),
    ("the NFL", "suspended", "Kaepernick"),
    ("the Russians", "purchase", "Hillary Clinton"),
    ("Judge Napolitano", "calls", "Hillary Clinton"),
    ("Bill Clinton", "raped", "Juanita Broderick"),
    ("the UK", "dominate", "Tesco"),
    ("the NFL", "give", "the SB"),
    ("the NFL", "give", "the SB"),
    ("Hillary Clinton", "becomes", "Hillary Clinton"),
    ("Hillary Clinton", "gave", "Mevs"),
]

G = nx.DiGraph()

def svo_graph(svo_list, file_name = "default"):
    for entry in svo_list:
        G.add_edge(entry[0], entry[2], label = " "+entry[1])

    for entry in G:
        G.nodes[entry]['style'] = 'filled'
        G.nodes[entry]['fillcolor'] = 'cadetblue2'


    toPdot = nx.drawing.nx_pydot.to_pydot
    N = toPdot(G)

    N.write(file_name + ".png", prog='dot', format='png')
    

if __name__ == "__main__":
    save_svo_graph(svo_list)