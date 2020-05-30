"""`Nate` importers involving pandas.

This module provides common importers for the `Nate` class. They use existing
pandas import functionality as an interface to `Nate`. These importers are the
reccomended way to import data into `Nate`, unless the user needs to import data
in ways not covered by this module's functionality.
"""

import pandas
from typing import List, Union
from .named_tuple_generator import tupleize
from .nate_class import Nate
from .timestamp_process import convert_times


def process_dataframe(temp_data,
                      text: str,
                      unique_id: str = None,
                      time: str = None,
                      columns_to_keep: List = []):
    """Builds a nate object from a dataframe."""
    series_dict = {}
    special_column_list = [(text, "text"), (unique_id, "unique_id"),
                           (time, "times")]

    for special_column, special_column_name in special_column_list:
        if special_column != None:
            temp_column = temp_data[special_column]
            temp_column.name = special_column_name
            series_dict[special_column_name] = temp_column.tolist()

    for covariate_column in columns_to_keep:
        temp_column = temp_data[covariate_column]
        temp_column.name = covariate_column
        series_dict[covariate_column] = temp_column.tolist()

    if time != None:
        series_dict['time'] = convert_times(series_dict['times'])
        del series_dict['times']

    return Nate(tupleize(series_dict))


def import_dataframe(input_dataframe: pandas.DataFrame,
                     text: str,
                     unique_id: str = None,
                     time: str = None,
                     columns_to_keep: List = []):
    """Imports a pandas dataframe into nate.

    Args:
        input_dataframe (pandas.DataFrame): The dataframe to be loaded.
        text (str): The name of the column containing the text data to be
            analyzed with nate. Required for all uses of nate.
        unique_id (str, optional): The name of the column containing unique
            identifiers (e.g. a unique name or hash ID#). Required
            for some uses of nate (e.g. Divsim).
        time (str, optional): The name of the column containing the time the
            observation was recorded. Required for some uses of
            nate (e.g. edge_burst).
        columns_to_keep (list, optional): A list of column names indicating
            which columns not specified elsewhere (e.g. for the
            time parameter) are kept.

    Returns:
        Nate: an instance of the `Nate` class containing all data from the
            columns specified in the parameters.

    The columns indicated in the text, unique_id, and time parameters will
    be renamed to 'text', 'unique_id', and 'time', accordingly. The names
    of the columns listed in 'columns_to_keep' will be preserved as-is.
    """
    return process_dataframe(input_dataframe, text, unique_id, time,
                             columns_to_keep)


def import_csv(file_paths: Union[List, str],
               text: str,
               unique_id: str = None,
               time: str = None,
               columns_to_keep: List = [],
               observation_threshold=0):
    """Imports a comma-separated values file (.csv) into nate.

    This function uses pre-existing pandas functionality to read in a
    comma-separated value file (.csv) into nate.

    Args:
        file_path (str or path-like): The location of the file to
            be loaded from disk.
        text (str): The name of the column containing the text
            data to be analyzed with nate. Required for all uses of nate.
        unique_id (str, optional): The name of the column containing unique
            identifiers (e.g. a unique name or hash ID#). Required for
            some uses of nate (e.g. Divsim).
        time (str, optional): The name of the column containing the time the
            observation was recorded. Required for some uses of nate
            (e.g. edge_burst).
        columns_to_keep (list, optional): A list of column names indicating
            which columns not specified elsewhere (e.g. for the time
            parameter) are kept.
        observation_threshold (int, optional): An integer indicating how many
            observations to include in the imported data, at minimum.
            Once the number of rows in the imported dataset exceeds this value,
            the importer will not import the next file in the list of
            file paths passed to `file_path`. Has no effect if a string
            or path-like object is passed to `file_paths`.

    Returns:
        Nate: an instance of the `Nate` class containing all data from the
            columns specified in the parameters.

    The columns indicated in the text, unique_id, and time parameters will
    be renamed to 'text', 'unique_id', and 'time', accordingly. The names of the
    columns listed in 'columns_to_keep' will be preserved as-is.

    Note that this function is only equipped to handle pre-processed .csv
    files that are ready to be loaded into a pandas dataframe with no
    additional manipulation. If the data requires any kind of special
    treatment, prudent users will first load their data using pandas
    directly into python, and then use the 'import_dataframe' function
    to load their data into nate.
    """
    columns_to_import = [*columns_to_keep]

    for special_column in [text, unique_id, time]:
        if special_column != None:
            columns_to_import.append(special_column)

    if isinstance(file_paths, list):
        df_list = []
        total_len = 0
        for entry in file_paths:
            temp_df = pandas.read_csv(entry, usecols=columns_to_import)
            df_list.append(temp_df)

            if observation_threshold != 0:
                total_len += len(temp_df)
                if total_len >= observation_threshold:
                    break

        temp_data = pandas.concat(df_list)

    elif isinstance(file_paths, str):

        temp_data = pandas.read_csv(file_paths, usecols=columns_to_import)

    else:
        raise TypeError("file_paths must be either string or list of strings")

    return process_dataframe(temp_data, text, unique_id, time, columns_to_keep)


def import_excel(file_paths: Union[List, str],
                 text: str,
                 unique_id: str = None,
                 time: str = None,
                 columns_to_keep: List = [],
                 observation_threshold=0):
    """Imports an excel file (.xlsx) into nate.

    This function uses pre-existing pandas functionality to read in an excel
    file (.xlsx) into nate.

    Args:
        file_path (str or path-like): The location of the file to be
            loaded from disk.
        text (str): The name of the column containing the text data
            to be analyzed with nate. Required for all uses of nate.
        unique_id (str, optional): The name of the column containing unique
            identifiers (e.g. a unique name or hash ID#). Required for
            some uses of Nate.
        time (str, optional): The name of the column containing the time the
            observation was recorded. Required for some uses of nate
            (e.g. edge_burst).
        columns_to_keep (list, optional): A list of column names indicating
            which columns not specified elsewhere (e.g. for the time
            parameter) are kept.
        observation_threshold (int, optional): An integer indicating how many
            observations to include in the imported data, at minimum. Once
            the number of rows in the imported dataset exceeds this value,
            the importer will not import the next file in the list of file
            paths passed to `file_path`. Has no effect if a string or
            path-like object is passed to `file_paths`.

    Returns:
        A `Nate` object containing all data from the columns specified in
            the parameters.

    The columns indicated in the text, unique_id, and time parameters will be
    renamed to 'text', 'unique_id', and 'time', accordingly. The names of the
    columns listed in 'columns_to_keep' will be preserved as-is.

    Note that this function is only equipped to handle pre-processed .xlsx
    files that are ready to be loaded into a pandas dataframe with no
    additional manipulation. If the data requires any kind of special
    treatment, prudent users will first load their data using pandas
    directly into python, and then use the 'import_dataframe' function to
    load their data into nate.
    """
    columns_to_import = [*columns_to_keep]

    for special_column in [text, unique_id, time]:
        if special_column != None:
            columns_to_import.append(special_column)

    print(columns_to_import)
    print(columns_to_keep)

    if isinstance(file_paths, list):
        df_list = []
        total_len = 0
        for entry in file_paths:
            temp_df = pandas.read_excel(entry, usecols=columns_to_import)
            df_list.append(temp_df)

            if observation_threshold != 0:
                total_len += len(temp_df)
                if total_len >= observation_threshold:
                    break

        temp_data = pandas.concat(df_list)

    elif isinstance(file_paths, str):

        temp_data = pandas.read_excel(file_paths, usecols=columns_to_import)

    else:
        raise TypeError("file_paths must be either string or list of strings")

    return process_dataframe(temp_data, text, unique_id, time, columns_to_keep)
