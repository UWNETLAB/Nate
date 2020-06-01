"""`Nate` importers for edgelists."""

import pandas
from .named_tuple_generator import tupleize


def process_edgelist(temp_data, From, To, Weight=None):
    """Turns an edgelist in a dataframe into a list of NamedTuples."""

    series_dict = {}

    special_column_list = [(From, "From"), (To, "To"), (Weight, "Weight")]

    for special_column, special_column_name in special_column_list:
        if special_column != None:
            temp_column = temp_data[special_column]
            temp_column.name = special_column_name
            series_dict[special_column_name] = temp_column.tolist()

    return tupleize(series_dict, "edge")


class EdgelistMixin():
    """Provides edgelist functionality to objects in nate."""

    def add_edges_from_csv(self, file_path, From, To, Weight=None):
        """Imports an edgelist from a .csv file into `nate`.
        
        This function sets the self.edgelist attribute to a list of
        NamedTuples, with each tuple representing one edge.

        Args:
            file_path (str): The location of the file to be loaded from disk.
            From (str): The name of the column containing the origin of
                the edge.
            To (str): The name of the column containing the destination of
                the edge.
            Weight (str, optional): The column containing the edge's weight.
            
        Note that the capitalized arguments are a result of 'from' being a
        reserved keyword in Python.
        """

        col_list = [From, To]

        if Weight != None:
            col_list.append(Weight)

        temp_data = pandas.read_csv(file_path, usecols=col_list)

        self.edgelist = process_edgelist(temp_data,
                                         From=From,
                                         To=To,
                                         Weight=Weight)

    def add_edges_from_dataframe(self, dataframe, From, To, Weight=None):
        """Imports an edgelist from a dataframe into `nate`.
        
        This function sets the self.edgelist attribute to a list of
        NamedTuples, with each tuple representing one edge.

        Args:
            dataframe (pandas.Dataframe): The dataframe from which to extract
                the edgelist.
            From (str): The name of the column containing the origin of
                the edge.
            To (str): The name of the column containing the destination of
                the edge.
            Weight (str, optional): The column containing the edge's weight.
            
        Note that the capitalized arguments are a result of 'from' being a
        reserved keyword in Python.
        """
        self.edgelist = process_edgelist(dataframe,
                                         From=From,
                                         To=To,
                                         Weight=Weight)
