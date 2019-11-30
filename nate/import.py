import pandas
from typing import List
from named_tuple_generator import create_observation_list

class base_importer():
    def __init__(self):
        self.data = None

    def tupleize(self):
        kwarg_dict = {}
        
        keys = self.data.columns.tolist()
        
        for i in range(0,len(keys)):
            kwarg_dict[keys[i]] = list(self.data[keys[i]])
            
        return create_observation_list("observation", **kwarg_dict)
        

class import_csv(base_importer):
    def __init__(self, file:str, unique_id:str = None, text:str = None, location:str = None, timestamp:str = None):
        self.data = pandas.read_csv(file)
        

class import_df(base_importer):
    def __init__(self):
        pass


