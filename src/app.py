'''
Sofia Usmani

Link to deployment: 

'''


import dash
from dash import dcc, html, Input,Output,State
import seaborn as sns
import plotly.express as px
from dash.exceptions import PreventUpdate
import io
import base64
import pandas as pd

df = pd.read_csv('assets/ProcessedTweets.csv')
df.to_csv("pt.csv")


dropdown = html.Div(
    className="dropdown_div",
    style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'},
    children=[
        html.P("Month: ", style={'marginRight': '5px'}),
        dcc.Dropdown(
            id='month_dropdown',
            options=[{'label': month, 'value': month} for month in df['Month'].unique()],
            value=None,
            style={'width': '150px', 'marginLeft': '2px', 'marginRight':'px'}
        )
    ]
)
rangeslider1 = html.Div(
    style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'},
    children=[
        html.P("Sentiment Score: ", style={'marginRight': '5px', 'marginLeft':'5px'}),
        html.Div(
            dcc.RangeSlider(
                id='range_slider_sent',
                min=df['Sentiment'].min(),
                max=df['Sentiment'].max(),
                step=0.1,
                marks={-1: '-1', 1:'1'},
                value=[-1, 1],
            ),
            style={'width': '150pt', 'marginLeft': '2px'}  # Set width of the slider container
        ),
        html.Div(id='slider_sentiment')
    ],
    className="rangeslider_div"
)


rangeslider2 = html.Div(
    style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'center'},
    children=[
        html.P("Subjectivity Score: ", style={'marginRight': '5px'}),
        html.Div(
            dcc.RangeSlider(
                id='range_slider_subj',
                min=df['Subjectivity'].min(),
                max=df['Subjectivity'].max(),
                step=0.1,
                marks={i: str(i) for i in range(10)},
                value=[0, 1],
            ),
            style={'width': '150pt', 'marginLeft': '2px'}  # Set width of the slider container
        ),
        html.Div(id='slider_subjectivity')
    ],
    className="rangeslider_div"
)


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(className="parent_container", children=[
    html.Div(id="row1", children=[html.Div([dropdown, rangeslider1, rangeslider2], style={'width':'100%', 'align-items': 'center', 'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'})]),
    html.Div(id="row2", children=[html.Div(dcc.Graph(id='graph1', style={'width': '100%'}, config={'staticPlot': False}), style=dict(width="100%"))]),
    html.Div(id="row3", children=[html.Plaintext("Raw Tweets")]), 
    html.Div(id="row4", children=[html.Plaintext(id='table', style={'width': '100%', 'justify-content':'center', 'white-space': 'pre-wrap', 'text-align': 'center'})]) 
])

@app.callback(Output('graph1', 'figure'), [Input('month_dropdown', 'value'), Input('range_slider_sent', 'value'), Input('range_slider_subj', 'value')])
def update_graph1(month, sent, subj):
    
    if(month is None):
        raise PreventUpdate
    else:
        filtered_df = df[df['Month']==month]
        if sent is not None:
            filtered_df = filtered_df[(filtered_df['Sentiment'] >= sent[0]) & (filtered_df['Sentiment'] <= sent[1])]
        if subj is not None:
            filtered_df = filtered_df[(filtered_df['Subjectivity'] >= subj[0]) & (filtered_df['Subjectivity'] <= subj[1])]

        figure = px.scatter(filtered_df, x='Dimension 1', y='Dimension 2')
        figure.update_traces(marker=dict(color='gray'))
        figure.update_xaxes(title_text='', showticklabels=False)
        figure.update_yaxes(title_text='', showticklabels=False)
        
        return figure


@app.callback(Output('table', 'children'),Input('graph1', 'selectedData'),State('table', 'children'))
def update_output(selectedData, current_output):
    if selectedData is None:
        raise PreventUpdate
    
    indices = [point['pointIndex'] for point in selectedData['points']]
    selected_tweets = df.loc[indices, 'RawTweet']
    tweet_elements = [html.P(tweet) for tweet in selected_tweets]
    return tweet_elements


if __name__ == '__main__':
    app.run_server(debug=True)