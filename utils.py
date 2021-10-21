import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State


def create_dashboard(group_labels_with_columns, group_values):
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
            html.Button(id='update_button', n_clicks=0, children='Update Plot'),
            html.Div(html.Iframe(id='parallel', style={'width': '100%', 'height': '1080px'}))
        ]
    )

    return app
