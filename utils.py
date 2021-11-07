"""AutoMOO Utilities"""


import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import hiplot as hip


def group_columns(group_labels_with_columns, group_values, cor_threshold, cor_matrix):
    # TODO Create grouping algorithm
    a = 1
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
