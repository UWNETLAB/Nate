import pandas
from typing import List
from named_tuple_generator import create_observation_list
from abc import ABC, abstractmethod

class base_importer(ABC):
    @abstractmethod
    def __init__(self):
        self.raw_data = None

    def tupleize(self, tuple_name = "observation"):
        kwarg_dict = {}
        
        keys = self.raw_data.columns.tolist()
        
        for i in range(0,len(keys)):
            kwarg_dict[keys[i]] = list(self.raw_data[keys[i]])
            
        self.data = create_observation_list("observation", **kwarg_dict)


class import_dataframe(base_importer):
    """
    This class imports a pandas dataframe into Nate.

    Required Parameters:
        input_dataframe (pandas.DataFrame): The dataframe to be loaded.  
        text (str): The name of the column containing the text data to be analyzed with Nate. Required for all uses of Nate. 

    Optional Keyword Parameters:
        unique_id (str): The name of the column containing unique identifiers (e.g. a unique name or hash ID#). Required for some uses of Nate (e.g. Divsim).
        timestamp (str): The name of the column containing the time the observation was recorded. Required for some uses of Nate (e.g. edge_burst).
        columns_to_keep (list): A list of column names indicating which columns not specified elsewhere (e.g. for the timestamp parameter) are kept. 

    The columns indicated in the text, unique_id, and timestamp parameters will be renamed to 'text', 'unique_id', and 'timestamp', accordingly. The names of the
    columns listed in 'columns_to_keep' will be preserved as-is. 
    """

    def __init__(self, input_dataframe,  text:str, unique_id:str = None,  timestamp:str = None, columns_to_keep:List = []):

        self.process_dataframe(input_dataframe, text, unique_id,  timestamp, columns_to_keep)

    def process_dataframe(self, temp_data, text:str, unique_id:str = None,  timestamp:str = None, columns_to_keep:List = []):
        """
        This is a docstring
        """
        series_list = []
        special_column_list = [
            (text, "text"),
            (unique_id, "unique_id"),
            (timestamp, "timestamp")
        ]

        for special_column, special_column_name in special_column_list:
            if special_column != None:
                temp_column = temp_data[special_column]
                temp_column.name = special_column_name
                series_list.append(temp_column)

        for covariate_column in columns_to_keep:
            series_list.append(temp_data[covariate_column])

        self.raw_data = pandas.DataFrame(series_list).transpose()


class import_csv(import_dataframe, base_importer):
    """
    This class uses pandas to read in a comma-separated value file (.csv) into Nate.

    Required Parameters:
        file_path (str or path-like): The location of the file to be loaded from disk.  
        text (str): The name of the column containing the text data to be analyzed with Nate. Required for all uses of Nate. 

    Optional Keyword Parameters:
        unique_id (str): The name of the column containing unique identifiers (e.g. a unique name or hash ID#). Required for some uses of Nate (e.g. Divsim).
        timestamp (str): The name of the column containing the time the observation was recorded. Required for some uses of Nate (e.g. edge_burst).
        columns_to_keep (list): A list of column names indicating which columns not specified elsewhere (e.g. for the timestamp parameter) are kept. 

    The columns indicated in the text, unique_id, and timestamp parameters will be renamed to 'text', 'unique_id', and 'timestamp', accordingly. The names of the
    columns listed in 'columns_to_keep' will be preserved as-is. 

    Note that this class is only equipped to handle pre-processed .csv files that are ready to be loaded into a pandas dataframe with no additional manipulation. If
    the data requires any kind of special treatment, prudent users will first load their data using pandas directly into python, and then use the 'import_dataframe'
    class to load their data into Nate.
    """
    def __init__(self, file_path:str, text:str, unique_id:str = None,  timestamp:str = None, columns_to_keep:List = []):
        temp_data:pandas.DataFrame = pandas.read_csv(file_path)

        self.process_dataframe(temp_data, text, unique_id,  timestamp, columns_to_keep)


class import_excel(import_dataframe, base_importer):
    """
    This class uses pandas to read in an excel file (.xlsx) into Nate. 

    Required Parameters:
        file_path (str or path-like): The location of the file to be loaded from disk. 
        text (str): The name of the column containing the text data to be analyzed with Nate. Required for all uses of Nate. 

    Optional Keyword Parameters:
        unique_id (str): The name of the column containing unique identifiers (e.g. a unique name or hash ID#). Required for some uses of Nate (e.g. Divsim).
        timestamp (str): The name of the column containing the time the observation was recorded. Required for some uses of Nate (e.g. edge_burst).
        columns_to_keep (list): A list of column names indicating which columns not specified elsewhere (e.g. for the timestamp parameter) are kept. 

    The columns indicated in the text, unique_id, and timestamp parameters will be renamed to 'text', 'unique_id', and 'timestamp', accordingly. The names of the
    columns listed in 'columns_to_keep' will be preserved as-is. 

    Note that this class is only equipped to handle pre-processed .xlsx files that are ready to be loaded into a pandas dataframe with no additional manipulation. If
    the data requires any kind of special treatment, prudent users will first load their data using pandas directly into python, and then use the 'import_dataframe'
    class to load their data into Nate.
    """

    def __init__(self, file_path:str, text:str, unique_id:str = None,  timestamp:str = None, columns_to_keep:List = []):

        temp_data:pandas.DataFrame = pandas.read_excel(file_path)

        self.process_dataframe(temp_data,  text, unique_id,  timestamp, columns_to_keep)

        
