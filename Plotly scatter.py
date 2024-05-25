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

# Determine the maximum values for the sliders based on your data
max_min_diameter = int(final_df['meters.estimated_diameter_min'].max())
max_max_diameter = int(final_df['meters.estimated_diameter_max'].max())

app.layout = html.Div([
    html.H1("Interactive Asteroid Size Comparison"),
    html.Div([
        html.Label("Minimum Diameter (meters):"),
        dcc.Slider(
            id='min-size-slider',
            min=0,  # Start from 0
            max=max_min_diameter,  # Max from the min diameter column
            step=1,
            value=0,  # Initial value set to 0
            marks={i: str(i) for i in range(0, max_min_diameter + 1, max_min_diameter // 10)},
            tooltip={"placement": "bottom", "always_visible": True},
            included=False  # This ensures that only the selected point is highlighted
        ),
    ], style={'padding': 20}),
    html.Div([
        html.Label("Maximum Diameter (meters):"),
        dcc.Slider(
            id='max-size-slider',
            min=0,  # Start from 0
            max=max_max_diameter,  # Max from the max diameter column
            step=1,
            value=max_max_diameter,  # Initial value set to the max
            marks={i: str(i) for i in range(0, max_max_diameter + 1, max_max_diameter // 10)},
            tooltip={"placement": "bottom", "always_visible": True},
            included=False  # This ensures that only the selected point is highlighted
        ),
    ], style={'padding': 20}),
    dcc.Graph(id='size-comparison-plot')
])

@app.callback(
    Output('size-comparison-plot', 'figure'),
    [Input('min-size-slider', 'value'), Input('max-size-slider', 'value')]
)
def update_plot(min_size, max_size):
    df_filtered = final_df[
        (final_df['meters.estimated_diameter_min'] >= min_size) &
        (final_df['meters.estimated_diameter_max'] <= max_size)
    ]

    fig = px.scatter(
        df_filtered,
        x='absolute_magnitude_h',
        y='relative_velocity_km/h',
        size='meters.estimated_diameter_min',
        color='is_potentially_hazardous_asteroid',
        symbol='is_potentially_hazardous_asteroid',
        size_max=15,
        color_continuous_scale='Viridis',
        title='Comparison of Asteroid Sizes vs. Magnitude vs. Velocity',
        labels={
            'absolute_magnitude_h': 'Asteroid Magnitude (Brightness)',
            'relative_velocity_km/h': 'Velocity (km/h)'
        }
    )

    fig.update_layout(
        legend_title_text='Hazardous?',
        xaxis_title='Asteroid Magnitude (Brightness)',
        yaxis_title='Velocity (km/h)',
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
