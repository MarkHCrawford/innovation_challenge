import pandas as pd
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.graph_objs import Scattergeo, Layout, Figure




link = "cuny_attendance.csv"
link_location = "college_location.csv"
df_location = pd.read_csv(link_location)

df = pd.read_csv(link, index_col=0)

df.dropna(inplace=True)
df = df[df["Enrollment Type Description"] == 'Total']

sorted_fall_terms = sorted(df['Fall Term'].unique())

merged_df = pd.merge(df, df_location, on='College Name', how='inner')

# Create the Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY, '/assets/styles.css'])

app.layout = html.Div([
    html.H1("College Data", style={'text-align': 'center'}),
    
    dbc.Card(
        dbc.CardBody([
            html.H3("Select a year to see the number of students enrolled:"),
            
            dcc.Dropdown(
                id='fall-term-dropdown',
                options=[{'label': year, 'value': year} for year in sorted_fall_terms],
                value=merged_df['Fall Term'].unique()[0],
                style={'color': 'black', 'background-color': 'white', 'margin': '30px'}
            ),
            
            dcc.Graph(id='college-histogram'),

            
        ])
    ),
    
    # 3D Scatter Plot added as a dcc.Graph component
    dcc.Graph(id='scatter-3d'),

])

# Define a callback to update the 3D Scatter Plot and histogram
@app.callback(
    Output('scatter-3d', 'figure'),
    Output('college-histogram', 'figure'),
    Input('fall-term-dropdown', 'value')
)
def update_figures(selected_year):
    filtered_df = merged_df[merged_df['Fall Term'] == selected_year]

    # Create the histogram
    fig_histogram = px.histogram(
        filtered_df, x='College Name', y='Head Count', title=f"College Data for {selected_year}", template='plotly_dark',
        color_discrete_sequence=['#98FB98']
    )
    fig_histogram.update_xaxes(title_text="College Name")
    fig_histogram.update_yaxes(title_text="Head Count")

    # Create the 3D Scatter Plot
    fig_3d = Figure(data=[Scattergeo(
        lon=filtered_df['Longitude'],
        lat=filtered_df['Latitude'],
        mode='markers',
        
        marker=dict(
            size=filtered_df['Head Count'] / 500,  # Adjust the size for visibility
            color=filtered_df['Head Count'],
            colorscale='Viridis',
            colorbar=dict(title='Head Count'),
        )
    )])
    fig_3d.update_geos(projection_scale=10)
    fig_3d.update_geos(fitbounds="locations")

    return fig_3d, fig_histogram  # Return 3D Scatter Plot and histogram

if __name__ == '__main__':
    app.run_server(debug=True)
