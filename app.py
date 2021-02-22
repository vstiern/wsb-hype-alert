"""Plotly Dash app."""

import dash 
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input

from src.data_functions import cold_start_initization, get_app_data, get_new_reddit_data


# collect initial data
cold_start_initization()

# get data from db
df, tickers = get_app_data()
print(f"Data initialized. Nr of rows: {len(df)}")

# define app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# app layout
app.layout = html.Div([

    # app title
    html.Div([
            html.H1(children= "Don't believe the Hype! - the r/wallstreetbets Ticker Alert Dashboard!",
                    style={"text-align": "center", "font-size":"200%", 'font-weight': 'bold', "color":"black"}),
        	html.Div(children="[Collects and updates new data every 5min]", 
                     style={"text-align": "center", 'width':'100%', 'font-weight': 'bold', "color":"black"})
	# Position 1, descritpion
        ]),

    # dropdown menu for ticker selection
    html.Div([
        html.Label(['Ticker selection (top 10):'], style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id="dropdown",
            options=[{"label": x, "value": x} for x in tickers],
            value=tickers,
            multi=True,
            style={"width": "75%"}
        ),
    ]),

    # radio button for y-axis of aggreage bar chart
    html.Div([
            html.Br(),
            html.Label(['Y-axis selection:'], style={'font-weight': 'bold'}),
            dcc.RadioItems(
                id='yaxis_raditem',
                options=[
                         {'label': 'Ticker comment mentions (Count)', 'value': 'count'},
                         {'label': 'Ticker comment score (Sum)', 'value': 'score'},
                ],
                value='count',
                style={"width": "50%"}
            ),
        ]),

    # graphs
    html.Div([
        # data update -> new reddit data every 5min
        dcc.Interval(
                    id='my_interval',
                    disabled=False,         # if True, the counter will no longer update
                    interval=5*60*1000,     # increment the counter n_intervals every interval milliseconds
                    n_intervals=1,          # number of times the interval has passed
                    max_intervals=-1,       # number of times the interval will be fired.
                                            # if -1, then the interval has no limit (the default)
                                            # and if 0 then the interval stops running.
        ),
        # aggreaged bar graph
        dcc.Graph(id='bar-graph', figure={}, clickData=None, hoverData=None,
                  config={
                      'staticPlot': False,     # True, False
                      'scrollZoom': False,     # True, False
                      'doubleClick': 'reset',  # 'reset', 'autosize' or 'reset+autosize', False
                      'displayModeBar': True,  # True, False, 'hover'
                      'watermark': True,       
                  },
                  className='ticker count'
                ),
        # timeseries graph
        dcc.Graph(id='ts-graph', figure={}, className='ticker count')        # timeseries with count per date
    ]),
    
    # hidden section for data update
    html.Div(id="last-update", style={"display": "none"})
])

# callback for bar graph
@app.callback(
    Output(component_id='bar-graph', component_property='figure'),
    Input(component_id='dropdown', component_property='value'),
    Input(component_id='yaxis_raditem', component_property='value'),
    Input(component_id='last-update', component_property='children')
)
def update_bar_chart(tickers, y_axis, jsonified_data):
    """Filter aggregate bar chart for selected tickers and y-axis."""
    df = pd.read_json(jsonified_data, orient='split')
    dff = df[df["ticker"].isin(tickers)]
    dff = dff.groupby(["name", "ticker"])[y_axis].sum().nlargest(10).reset_index()
    fig = px.bar(dff, x="name", y=y_axis, color="ticker")
    return fig

# callback for timeseries graph
@app.callback(
    Output(component_id='ts-graph', component_property='figure'),
    Input(component_id='bar-graph', component_property='hoverData'),
    Input(component_id='bar-graph', component_property='clickData'),
    Input(component_id='yaxis_raditem', component_property='value'),
    Input(component_id='last-update', component_property='children')
)
def update_ts_graph(hov_data, clk_data, y_axis, jsonified_data):
    """Filter datetime bar chart for selected ticker and y-axis."""
    df = pd.read_json(jsonified_data, orient='split')
    if hov_data is None:
        dff2 = df[df["ticker"] == tickers[0]]
        fig2 = px.bar(dff2, x="date_hour", y=y_axis, color="ticker", 
                      title=f'Mentions {y_axis} per date_hour for {tickers[0]}')
        return fig2
    else:
        hov_name = hov_data['points'][0]['x']
        dff2 = df[df.name == hov_name]
        fig2 = px.bar(dff2,  x="date_hour", y=y_axis, color="ticker", 
                      color_discrete_sequence=px.colors.qualitative.G10,
                      title=f'Mentions {y_axis} per date_hour for {hov_name}')
        return fig2

# callback for new reddit data
@app.callback(
    Output(component_id='last-update', component_property='children'),
    Input(component_id='my_interval', component_property='n_intervals')
)
def refresh_data(value):
    """Update data for graphs."""
    get_new_reddit_data()
    df, tickers = get_app_data()
    print(f"Data updated. Nr of rows: {len(df)}")
    j_df = df.to_json(date_format='iso', orient='split')
    return j_df


if __name__ == "__main__":
    app.run_server(debug=False)