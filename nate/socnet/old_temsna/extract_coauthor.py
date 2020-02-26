import metaknowledge as mk
import pandas as pd
import pickle
import community
import networkx as nx
import yaml
# Web of Science Field Codes
# AF (Full Author)
# TI (Title)
# ID (WoS Keywords)
# DE (Author keywords)
# AB (Abstracts)
# TC (Times Cited)
# PY (Year Published)

RCY = mk.RecordCollection('../input/', cached = False)

RC = RCY.yearSplit(2008,2019)

nx.

coauth = RC.networkCoAuthor()
# coauth.remove_nodes_from(list(nx.isolates(coauth)))   #temporarily commented out until we decide whether to NLP entire network or just giant component
coauth = max(nx.connected_component_subgraphs(coauth), key=len)  #temporarily added - see above
#partition = community.best_partition(coauth)
mk.writeGraph(coauth, '../output/coauthorship')

wos_dict = RC.makeDict(onlyTheseTags=["UT", "AF", "AU", "TI", "ID", "DE", "AB", "TC", "SO", "PY"],
           longNames=True, 
           numAuthors=False,
           genderCounts=False)

author_dict = {}

abs_dict = {}

cites_dict = {}


for i in range(0, len(wos_dict['wosString'])):
    wosID = wos_dict['wosString'][i]
    
    try:
        abs_dict[wosID] = {
            "abstract": wos_dict['abstract'][i],
            "title": wos_dict['title'][i],
            "keywords": [],
            }

        cites_dict[wosID] = {
            "cites": wos_dict['wosTimesCited'][i],
            "year": wos_dict['year'][i],
        } 
        
        abs_keywords = []
        try:
            abs_keywords.extend(wos_dict['keywords'][i])
        except TypeError:
            pass
        
        try:
            abs_keywords.extend(wos_dict['authKeywords'][i])
        except TypeError:
            pass
            
        abs_dict[wosID]['keywords'] = list(set(x.lower() for x in abs_keywords))
            
    except TypeError:
        pass
    
    try:     
        for author in wos_dict['authorsFull'][i]:
            if author in coauth:
                if author not in author_dict:
                    author_dict[author] = {
                        "wosString": [],
                        "title": [],
                        "keywords": [],
                        "abstract": [],
                        "wosTimesCited": 0,
                        "journal": [],
                        "year": [],
                        "community": 0,
                    }

                combined_keywords = []
                combined_keywords2 = []
                try:
                    combined_keywords.extend(wos_dict["keywords"][i])
                except TypeError:
                    pass
                try:
                    combined_keywords.extend(wos_dict["authKeywords"][i])
                except TypeError:
                    pass

                for keyword in combined_keywords:
                    combined_keywords2.append(keyword.lower())

                combined_keywords2 = list(set(combined_keywords2))

                author_dict[author]["wosString"].append(wos_dict["wosString"][i])
                author_dict[author]["title"].append(wos_dict["title"][i])
                author_dict[author]["keywords"] = combined_keywords2        
                author_dict[author]["abstract"].append(wos_dict["abstract"][i])
                author_dict[author]["wosTimesCited"] += (wos_dict["wosTimesCited"][i])
                author_dict[author]["journal"].append(wos_dict["journal"][i])
                author_dict[author]["year"].append(wos_dict["year"][i])
    except TypeError:
        pass
        
with open("../output/author_metadata.pkl", "wb") as handle:
    pickle.dump(author_dict, handle)
    
with open("../output/comm_abs.pkl", "wb") as handle:
    pickle.dump(abs_dict, handle)
    
with open("../output/cites_dict.yaml", "w") as stream:
    yaml.dump(cites_dict, stream, default_flow_style=False)
        
