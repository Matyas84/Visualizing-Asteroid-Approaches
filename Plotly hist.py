import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import matplotlib.colors as mcolors

# Load your data
final_df = pd.read_csv('final_df.csv')

# Initialize the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Data mapping for dropdowns
data_choices = {
    'Relative Velocity': {
        'relative_velocity_km/s': 'relative_velocity_km/s',
        'relative_velocity_km/h': 'relative_velocity_km/h',
        'relative_velocity_m/h': 'relative_velocity_m/h'
    },
    'Estimated Diameter Minimum': {
        'kilometers': 'kilometers.estimated_diameter_min',
        'meters': 'meters.estimated_diameter_min',
        'miles': 'miles.estimated_diameter_min',
        'feet': 'feet.estimated_diameter_min'
    },
    'Estimated Diameter Maximum': {
        'kilometers': 'kilometers.estimated_diameter_max',
        'meters': 'meters.estimated_diameter_max',
        'miles': 'miles.estimated_diameter_max',
        'feet': 'feet.estimated_diameter_max'
    },
    'Miss Distance': {
        'astronomical': 'miss_dist_astromnomical',
        'lunar': 'miss_dist_lunar',
        'kilometers': 'miss_dist_km',
        'miles': 'miss_dist_miles'
    }
}

# Updated color options
color_options = ['green', 'yellow', 'black', 'red', 'blue', 'cyan', 'magenta', 'orange', 'purple', 'brown', 'lime', 'teal', 'olive']

app.layout = html.Div([
    html.H1("Interactive Asteroid Data Visualization", style={'textAlign': 'center'}),
    html.Div([
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': k, 'value': k} for k in data_choices.keys()],
            value='Relative Velocity',
            style={'width': '70%', 'margin': 'auto'}
        ),
        dcc.Dropdown(
            id='type-dropdown',
            value='relative_velocity_km/h',
            style={'width': '70%', 'margin': 'auto'}
        ),
        dcc.Dropdown(
            id='plot-type-dropdown',
            options=[{'label': 'Histogram', 'value': 'Histogram'}, {'label': 'Box Plot', 'value': 'Box Plot'}],
            value='Histogram',
            style={'width': '70%', 'margin': 'auto'}
        ),
        html.Div([
            html.Label("Number of Bins:", style={'textAlign': 'center'}),
            dcc.Slider(
                id='bins-slider',
                min=1,
                max=50,
                step=1,
                value=30,
                marks={i: str(i) for i in range(1, 51) if i == 1 or i % 5 == 0},
                tooltip={"placement": "bottom", "always_visible": True},
                included=False  # Highlight only the selected point
            )
        ], id='bins-slider-div', style={'padding': 20, 'display': 'block', 'width': '70%', 'margin': 'auto'}),
        html.Label("Select a Color:", style={'textAlign': 'center'}),
        html.Div(
            dbc.ButtonGroup(
                [dbc.Button(style={'background-color': color, 'border': '1px solid black', 'width': '30px', 'height': '30px', 'border-radius': '50%', 'padding': '0', 'margin': '2px'}, id=color, n_clicks_timestamp=-1) for color in color_options],
                id='color-buttons',
                className="mr-2"
            ), style={'textAlign': 'center'}
        ),
        html.Div([
            html.Label("Color Transparency:", style={'textAlign': 'center'}),
            dcc.Slider(
                id='transparency-slider',
                min=0,
                max=1,
                step=0.1,
                value=1,
                marks={i / 10: str(i / 10) for i in range(0, 11)},
                tooltip={"placement": "bottom", "always_visible": True},
                included=False  # Highlight only the selected point
            )
        ], id='transparency-slider-div', style={'padding': 20, 'width': '70%', 'margin': 'auto'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),
    dcc.Graph(id='dynamic-plot', style={'width': '70%', 'margin': 'auto'})
])

# Callbacks for setting dynamic dropdown and plots
@app.callback(
    Output('type-dropdown', 'options'),
    Input('category-dropdown', 'value')
)
def set_type_options(selected_category):
    return [{'label': k, 'value': v} for k, v in data_choices[selected_category].items()]

@app.callback(
    Output('type-dropdown', 'value'),
    Input('type-dropdown', 'options')
)
def set_type_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('bins-slider-div', 'style'),
    Input('plot-type-dropdown', 'value')
)
def toggle_bins_slider(plot_type):
    if plot_type == 'Histogram':
        return {'padding': 20, 'display': 'block', 'width': '70%', 'margin': 'auto'}
    else:
        return {'padding': 20, 'display': 'none', 'width': '70%', 'margin': 'auto'}

@app.callback(
    Output('dynamic-plot', 'figure'),
    [Input('type-dropdown', 'value'), Input('plot-type-dropdown', 'value'), Input('bins-slider', 'value'), Input('transparency-slider', 'value')] + [Input(color, 'n_clicks_timestamp') for color in color_options]
)
def update_plot(selected_type, plot_type, bins, transparency, *args):
    ctx = dash.callback_context

    if not ctx.triggered:
        selected_color = 'green'
    else:
        timestamps = {color: ctx.inputs.get(f'{color}.n_clicks_timestamp', -1) for color in color_options}
        selected_color = max(timestamps, key=timestamps.get)

    # Convert the selected color to RGBA format with transparency
    rgba_color = mcolors.to_rgba(selected_color, alpha=transparency)

    if plot_type == 'Histogram':
        fig = px.histogram(final_df, x=selected_type, nbins=bins, title=f'<b>Distribution of {selected_type}</b>')
    else:
        fig = px.box(final_df, x=selected_type, title=f'<b>Distribution of {selected_type}</b>')

    # Update marker color with transparency
    fig.update_traces(marker=dict(color=f'rgba{rgba_color}'))

    fig.update_layout(title={'font': {'size': 20}})  # Make the title font size larger if needed

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)