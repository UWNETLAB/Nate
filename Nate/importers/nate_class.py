from pprint import pprint
from ..edgeburst.edge_burst_class import edge_burst
 

class nate():
    """
    This is the `Nate` package's base class. Each of the importer functions the `Nate` package loads into namespace returns a populated instance of the `nate` class.

    Calling this class directly is functionally identical to 
    """
    def __init__(self, data):
        self.data = data

    def __call__(self, start:int = 0, end:int = 5):
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def __getitem__(self, index):
        return self.data[index]

    def head(self, start:int = 0, end:int = 5):
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def list_texts(self, start:int = None, end:int = None):
        """
        Returns a list of 
        """ 
        return [str(i.text) for i in self.data[start:end]]

    def list_timestamps(self, start:int = None, end:int = None):
        """
        This is a docstring
        """
        return [i.timestamp for i in self.data[start:end]]

    def list_ids(self, start:int = None, end:int = None): 
        """
        This is a docstring
        """ 
        return [i.unique_id for i in self.data[start:end]]

    def list_column(self, column_name:str, start:int = None, end:int = None): 
        """
        This is a docstring
        """ 
        return [getattr(i, column_name) for i in self.data[start:end]]

    def edge_burst_pipeline(self): 
        """
        Returns an instance of the 'edge_burst' class, initialized with the relevant data contained 
        """ 
        return edge_burst(self)
