"""autoMOO Utilities"""

import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import hiplot as hip
import argparse
import configparser
import seaborn as sns
import matplotlib.pyplot as plt
import sys


def input_parser():
    '''
    This function parses the command line arguments.

    Returns
    -------
    config_inputs : list
       The function return is list of parsed arguments.
    '''
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument(
        '-c',
        '--config',
        type=str,
        action='store',
        help="This is the config file that" +
        " stores the preferences and paths",
        required=True
    )

    config_inputs = my_parser.parse_args()
    return config_inputs
  

def config_parser(arguments):
    '''
    This function parses the config file.

    Parameters
    ----------
    arguments: list
        This is a config file from the argument line

    Returns
    -------
    data_file: str
        Data file pulled from config file
    correlation_colormap : str
        string that dictates correlation matrix colors
    dashboard preferences TBD : str, int etc
        TBD
    '''
    # checking config file
    if arguments.config is None:
        raise TypeError('Please include config file to create dashboard')
        sys.exit(1)
    elif arguments.config is not None:
        my_config = configparser.ConfigParser()
        my_config.read(arguments.config)
        if my_config['FILES']['input'] is None:
            raise TypeError('Missing data file path. Please add this to your config file')
            sys.exit(1)
        if my_config['FILES']['input'] is None:
            raise TypeError('Missing data file path. Please add this to your config file')
            sys.exit(1)
        elif my_config['PREFERENCES']['correlation_colormap'] is None:
            raise TypeError('Missing correlation colormap. Please add this to your config file')
            sys.exit(1)
        #add elifs for other dash preferences
        else:
            data_file = my_config['FILES']['input']
            tbd = my_config['PREFERENCES']['TBD']
            correlation_colormap = my_config['PREFERENCES']['correlation_colormap']
    return data_file, tbd, correlation_colormap


def correlation_matrix(data,colormap):
    '''
    This function creates correlation matrices.

    Parameters
    ----------
    data : dataframe
        dataframe that holds csv data
    colormap: str
        string that dictates colors of correlation heatmap visual
    
    Returns
    -------
    correlations: numpy array
        array which holds correlations
    correlation_colormap : plot
        correlation heatmap visual
    '''
    #creates correlation matrix
    corr_mat = data.corr()
    #creates numpy array of correlations
    correlations = corr_mat.to_numpy()
    #creates a heatmap visualization that can be used by researcher
    correlation_visual = sns.heatmap(corr_mat, annot=True, cmap=colormap)
    return correlations, correlation_visual


def group_columns(
        column_labels,
        data,
        cor_threshold,
        cor_matrix
):
    """
    Grouping columns

    Parameters
    ----------
    column_labels: dict
        Dictionary with keys of group labels and values of corresponding
        column labels
    data: ndarray
        Numpy array with each column being the values for each group
    cor_threshold: float
            Current correlation threshold selected by the user
    cor_matrix: ndarray
        Numpy arrary of column correlations

    Returns
    -------
    group_labels_with_columns: dict
        Updated `group_labels_with_columns` based on `cor_threshold`
    group_values: ndarray
        Updated `group_values` based on `cor_threshold`
    """
    group_labels_with_columns = {}  # initialize empty dictionary
    group_values = np.array([])  # initialize empty array
    group_label = 0
    val = -1
    col_list = list(column_labels.keys())  # create list of column labels
    for name in column_labels:
        val = val + 1  # iterable value for correlation check
        # if group label not included in grouped dictionary already
        if any(name != i for i in group_labels_with_columns.values()):
            group_label = group_label + 1
            # store previous label in new group
            group_labels_with_columns[str(group_label)] = name
            # add column data to grouped data
            group_values.append(data[:, val])
            # remaining column labels
            for leftover in range(val+1, len(col_list), 1):
                # pull correlation value
                correlation_val = cor_matrix(val, leftover)
                if correlation_val > threshold:  # if higher than threshold
                    stor = col_list(leftover)  # get name of column
                    # store name of column in group
                    group_labels_with_columns[str(group_label)].append(stor)
                else:
                    pass
        # if group only has one entry
        if len(group_labels_wth_columns[str(group_label)]) < 2:
            new = str(name)
            old = str(group_label)
            # change key name to original
            group_labels_with_columns[new] = group_labels_with_columns.pop(old)

    return group_labels_with_columns, group_values


def create_dashboard(group_labels_with_columns, group_values, cor_matrix):
    """
    Create dash app

    Parameters
    ----------
    group_labels_with_columns: dict
        Dictionary with keys of group labels and values of corresponding
        column lables
    group_values: ndarray
        Numpy array with each column being the values for each group
    cor_matrix: ndarray
        Numpy arrary of column correlations

    Returns
    -------
    app: Dash
        AutoMOO dashboard
    """
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Label(
                [
                    'Select Correlation Threshold',
                    dcc.Input(
                        id='cor_threshold',
                        type='number'
                    )
                ]
            ),
            html.Button(
                id='update_button',
                n_clicks=0,
                children='Update Plot'
            ),
            html.Div(
                html.Iframe(
                    id='parallel',
                    style={'width': '100%', 'height': '1080px'}
                )
            ),
            dcc.Store(
                id='memory',
                data={
                    'group_labels_with_columns': group_labels_with_columns,
                    'group_values': group_values,
                    'cor_matrix': cor_matrix
                }
            )
        ]
    )

    @app.callback(
        Output('parallel', 'srcDoc'),
        Output('memory', 'data'),
        Input('update_button', 'n_clicks'),
        State('cor_threshold', 'value'),
        State('memory', 'data')
    )
    def update_parallel(n_clicks, cor_threshold, memory_data):
        """
        Update parallel axis plots

        Parameters
        ----------
        n_clicks: int
            Number of times button pressed
        cor_threshold: float
            Current correlation threshold selected by the user
        memory_data: dict
            Data stored in memory

        Returns
        -------
        srcdoc: str
            html rendering as string

        memory_data: dict
            Updated data stored in memory
        """
        # Unpack memory data
        old_group_labels_with_columns = \
            memory_data['group_labels_with_columns']
        old_group_values = np.array(memory_data['group_values'])
        cor_matrix = np.array(memory_data['cor_matrix'])

        if n_clicks == 0:
            srcdoc = ''
        else:
            # TODO Create column grouping algorithm
            new_group_labels_with_columns, new_group_values = group_columns(
                old_group_labels_with_columns,
                old_group_values,
                cor_threshold,
                cor_matrix
            )

            # Create parallel plot
            df = pd.DataFrame(
                new_group_values,
                columns=new_group_labels_with_columns.keys()
            )
            exp = hip.Experiment.from_dataframe(df)
            exp.display_data(
                hip.Displays.PARALLEL_PLOT
            ).update({'hide': ['uid']})
            exp.display_data(
                hip.Displays.TABLE
            ).update({'hide': ['uid', 'from_uid']})
            srcdoc = exp.to_html()  # Store html as string

            # Pack in memory data
            memory_data['group_labels_with_columns'] = \
                new_group_labels_with_columns
            memory_data['group_values'] = new_group_values
        return srcdoc, memory_data

    return app
