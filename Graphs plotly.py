import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc  # Correct import statement
import plotly.express as px
import pandas as pd

# Load your data
final_df = pd.read_csv('final_df.csv')

# Initialize the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Interactive Asteroid Data Visualization"),
    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
                id='size-slider',
                min=final_df['meters.estimated_diameter_min'].min(),
                max=final_df['meters.estimated_diameter_max'].max(),
                step=10,
                value=[100, 500],
                marks={str(size): str(size) for size in range(100, 501, 100)},
                tooltip={"placement": "bottom", "always_visible": True},
            )
        ], width=12)
    ]),
    dcc.Graph(id='scatter-plot'),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='velocity-type-dropdown',
                options=[
                    {'label': 'Histogram', 'value': 'Histogram'},
                    {'label': 'Box Plot', 'value': 'Box Plot'}
                ],
                value='Histogram'
            )
        ], width=6)
    ]),
    dcc.Graph(id='velocity-plot')
])

# Callback for updating the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('size-slider', 'value')]
)
def update_scatter(selected_size):
    filtered_df = final_df[
        (final_df['meters.estimated_diameter_min'] >= selected_size[0]) &
        (final_df['meters.estimated_diameter_max'] <= selected_size[1])
    ]
    fig = px.scatter(
        filtered_df, x='absolute_magnitude_h', y='relative_velocity_km/h',
        size='meters.estimated_diameter_min', color='is_potentially_hazardous_asteroid',
        size_max=15, hover_name="name", title='Comparison of Asteroid Sizes vs. Magnitude vs. Velocity'
    )
    return fig

# Callback for updating the velocity distribution plot
@app.callback(
    Output('velocity-plot', 'figure'),
    [Input('velocity-type-dropdown', 'value')]
)
def update_velocity_plot(plot_type):
    if plot_type == 'Histogram':
        fig = px.histogram(final_df, x='relative_velocity_km/h', nbins=30, title='Histogram of Asteroid Velocities')
    else:
        fig = px.box(final_df, x='relative_velocity_km/h', title='Box Plot of Asteroid Velocities')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
