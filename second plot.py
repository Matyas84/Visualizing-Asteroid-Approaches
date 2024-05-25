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

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Interactive Asteroid Size Comparison"),
    dcc.RangeSlider(
        id='size-range-slider',
        min=final_df['meters.estimated_diameter_min'].min(),
        max=final_df['meters.estimated_diameter_max'].max(),
        step=1,
        value=[100, 500],
        marks={i: '{}'.format(i) for i in range(int(final_df['meters.estimated_diameter_min'].min()), int(final_df['meters.estimated_diameter_max'].max()) + 1, 100)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    dcc.Graph(id='size-comparison-plot')
])

# Callback to update the scatter plot based on the selected size range
@app.callback(
    Output('size-comparison-plot', 'figure'),
    [Input('size-range-slider', 'value')]
)
def update_plot(size_range):
    min_size, max_size = size_range  # Corrected from 'size setsize_range'
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
        },
        hover_name='name'
    )

    fig.update_layout(
        legend_title_text='Hazardous?',
        xaxis_title='Asteroid Magnitude (Brightness)',
        yaxis_title='Velocity (km/h)',
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        gridcolor='lightgray'
    )
    
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

