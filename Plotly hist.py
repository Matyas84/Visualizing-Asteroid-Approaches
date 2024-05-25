import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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
        'astronomical': 'miss_dist_astronomical',
        'lunar': 'miss_dist_lunar',
        'kilometers': 'miss_dist_km',
        'miles': 'miss_dist_miles'
    }
}

app.layout = html.Div([
    html.H1("Interactive Asteroid Data Visualization"),
    html.Div([
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': k, 'value': k} for k in data_choices.keys()],
            value='Relative Velocity'
        ),
        dcc.Dropdown(
            id='type-dropdown',
            value='relative_velocity_km/h'
        ),
        dcc.Dropdown(
            id='plot-type-dropdown',
            options=[{'label': 'Histogram', 'value': 'Histogram'}, {'label': 'Box Plot', 'value': 'Box Plot'}],
            value='Histogram'
        ),
        dcc.Dropdown(
            id='color-dropdown',
            options=[
                {'label': 'Green', 'value': 'green'},
                {'label': 'Yellow', 'value': 'yellow'},
                {'label': 'Black', 'value': 'black'},
                {'label': 'Red', 'value': 'red'},
                {'label': 'Blue', 'value': 'blue'},
                {'label': 'Cyan', 'value': 'cyan'},
                {'label': 'Magenta', 'value': 'magenta'},
                {'label': 'Orange', 'value': 'orange'},
                {'label': 'Purple', 'value': 'purple'},
                {'label': 'Brown', 'value': 'brown'},
                {'label': 'Pink', 'value': 'pink'}
            ],
            value='green',  # Initial default color set to 'green'
            placeholder='Select a color'
        )
    ], style={'display': 'flex', 'flexDirection': 'column'}),
    dcc.Graph(id='dynamic-plot')
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
    Output('dynamic-plot', 'figure'),
    [Input('type-dropdown', 'value'), Input('plot-type-dropdown', 'value'), Input('color-dropdown', 'value')]
)
def update_plot(selected_type, plot_type, color):
    if plot_type == 'Histogram':
        fig = px.histogram(final_df, x=selected_type, color_discrete_sequence=[color], nbins=30, title='Distribution of ' + selected_type)
    else:
        fig = px.box(final_df, x=selected_type, color_discrete_sequence=[color], title='Distribution of ' + selected_type)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
