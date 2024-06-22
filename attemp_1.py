import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import matplotlib.colors as mcolors
import datetime
import config
import nasa

# Initialize the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Data mapping for dropdowns in histogram
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

# Define unit options for scatter plot
unit_options = {
    'Meters': ['meters.estimated_diameter_min', 'meters.estimated_diameter_max'],
    'Kilometers': ['kilometers.estimated_diameter_min', 'kilometers.estimated_diameter_max'],
    'Miles': ['miles.estimated_diameter_min', 'miles.estimated_diameter_max'],
    'Feet': ['feet.estimated_diameter_min', 'feet.estimated_diameter_max']
}

# Define options for relative velocity in scatter plot
velocity_options = {
    'relative_velocity_km/s': 'Velocity (km/s)',
    'relative_velocity_km/h': 'Velocity (km/h)',
    'relative_velocity_m/h': 'Velocity (m/h)'
}

# Define color options
color_options = ['red', 'green', 'blue', 'yellow', 'black', 'purple', 'lime', 'teal','orange', 'brown', 'olive']

app.layout = html.Div([
    html.H1("Interactive Asteroid Data Visualization", style={'textAlign': 'center'}),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date_placeholder_text="Start Date",
        end_date_placeholder_text="End Date",
        display_format='YYYY-MM-DD'
    ),
    html.Div(id='output-container-date-picker-range', style={'textAlign': 'center'}),
    # dcc.Store stores the intermediate value
    dcc.Store(id='final-df'),

    dbc.Tabs([
        dbc.Tab(label='Histogram and Box Plot', children=[
            html.Div([
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': k, 'value': k} for k in data_choices.keys()],
                    value='Relative Velocity',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
                ),
                dcc.Dropdown(
                    id='type-dropdown',
                    value='relative_velocity_km/h',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
                ),
                dcc.Dropdown(
                    id='plot-type-dropdown',
                    options=[{'label': 'Histogram', 'value': 'Histogram'}, {'label': 'Box Plot', 'value': 'Box Plot'}],
                    value='Histogram',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
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
                html.Label("Select a Color:", style={'textAlign': 'center', 'marginTop': '20px'}),
                html.Div(
                    dbc.ButtonGroup(
                        [dbc.Button(style={'background-color': color, 'border': '1px solid black', 'width': '30px', 'height': '30px', 'border-radius': '50%', 'padding': '0', 'margin': '2px'}, id=color, n_clicks_timestamp=-1) for color in color_options],
                        id='color-buttons',
                        className="mr-2"
                    ), style={'textAlign': 'center'}
                ),
                html.Div([
                    html.Label("Color Transparency:", style={'textAlign': 'center', 'marginTop': '20px'}),
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
        ]),
        dbc.Tab(label='Scatter Plot', children=[
            html.Div([
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
                                min=0,
                                max=1,
                                step=0.1,
                                value=0,
                                marks={},
                                tooltip={"placement": "bottom", "always_visible": True},
                                included=False
                            ),
                        ], style={'padding': 10}),
                        html.Div([
                            html.Label("Maximum Diameter:"),
                            dcc.Slider(
                                id='max-size-slider',
                                min=0,
                                max=1,
                                step=0.1,
                                value=1,
                                marks={},
                                tooltip={"placement": "bottom", "always_visible": True},
                                included=False
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
                                included=False
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
        ]),
        dbc.Tab(label='Bar Chart', children=[
            html.Div([
                html.H1("Asteroid Count per Day", style={'textAlign': 'center'}),
                html.Div([
                    html.Div([
                        html.Label("Hazardous Asteroid:", style={'textAlign': 'center', 'marginTop': '20px'}),
                        dcc.Dropdown(
                            id='hazard-dropdown',
                            options=[
                                {'label': 'Both', 'value': 'both'},
                                {'label': 'True', 'value': 'True'},
                                {'label': 'False', 'value': 'False'}
                            ],
                            value='both',
                            style={'width': '100%', 'marginTop': '10px'},
                            placeholder="Select Hazardous Asteroid Status"
                        ),
                    ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.Label("X-Axis Scale:", style={'textAlign': 'center'}),
                        dcc.Slider(
                            id='x-scale-slider',
                            min=0.5,
                            max=1.6,
                            step=0.1,
                            value=1.2,
                            marks={i / 10: str(i / 10) for i in range(5, 21, 5)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            included=False
                        ),
                        html.Label("Y-Axis Scale:", style={'textAlign': 'center', 'marginTop': '20px'}),
                        dcc.Slider(
                            id='y-scale-slider',
                            min=1,
                            max=3,
                            step=0.1,
                            value=1.1,
                            marks={i / 10: str(i / 10) for i in range(10, 31, 10)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            included=False
                        ),
                    ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '5%'})
                ], style={'width': '70%', 'margin': 'auto', 'marginTop': '20px', 'display': 'flex', 'justifyContent': 'space-between'}),
                dcc.Graph(id='bar-chart', style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'})
            ])
        ])
    ])
])

# Callbacks for setting dynamic dropdown and plots in histogram
@app.callback(
    Output('final-df', 'data'),
    Output('output-container-date-picker-range', 'children'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_output(start_date_input, end_date_input):
    if start_date_input and end_date_input:
        final_df = nasa.download_data(start_date_input, end_date_input)
        return final_df.to_dict(), f"Pocet: {len(final_df)}"

    return None, "Choose the range please!"

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
    [Input('final-df', 'data'), Input('type-dropdown', 'value'), Input('plot-type-dropdown', 'value'), Input('bins-slider', 'value'), Input('transparency-slider', 'value')] + [Input(color, 'n_clicks_timestamp') for color in color_options]
)
def update_plot(final_df, selected_type, plot_type, bins, transparency, *args):
    if final_df is None:
        return {}

    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
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

# Callbacks for scatter plot
@app.callback(
    [Output('min-size-slider', 'max'),
     Output('min-size-slider', 'marks'),
     Output('min-size-slider', 'step'),
     Output('max-size-slider', 'max'),
     Output('max-size-slider', 'marks'),
     Output('max-size-slider', 'step'),
     Output('min-size-slider', 'value'),
     Output('max-size-slider', 'value')],
    [Input('final-df', 'data'), Input('unit-dropdown', 'value')]
)
def update_sliders(final_df, unit):
    if final_df is None:
        return 1, {}, 0.1, 1, {}, 0.1, 0, 1

    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
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
    [Input('final-df', 'data'), Input('unit-dropdown', 'value'), Input('min-size-slider', 'value'), Input('max-size-slider', 'value'), Input('velocity-dropdown', 'value'), Input('plot-size-slider', 'value'), Input('hazardous-color-dropdown', 'value'), Input('non-hazardous-color-dropdown', 'value')]
)
def update_plot_scatter(final_df, unit, min_size, max_size, velocity_unit, plot_size, hazardous_color, non_hazardous_color):
    if final_df is None:
        return {}

    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
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

# Callback to update the bar chart based on dropdown selection and sliders
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('final-df', 'data'), Input('hazard-dropdown', 'value'), Input('x-scale-slider', 'value'), Input('y-scale-slider', 'value')]
)
def update_chart(final_df, hazard_status, x_scale, y_scale):
    if final_df is None:
        return {}

    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
    final_df['date'] = pd.to_datetime(final_df['date'])
    asteroid_counts = final_df.groupby(['date', 'is_potentially_hazardous_asteroid']).size().reset_index(name='count')

    if hazard_status == 'both':
        filtered_df = asteroid_counts
    else:
        filtered_df = asteroid_counts[asteroid_counts['is_potentially_hazardous_asteroid'] == (hazard_status == 'True')]

    # Create bar chart
    fig = px.bar(filtered_df, x='date', y='count', color='is_potentially_hazardous_asteroid',
                 labels={'count': 'Asteroid Count', 'date': 'Date', 'is_potentially_hazardous_asteroid': 'Hazardous'},
                 title='Daily Asteroid Counts')

    # Update colors
    if hazard_status == 'True':
        fig.update_traces(marker_color='red')
    elif hazard_status == 'False':
        fig.update_traces(marker_color='blue')

    # Update axis ranges and scaling
    fig.update_xaxes(range=[filtered_df['date'].min(), filtered_df['date'].max()])
    fig.update_yaxes(range=[0, filtered_df['count'].max() * y_scale])
    fig.update_layout(
        title={'font': {'size': 20}},
        xaxis_title="Date",
        yaxis_title="Asteroid Count",
        xaxis={'tickformat': '%Y-%m-%d'},
        xaxis_tickangle=-45
    )
    fig.update_layout(
        autosize=False,
        width=800 * x_scale,
        height=600,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)