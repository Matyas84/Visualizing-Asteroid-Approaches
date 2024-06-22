import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load your data
final_df = pd.read_csv('final_df.csv')

# Process data to count asteroids per date
final_df['date'] = pd.to_datetime(final_df['date'])  # Ensure 'date' column is datetime
asteroid_counts = final_df.groupby(['date', 'is_potentially_hazardous_asteroid']).size().reset_index(name='count')

# Initialize the Dash app with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = html.Div([
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
                max=1.5,
                step=0.1,
                value=1,
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

# Callback to update the chart based on dropdown selection and sliders
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('hazard-dropdown', 'value'), Input('x-scale-slider', 'value'), Input('y-scale-slider', 'value')]
)
def update_chart(hazard_status, x_scale, y_scale):
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