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
import webbrowser
import threading


# Initialize the Dash app with Bootstrap styles for a responsive and visually appealing layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Data mapping for dropdowns in the histogram and box plot tab
# This dictionary maps user-friendly category names to their corresponding DataFrame column names
data_choices = {
    'Relative Velocity': {
        'Displayed in km/s': 'relative_velocity_km/s',
        'Displayed in km/h': 'relative_velocity_km/h',
        'Displayed in m/h': 'relative_velocity_m/h'
    },
    'Estimated Diameter Minimum': {
        'Kilometers': 'kilometers.estimated_diameter_min',
        'Meters': 'meters.estimated_diameter_min',
        'Miles': 'miles.estimated_diameter_min',
        'Feet': 'feet.estimated_diameter_min'
    },
    'Estimated Diameter Maximum': {
        'Kilometers': 'kilometers.estimated_diameter_max',
        'Meters': 'meters.estimated_diameter_max',
        'Miles': 'miles.estimated_diameter_max',
        'Feet': 'feet.estimated_diameter_max'
    },
    'Miss Distance': {
        'Astronomical': 'miss_dist_astromnomical',
        'Lunar': 'miss_dist_lunar',
        'Kilometers': 'miss_dist_km',
        'Miles': 'miss_dist_miles'
    }
}

# Define unit options for scatter plot
# This dictionary defines the units available for asteroid diameter measurements
unit_options = {
    'Meters': ['meters.estimated_diameter_min', 'meters.estimated_diameter_max'],
    'Kilometers': ['kilometers.estimated_diameter_min', 'kilometers.estimated_diameter_max'],
    'Miles': ['miles.estimated_diameter_min', 'miles.estimated_diameter_max'],
    'Feet': ['feet.estimated_diameter_min', 'feet.estimated_diameter_max']
}

# Define options for relative velocity in the scatter plot
# This dictionary maps column names to user-friendly labels for velocity
velocity_options = {
    'relative_velocity_km/s': 'Velocity (km/s)',
    'relative_velocity_km/h': 'Velocity (km/h)',
    'relative_velocity_m/h': 'Velocity (m/h)'
}

# List of color options available for customization of the plots
color_options = ['red', 'green', 'blue', 'yellow', 'black', 'purple', 'lime', 'teal', 'grey', 'brown', 'olive']

# Layout definition for the Dash application
app.layout = html.Div([
    html.H1("Interactive Asteroid Data Visualization", style={'textAlign': 'center'}),
    
    # Date picker for selecting the date range of interest
    html.Div([
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format='YYYY-MM-DD'
        ),
    ], style={
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
        "margin": "20px"
    }),
    
    # Container to display the number of asteroids in the selected date range
    html.Div(id='output-container-date-picker-range', style={'textAlign': 'center'}),
    
    # Store component to hold the processed data for use in callbacks
    dcc.Store(id='final-df'),

    # Tabs for different types of visualizations
    dbc.Tabs([
        
        # Tab for Histogram and Box Plot
        dbc.Tab(label='Histogram and Box Plot', children=[
            html.Div([
                # Dropdown for selecting the data category (e.g. Relative Velocity, Estimated Diameter etc.)
                dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': k, 'value': k} for k in data_choices.keys()],
                    value='Relative Velocity',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
                ),
                # Dropdown for selecting the specific type within the selected category
                dcc.Dropdown(
                    id='type-dropdown',
                    value='relative_velocity_km/h',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
                ),
                # Dropdown for selecting the plot type (Histogram or Box Plot)
                dcc.Dropdown(
                    id='plot-type-dropdown',
                    options=[{'label': 'Histogram', 'value': 'Histogram'}, {'label': 'Box Plot', 'value': 'Box Plot'}],
                    value='Histogram',
                    style={'width': '70%', 'margin': 'auto', 'marginTop': '20px'}
                ),
                # Slider for selecting the number of bins in the histogram
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
                
                # Color selection buttons
                html.Label("Select a Color:", style={'textAlign': 'center', 'marginTop': '20px'}),
                html.Div(
                    dbc.ButtonGroup(
                        [dbc.Button(style={'background-color': color, 'border': '1px solid black', 'width': '30px', 'height': '30px', 'border-radius': '50%', 'padding': '0', 'margin': '2px'}, id=color, n_clicks_timestamp=-1) for color in color_options],
                        id='color-buttons',
                        className="mr-2"
                    ), style={'textAlign': 'center'}
                ),
                
                # Slider for adjusting the color transparency
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
        
        # Tab for Scatter Plot
        dbc.Tab(label='Scatter Plot', children=[
            html.Div([
                html.H1("Interactive Asteroid Size Comparison", style={'textAlign': 'center'}),
                dbc.Row([
                    dbc.Col([
                        # Dropdown for selecting the unit of asteroid diameter
                        html.Div([
                            html.Label("Select Unit for Asteroid Diameter:"),
                            dcc.Dropdown(
                                id='unit-dropdown',
                                options=[{'label': k, 'value': k} for k in unit_options.keys()],
                                value='Meters',
                                style={'width': '100%'}
                            ),
                        ], style={'padding': 10}),
                        
                        # Slider for setting the minimum diameter filter
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
                        
                        # Slider for setting the maximum diameter filter
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
                        
                        # Dropdown for selecting the unit of relative velocity
                        html.Div([
                            html.Label("Select Unit for Relative Velocity:"),
                            dcc.Dropdown(
                                id='velocity-dropdown',
                                options=[{'label': v, 'value': k} for k, v in velocity_options.items()],
                                value='relative_velocity_km/h',
                                style={'width': '100%'}
                            ),
                        ], style={'padding': 10}),
                        
                        # Slider for adjusting the size of the scatter plot
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
                        
                        # Dropdown for selecting the color of hazardous asteroids
                        html.Div([
                            html.Label("Color for Hazardous Asteroids:"),
                            dcc.Dropdown(
                                id='hazardous-color-dropdown',
                                options=[{'label': color.capitalize(), 'value': color} for color in color_options],
                                value='red',
                                style={'width': '100%'}
                            ),
                        ], style={'padding': 10}),
                        
                        # Dropdown for selecting the color of non-hazardous asteroids
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
        
        # Tab for Bar Chart
        dbc.Tab(label='Bar Chart', children=[
            html.Div([
                html.H1("Asteroid Count per Day", style={'textAlign': 'center'}),
                html.Div([
                    # Dropdown for selecting the hazardous status filter
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
                    
                    # Sliders for adjusting the scale of the axes in the bar chart
                    html.Div([
                        html.Label("X-Axis Scale:", style={'textAlign': 'center'}),
                        dcc.Slider(
                            id='x-scale-slider',
                            min=0.5,
                            max=2,
                            step=0.1,
                            value=1.2,
                            marks={i / 10: str(i / 10) for i in range(5, 21, 5)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            included=False
                        ),
                        html.Label("Y-Axis Scale:", style={'textAlign': 'center', 'marginTop': '20px'}),
                        dcc.Slider(
                            id='y-scale-slider',
                            min=0.5,
                            max=3,
                            step=0.1,
                            value=1.2,
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

# Callback to update data based on selected date range, automatically update certain parts of the app in response to user inputs, without needing to reload the entire page.
@app.callback(
    Output('final-df', 'data'),
    Output('output-container-date-picker-range', 'children'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'))
def update_output(start_date_input, end_date_input):
    # Download data from NASA API based on selected date range
    if start_date_input and end_date_input:
        final_df = nasa.download_data(start_date_input, end_date_input)
        return final_df.to_dict(), f"Count of Asteroids: {len(final_df)}"
    return None, "Choose the range please!"

# Callback to update type options based on selected category
@app.callback(
    Output('type-dropdown', 'options'),
    Input('category-dropdown', 'value')
)
def set_type_options(selected_category):
    # Update the options in the type dropdown based on the selected category
    return [{'label': k, 'value': v} for k, v in data_choices[selected_category].items()]

# Callback to set default value for type dropdown
@app.callback(
    Output('type-dropdown', 'value'),
    Input('type-dropdown', 'options')
)
def set_type_value(available_options):
    # Set the default value of the type dropdown to the first option available
    return available_options[0]['value']

# Callback to toggle visibility of bins slider based on plot type
@app.callback(
    Output('bins-slider-div', 'style'),
    Input('plot-type-dropdown', 'value')
)
def toggle_bins_slider(plot_type):
    # Show or hide the bins slider based on the selected plot type (Histogram or Box Plot)
    if plot_type == 'Histogram':
        return {'padding': 20, 'display': 'block', 'width': '70%', 'margin': 'auto'}
    else:
        return {'padding': 20, 'display': 'none', 'width': '70%', 'margin': 'auto'}

# Callback to update the histogram or box plot based on user inputs
@app.callback(
    Output('dynamic-plot', 'figure'),
    [Input('final-df', 'data'), 
     Input('type-dropdown', 'value'), 
     Input('plot-type-dropdown', 'value'), 
     Input('bins-slider', 'value'), 
     Input('transparency-slider', 'value')] + [Input(color, 'n_clicks_timestamp') for color in color_options]
)
def update_plot(final_df, selected_type, plot_type, bins, transparency, *args):
    # Check if the data is actually available
    if final_df is None:
        return {}

    # Convert the data from dictionary to DataFrame
    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
    
    # Get the context of the triggered callback to determine the selected color
    ctx = dash.callback_context

    if not ctx.triggered:
        selected_color = 'green'  # Default color if no button has been clicked
    else:
        # Determine the most recently clicked color button
        timestamps = {color: ctx.inputs.get(f'{color}.n_clicks_timestamp', -1) for color in color_options}
        selected_color = max(timestamps, key=timestamps.get)

    # Convert the selected color to RGBA format with transparency
    rgba_color = mcolors.to_rgba(selected_color, alpha=transparency)

    # Ensure selected_type column is numeric
    if final_df[selected_type].dtype == 'object':
        final_df[selected_type] = pd.to_numeric(final_df[selected_type], errors='coerce')

    # Generate the appropriate plot based on the selected plot type
    if plot_type == 'Histogram':
        fig = px.histogram(final_df, x=selected_type, nbins=bins, title=f'<b>Distribution of {selected_type}</b>')
    else:
        fig = px.box(final_df, x=selected_type, title=f'<b>Distribution of {selected_type}</b>')

    # Update marker color with transparency
    fig.update_traces(marker=dict(color=f'rgba{rgba_color}'))

    # Update layout for better visualization
    fig.update_layout(title={'font': {'size': 20}})

    return fig

# Callback to update slider parameters for scatter plot based on selected unit
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

    # Convert the data from dictionary to DataFrame
    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
    
    # Get the columns for the selected unit
    min_col, max_col = unit_options[unit]
    max_min_diameter = final_df[min_col].max()
    max_max_diameter = final_df[max_col].max()

    # Determine the step size for the sliders
    step_min = max(1, max_min_diameter // 10)
    step_max = max(1, max_max_diameter // 10)

    # Use finer steps for kilometers and miles
    if unit in ['Kilometers', 'Miles']:
        step_min = 0.1
        step_max = 0.1
    
    # Create marks for the sliders
    min_marks = {i: str(i) for i in range(0, int(max_min_diameter) + 1, max(1, int(max_min_diameter) // 10))}
    max_marks = {i: str(i) for i in range(0, int(max_max_diameter) + 1, max(1, int(max_max_diameter) // 10))}
    
    return max_min_diameter, min_marks, step_min, max_max_diameter, max_marks, step_max, 0, max_max_diameter

# Callback to update the scatter plot based on user inputs
@app.callback(
    Output('size-comparison-plot', 'figure'),
    [Input('final-df', 'data'), 
     Input('unit-dropdown', 'value'), 
     Input('min-size-slider', 'value'), 
     Input('max-size-slider', 'value'), 
     Input('velocity-dropdown', 'value'), 
     Input('plot-size-slider', 'value'), 
     Input('hazardous-color-dropdown', 'value'), 
     Input('non-hazardous-color-dropdown', 'value')]
)
def update_plot_scatter(final_df, unit, min_size, max_size, velocity_unit, plot_size, hazardous_color, non_hazardous_color):
    # Check if the data is available
    if final_df is None:
        return {}

    # Convert the data from dictionary to DataFrame
    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
    
    # Get the columns for the selected unit
    min_col, max_col = unit_options[unit]

    # Ensure the columns are numeric
    final_df[min_col] = pd.to_numeric(final_df[min_col], errors='coerce')
    final_df[max_col] = pd.to_numeric(final_df[max_col], errors='coerce')
    final_df[velocity_unit] = pd.to_numeric(final_df[velocity_unit], errors='coerce')
    final_df['absolute_magnitude_h'] = pd.to_numeric(final_df['absolute_magnitude_h'], errors='coerce')
    
    # Filter the DataFrame based on the selected size range
    df_filtered = final_df[
        (final_df[min_col] >= min_size) &
        (final_df[max_col] <= max_size)
    ]

    # Create the scatter plot
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

    # Update layout for better visualization
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
    [Input('final-df', 'data'), 
     Input('hazard-dropdown', 'value'), 
     Input('x-scale-slider', 'value'), 
     Input('y-scale-slider', 'value')]
)
def update_chart(final_df, hazard_status, x_scale, y_scale):
    if final_df is None:
        return {}

    # Convert the data from dictionary to DataFrame
    final_df = pd.DataFrame.from_dict(final_df, orient="columns")
    
    # Convert 'date' column to datetime
    final_df['date'] = pd.to_datetime(final_df['date'])
    
    # Group by date and hazardous status to get the count of asteroids
    asteroid_counts = final_df.groupby(['date', 'is_potentially_hazardous_asteroid']).size().reset_index(name='count')

    # Filter the DataFrame based on the selected hazardous status
    if hazard_status == 'both':
        filtered_df = asteroid_counts
    else:
        filtered_df = asteroid_counts[asteroid_counts['is_potentially_hazardous_asteroid'] == (hazard_status == 'True')]

    # Create the bar chart
    fig = px.bar(filtered_df, x='date', y='count', color='is_potentially_hazardous_asteroid',
                 labels={'count': 'Asteroid Count', 'date': 'Date', 'is_potentially_hazardous_asteroid': 'Hazardous'},
                 title='Daily Asteroid Counts')

    # Update colors based on the selected hazardous status
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


# Defining a function to open the browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")


# Run the Dash server
if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run_server(debug=True)
