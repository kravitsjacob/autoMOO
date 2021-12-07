"""autoMOO Utilities"""

import csv
import ast
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
    """
    This function parses the command line arguments and config file

    Returns
    -------
    data_file: str
        Data file pulled from config file
    cor_colormap : str
        string that dictates correlation matrix colors
    """
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument(
        '-c',
        '--config',
        type=str,
        action='store',
        help="This is the config file that" +
        " stores the preferences and paths",
        required=False
    )

    config_inputs = my_parser.parse_args()

    if config_inputs.config is None:
        raise TypeError('Please include config file to create dashboard')
        sys.exit(1)
    elif config_inputs.config is not None:
        my_config = configparser.ConfigParser()
        my_config.read(config_inputs.config)
        if my_config['FILES']['input'] is None:
            raise TypeError(
                'Missing data file path. Please add this to your config file'
            )
            sys.exit(1)
        if my_config['FILES']['input'] is None:
            raise TypeError(
                'Missing data file path. Please add this to your config file'
            )
            sys.exit(1)
        elif my_config['PREFERENCES']['correlation_colormap'] is None:
            raise TypeError(
                'Missing correlation colormap. Please add this to your config'
                ' file'
            )
            sys.exit(1)
        else:
            data_file = my_config['FILES']['input']
            cor_colormap = my_config['PREFERENCES']['correlation_colormap']

    return data_file, cor_colormap


def file_reader(path):
    """
    Read contents of Comma Separated Values (CSV) files

    TODO it is faster to guess the datatypes initially instead of for every
    row with the underlying assumption is that each column will have a
    consistent datatype

    Parameters
    ----------
    path: str
        Path to file

    Returns
    -------
    data: list
        List of dictionaries containing the contents of dataset stored in
        `path`. This has the form
        [
            {col1: val1, col2: val1},
            {col1: val2, col2: val2}
            ...
        ]
    """
    with open(path, 'r') as read_obj:
        data = []
        dict_reader = csv.DictReader(read_obj, skipinitialspace=True)
        for row in dict_reader:
            data.append({k: ast.literal_eval(v) for k, v in row.items()})

    return data


def correlation_matrix(
        data,
        colormap=px.colors.diverging.RdBu
):
    """
    This function creates correlation matrices.

    TODO this function is still parsing datatypes

    Parameters
    ----------
    data: list
        List of dictionaries containing the contents of dataset
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
    corr_mat = pd.DataFrame(data).corr()

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

    # Convert to base
    correlations = correlations.tolist()

    return correlations, correlation_visual


def group_columns(
    data,
    cors,
    cor_threshold
):
    """
    Grouping columns

    Parameters
    ----------
    data: list
        List of dictionaries containing the contents of dataset
    cors: list
        List of lists containing column correlations
    cor_threshold: float
            Current correlation threshold selected by the user

    Returns
    -------
    data_grouped: dict
        List of dictionaries containing the grouped dataset based on
        `cor_threshold`
    group_labels_with_columns: dict
        Updated `group_labels_with_columns` based on `cor_threshold`. Keys are
        each group and contents are a list of columns in that group
    """
    group_labels_with_columns = {'Group 1': []}  # initialize empty dictionary
    data_grouped = {}  # initialize empty array
    group_label = 0
    val = -1
    col_list = list(data[0].keys())  # create list of column labels
    for col in col_list:
        val = val + 1  # iterable value for correlation check

        # List currently grouped columns
        group_cols = sorted(
            {x for v in group_labels_with_columns.values() for x in v}
        )

        # If group label not included in grouped columns already
        if col not in group_cols:
            group_label = group_label + 1
            group_name = 'Group ' + str(group_label)

            # Store previous label in new group
            group_labels_with_columns[group_name] = [col]

            # Add column data to grouped data
            group_data = [row[list(row.keys())[0]] for row in data]
            data_grouped[group_name] = group_data

            # Remaining column labels
            for leftover in range(val+1, len(col_list), 1):
                # Pull correlation value
                correlation_val = cors[val][leftover]

                if correlation_val > cor_threshold:  # if higher than threshold
                    stor = col_list[leftover]  # get name of column
                    # store name of column in group
                    group_labels_with_columns[group_name].append(stor)
                else:
                    pass

    return data_grouped, group_labels_with_columns


def create_dashboard(
        data,
        cor_colormap,
):
    """
    Create dash app

    Parameters
    ----------
    data: list
        List of dictionaries containing the contents of dataset. Has form:
        [
            {col1: val1, col2: val1},
            {col1: val2, col2: val2}
            ...
        ]
    cor_colormap: str
        Plotly diverging colormap

    Returns
    -------
    app: Dash
        AutoMOO dashboard
    """
    # Initialize app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Correlation matrix
    cors, cor_fig = correlation_matrix(
        data=data,
        colormap=getattr(px.colors.diverging, cor_colormap)
    )

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
                            columns=[
                                {'name': 'Group', 'id': 'Group'},
                                {'name': 'Columns', 'id': 'Columns'}
                            ],
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                            },
                            style_cell_conditional=[
                                {'if': {'column_id': 'Group'},
                                 'width': '20%'}
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
                    'data': data,
                    'cors': cors,
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
        group_table_data: dict
            Data for the group_table display
        """
        # Unpack memory data
        data = memory_data['data']
        cors = memory_data['cors']

        if n_clicks == 0:
            exp = hip.Experiment.from_iterable(data)
            exp.display_data(
                hip.Displays.PARALLEL_PLOT
            ).update({'hide': ['uid']})
            exp.display_data(
                hip.Displays.TABLE
            ).update({'hide': ['uid', 'from_uid']})
            srcdoc = exp.to_html()  # Store html as string
        else:
            new_group_labels_with_columns, new_group_values = group_columns(
                data=data,
                cors=cors,
                cor_threshold=cor_threshold,
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
                group_table_data.append(
                    {'Group': key, 'Columns': ', '.join(value)}
                )

        return srcdoc, group_table_data

    return app
