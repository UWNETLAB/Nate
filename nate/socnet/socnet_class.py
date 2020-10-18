"""
This module accepts a social network that has text attributes for nodes and outputs
the same social network with similarity values between i,j as an edge attribute 
"""
from nate.socnet.centralities import compute_centralities
from nate.socnet.alters import find_alters
from nate.socnet.dissimilarities import find_dissimilarities

class SOCnet():
    def __init__(self, data, edgelist):
        self.data = data
        self.edgelist = edgelist
        self.centralities = compute_centralities(edgelist)
        self.alters = find_alters(edgelist)
        self.dissimilarities = None
