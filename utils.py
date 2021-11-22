"""autoMOO Utilities"""

import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import hiplot as hip
import argparse
import configparser
import plotly.express as px
import plotly.graph_objs as go
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


def correlation_matrix(
        data,
        colormap=px.colors.diverging.BrBG
):
    """
    This function creates correlation matrices.

    Parameters
    ----------
    data : dataframe
        dataframe that holds csv data
    colormap: list
        List of plotly colormap
    
    Returns
    -------
    correlations: numpy array
        array which holds correlations
    correlation_visual: plotly.graph_objs._figure.Figure
        Plotly figure of column correlations
    """
    # Creates correlation matrix
    corr_mat = data.corr()

    # Creates numpy array of correlations
    correlations = corr_mat.to_numpy()

    # Creates a heatmap visualization that can be used by researcher
    correlation_visual = go.Figure(
        go.Heatmap(
            z=corr_mat.values,
            x=corr_mat.index.values,
            y=corr_mat.columns.values,
            colorscale=colormap,
            showscale=True,
            ygap=1,
            xgap=1
        )
    )
    
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
    group_labels_with_columns = {'Group 1': []}  # initialize empty dictionary
    group_values = []  # initialize empty array
    group_label = 0
    val = -1
    col_list = list(column_labels.keys())  # create list of column labels
    for name in column_labels:
        val = val + 1  # iterable value for correlation check

        # List currently grouped columns
        group_cols = sorted({x for v in group_labels_with_columns.values() for x in v})

        # if group label not included in grouped columns already
        if name not in group_cols:
            group_label = group_label + 1
            group_label = 'Group ' + str(group_label)
            # store previous label in new group
            group_labels_with_columns[group_label] = [name]
            # add column data to grouped data
            group_values.append(data[:, val])
            # remaining column labels
            for leftover in range(val+1, len(col_list), 1):
                # pull correlation value
                correlation_val = cor_matrix[val, leftover]
                if correlation_val > cor_threshold:  # if higher than threshold
                    stor = col_list[leftover]  # get name of column
                    # store name of column in group
                    group_labels_with_columns[group_label].append(stor)
                else:
                    pass
    return group_labels_with_columns, group_values


def group_columns_temp(
        column_labels,
        data,
        cor_threshold,
        cor_matrix
):
    # Create labels
    group_labels_with_columns = {}
    for i, column in enumerate(column_labels):
        group_labels_with_columns['Group ' + str(i + 1)] = [column]

    # Create data
    group_values = []
    for i in range(data.shape[1]):
        group_values.append(data[:, i])

    return group_labels_with_columns, group_values


def create_dashboard(
        group_labels_with_columns,
        group_values,
        cor_matrix,
        cor_fig
):
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
        Numpy array of column correlations
    cor_fig: plotly.graph_objs._figure.Figure
        Plotly figure of column correlations

    Returns
    -------
    app: Dash
        AutoMOO dashboard
    """
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container(
        [
            dbc.Row(dbc.Col(html.H1('AutoMOO'))),
            dbc.Row(
                dbc.Col(
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
                        )
                    ]
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id='correlation_matrix', figure=cor_fig)
                    ),
                    dbc.Col(
                        dash_table.DataTable(
                            id='group_table',
                            #data=[{'A': 1, 'B': 2}, {'A': 3, 'B': 2}],
                            columns=[
                                {'name': 'Group', 'id': 'Group'},
                                {'name': 'Columns', 'id': 'Columns'}
                            ]
                        )
                    )
                ]
            ),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        html.Iframe(
                            id='parallel',
                            style={'width': '100%', 'height': '1080px'}
                        )
                    ),
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
        Output('group_table', 'data'),
        Input('update_button', 'n_clicks'),
        State('cor_threshold', 'value'),
        State('group_table', 'data'),
        State('memory', 'data'),
    )
    def update_parallel(
            n_clicks,
            cor_threshold,
            group_table_data,
            memory_data
    ):
        """
        Update parallel axis plots

        Parameters
        ----------
        n_clicks: int
            Number of times button pressed
        cor_threshold: float
            Current correlation threshold selected by the user
        group_table_data: dict
            Group labels and columns within each group
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
            new_group_labels_with_columns, new_group_values = group_columns_temp(
                old_group_labels_with_columns,
                old_group_values,
                cor_threshold,
                cor_matrix
            )

            # Update parallel plot
            df = pd.DataFrame(new_group_values).T
            df.columns = new_group_labels_with_columns.keys()
            exp = hip.Experiment.from_dataframe(df)
            exp.display_data(
                hip.Displays.PARALLEL_PLOT
            ).update({'hide': ['uid']})
            exp.display_data(
                hip.Displays.TABLE
            ).update({'hide': ['uid', 'from_uid']})
            srcdoc = exp.to_html()  # Store html as string

            # Update group table
            group_table_data = []
            for key, value in new_group_labels_with_columns.items():
                group_table_data.append({'Group': key, 'Columns': value})

        return srcdoc, group_table_data

    return app
