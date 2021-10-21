import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import hiplot as hip


def group_columns(group_labels_with_columns, group_values, cor_threshold):
    # TODO Create grouping algorithm
    return group_labels_with_columns, group_values


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
            html.Div(html.Iframe(id='parallel', style={'width': '100%', 'height': '1080px'})),
            dcc.Store(id='memory', data={'group_labels_with_columns': group_labels_with_columns,
                                         'group_values': group_values})
        ]
    )

    @app.callback(
        Output('parallel', 'srcDoc'),
        Input('update_button', 'n_clicks'),
        State('cor_threshold', 'value'),
        State('memory', 'data')
    )
    def update_parallel(n_clicks, cor_threshold, memory_data):
        # Unpack memory data
        old_group_labels_with_columns = memory_data['group_labels_with_columns']
        old_group_values = memory_data['group_values']

        if n_clicks == 0:
            srcdoc = ''
        else:
            # TODO Create column grouping algorithm
            new_group_labels_with_columns, new_group_values = group_columns(
                old_group_labels_with_columns, old_group_values, cor_threshold
            )

            # Create parallel plot
            exp = hip.Experiment.from_iterable()

            exp.display_data(hip.Displays.PARALLEL_PLOT).update({'hide': ['uid']})
            exp.display_data(hip.Displays.TABLE).update({'hide': ['uid', 'from_uid']})
            srcdoc = exp.to_html()  # Store html as string
        return srcdoc

    return app
