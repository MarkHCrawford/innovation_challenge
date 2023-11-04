import pandas as pd
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.graph_objs import Scattergeo, Layout, Figure



# csvs and data frame creation
link = "cuny_attendance.csv"
link_location = "college_location.csv"
link_ret = "cuny_retention.csv"
df_ret = pd.read_csv(link_ret)
df_ret = df_ret.dropna()
df_location = pd.read_csv(link_location)
mask = df_ret['Record Type Description'] == '1 Year Retention'
filtered_df_ret = df_ret[mask]
filtered_df_ret = filtered_df_ret.sort_values(by='Fall Term', ascending=True)
df = pd.read_csv(link, index_col=0)
df.dropna(inplace=True)
df = df[df["Enrollment Type Description"] == 'Total']
sorted_fall_terms = sorted(df['Fall Term'].unique())
merged_df = pd.merge(df, df_location, on='College Name', how='inner')



# Dash declaration, bootstrap import
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY, '/assets/styles.css'])


# app layout
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
        ]),
    ),
    dbc.Card(
        dbc.CardBody([
            html.H3("Select a college to see the retention rate:"),
            dcc.Dropdown(
                id='college-dropdown',
                options=[{'label': college, 'value': college} for college in filtered_df_ret['College'].unique()],
                value=filtered_df_ret['College'].unique()[0],
                style={'color': 'black', 'background-color': 'white', 'margin': '30px'}
            ),
            dcc.Graph(id='college-line-chart'),
        ]),
    ),
# kepler map
    html.Iframe(
        src="https://kepler.gl/demo/map?mapUrl=https://dl.dropboxusercontent.com/scl/fi/lqhmzzw3ydnxril95tvs8/keplergl_ve6gzsq.json?rlkey=rapifpf57wsenpe3648m5uxsc&dl=0",
        width="100%",
        height="500px",  # Adjust the height as needed
        style={"border": "none"}  # You can customize the iframe styles as needed
    ),
    
])

# Define a callback to update the 3D Scatter Plot and histogram
@app.callback(
    Output('college-histogram', 'figure'),
    Output('college-line-chart', 'figure'),
    Input('fall-term-dropdown', 'value'),
    Input('college-dropdown', 'value')
)
def update_figures(selected_year, selected_college):
    filtered_df = merged_df[merged_df['Fall Term'] == selected_year]

    # plotly histogram
    fig_histogram = px.histogram(
        filtered_df, x='College Name', y='Head Count', title=f"College Data for {selected_year}", template='plotly_dark',
        color_discrete_sequence=['#98FB98']
    )
    fig_histogram.update_xaxes(title_text="College Name")
    fig_histogram.update_yaxes(title_text="Head Count")

    # Create the 3D Scatter Plot
    
    # Create the line chart for the selected college
    filtered_df_college = filtered_df_ret[filtered_df_ret['College'] == selected_college]
    fig_line_chart = px.line(
        filtered_df_college, x='Fall Term', y='Percentage', title=f"Retention Data for {selected_college}",
        labels={'Fall Term': 'Fall Term', 'Percentage': 'Percentage'},
        template='plotly_dark'
    )

    return fig_histogram, fig_line_chart

if __name__ == '__main__':
    app.run_server(debug=True)

