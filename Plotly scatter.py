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

# Define unit options for diameter
unit_options = {
    'Meters': ['meters.estimated_diameter_min', 'meters.estimated_diameter_max'],
    'Kilometers': ['kilometers.estimated_diameter_min', 'kilometers.estimated_diameter_max'],
    'Miles': ['miles.estimated_diameter_min', 'miles.estimated_diameter_max'],
    'Feet': ['feet.estimated_diameter_min', 'feet.estimated_diameter_max']
}

# Define options for relative velocity
velocity_options = {
    'relative_velocity_km/s': 'Velocity (km/s)',
    'relative_velocity_km/h': 'Velocity (km/h)',
    'relative_velocity_m/h': 'Velocity (m/h)'
}

# Define color options
color_options = ['red', 'green', 'blue', 'yellow', 'black', 'purple', 'lime', 'teal','orange', 'brown', 'olive']

app.layout = html.Div([
    html.H1("Interactive Asteroid Size Comparison", style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Select Unit for Asteroid Diameter:"),
                dcc.Dropdown(
                    id='unit-dropdown',
                    options=[{'label': k, 'value': k} for k in unit_options.keys()],
                    value='Meters',
                    style={'width': '100%'}
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Minimum Diameter:"),
                dcc.Slider(
                    id='min-size-slider',
                    min=0,  # Start from 0
                    max=1,  # Default max, will be updated by callback
                    step=0.1,  # Finer control
                    value=0,  # Initial value set to 0
                    marks={},  # Initial empty marks, will be updated by callback
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False  # This ensures that only the selected point is highlighted
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Maximum Diameter:"),
                dcc.Slider(
                    id='max-size-slider',
                    min=0,  # Start from 0
                    max=1,  # Default max, will be updated by callback
                    step=0.1,  # Finer control
                    value=1,  # Initial value set to max, will be updated by callback
                    marks={},  # Initial empty marks, will be updated by callback
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False  # This ensures that only the selected point is highlighted
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Select Unit for Relative Velocity:"),
                dcc.Dropdown(
                    id='velocity-dropdown',
                    options=[{'label': v, 'value': k} for k, v in velocity_options.items()],
                    value='relative_velocity_km/h',
                    style={'width': '100%'}
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Select Plot Size:"),
                dcc.Slider(
                    id='plot-size-slider',
                    min=200,
                    max=800,
                    step=50,
                    value=500,
                    marks={i: f'{i}px' for i in range(200, 801, 100)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    included=False  # This ensures that only the selected point is highlighted
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Color for Hazardous Asteroids:"),
                dcc.Dropdown(
                    id='hazardous-color-dropdown',
                    options=[{'label': color.capitalize(), 'value': color} for color in color_options],
                    value='red',
                    style={'width': '100%'}
                ),
            ], style={'padding': 10}),
            html.Div([
                html.Label("Color for Non-Hazardous Asteroids:"),
                dcc.Dropdown(
                    id='non-hazardous-color-dropdown',
                    options=[{'label': color.capitalize(), 'value': color} for color in color_options],
                    value='blue',
                    style={'width': '100%'}
                ),
            ], style={'padding': 10}),
        ], width=3),
        dbc.Col([
            dcc.Graph(id='size-comparison-plot', style={'height': '80vh'})
        ], width=9)
    ])
])

@app.callback(
    [Output('min-size-slider', 'max'),
     Output('min-size-slider', 'marks'),
     Output('min-size-slider', 'step'),
     Output('max-size-slider', 'max'),
     Output('max-size-slider', 'marks'),
     Output('max-size-slider', 'step'),
     Output('min-size-slider', 'value'),
     Output('max-size-slider', 'value')],
    Input('unit-dropdown', 'value')
)
def update_sliders(unit):
    min_col, max_col = unit_options[unit]
    max_min_diameter = final_df[min_col].max()
    max_max_diameter = final_df[max_col].max()

    step_min = max(1, max_min_diameter // 10)
    step_max = max(1, max_max_diameter // 10)

    # Use finer steps for kilometers and miles
    if unit in ['Kilometers', 'Miles']:
        step_min = 0.1
        step_max = 0.1
    
    min_marks = {i: str(i) for i in range(0, int(max_min_diameter) + 1, max(1, int(max_min_diameter) // 10))}
    max_marks = {i: str(i) for i in range(0, int(max_max_diameter) + 1, max(1, int(max_max_diameter) // 10))}
    
    return max_min_diameter, min_marks, step_min, max_max_diameter, max_marks, step_max, 0, max_max_diameter

@app.callback(
    Output('size-comparison-plot', 'figure'),
    [Input('unit-dropdown', 'value'), Input('min-size-slider', 'value'), Input('max-size-slider', 'value'), Input('velocity-dropdown', 'value'), Input('plot-size-slider', 'value'), Input('hazardous-color-dropdown', 'value'), Input('non-hazardous-color-dropdown', 'value')]
)
def update_plot(unit, min_size, max_size, velocity_unit, plot_size, hazardous_color, non_hazardous_color):
    min_col, max_col = unit_options[unit]
    
    df_filtered = final_df[
        (final_df[min_col] >= min_size) &
        (final_df[max_col] <= max_size)
    ]

    fig = px.scatter(
        df_filtered,
        x='absolute_magnitude_h',
        y=velocity_unit,
        size=min_col,
        color='is_potentially_hazardous_asteroid',
        symbol='is_potentially_hazardous_asteroid',
        size_max=15,
        color_discrete_map={
            True: hazardous_color,
            False: non_hazardous_color
        },
        title='<b>Comparison of Asteroid Sizes vs. Magnitude vs. Velocity</b>',
        labels={
            'absolute_magnitude_h': 'Asteroid Magnitude (Brightness)',
            velocity_unit: velocity_options[velocity_unit]
        }
    )

    fig.update_layout(
        legend_title_text='Hazardous?',
        xaxis_title='Asteroid Magnitude (Brightness)',
        yaxis_title=velocity_options[velocity_unit],
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=plot_size
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
