# -*- coding: utf-8 -*-
"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
from fig_updater import fig_updater
from data import df, options

app = dash.Dash(__name__,suppress_callback_exceptions=True)
fig = fig_updater(df, xs=['dateRep'], ys=['cases']) 

main_layout = html.Div(id='main',children=[
    # dependent and independent variables (x- and y-axes)
    html.Div(style=dict(columnCount=3), children=[html.H6("Select x-axis"),
                                                  html.H6("Select y-axis"),
                                                  html.H6("Cartesian product")]),
    html.Div(style=dict(columnCount=3), children=[dcc.Dropdown(options=options, id='x-axis', multi=True, value=['dateRep']),
                                                  dcc.Dropdown(options=options, id='y-axis', multi=True, value=['cases']),
                                                  daq.ToggleSwitch(id='cartesian-prod',value=False)
                                                  ]),
    # legend options (symbol, size, color)
    html.Div(style=dict(columnCount=3), children=[html.H6("Select symbol"),
                                                  html.H6("Select size"),
                                                  html.H6("Select color")]),
    html.Div(style=dict(columnCount=3), children=[
        dcc.Dropdown(options=options, id='symbol'),
        dcc.Dropdown(options=options, id='size'),
        dcc.Dropdown(options=options, id='color')]),
    # hover data selection
    html.Div([html.H6("Select Hover Data"),
              dcc.Dropdown(options=options, id='hover-data', multi=True)]),
    html.Div([html.H6("Select smoothing fits"),
        dcc.RadioItems(options=[{'label':'Whittaker', 'value':'whittaker'}, 
                  {'label':'Moving Average', 'value':'moving-average'}, 
                  {'label':'None', 'value':'none'}], value='none', id='smoother'),
              html.Div(id='smoother-slider-container',children=[dcc.Slider(min=0,max=100,value=5,step=1,id='smoother-slider')])])  
    ])

graph_layout = dcc.Graph(figure=fig, id='plot')

aliasing_layout = html.Div(id='aliasing',
        children=[html.Div(style=dict(columnCount=3), 
                  children=[html.H6("Name"),
                            html.H6("Alias"),
                            html.H6("Alias History")]),
        html.Div(style=dict(columnCount=3), 
        children=[html.Div(children=[dcc.Dropdown(options=options, id='name')]),
        html.Div(children=[dcc.Input(id='alias', value='')]),
        html.Div(children=[dcc.Textarea(
                id='alias-history',
                value='',
                disabled=True)])
    ]),
    html.Div(html.Button(id='submit-alias', n_clicks=0, children='Submit')),
    ])

filtering_layout = html.Div(id='filtering',children=[html.H6("Not yet implemented")])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1(children='Plotly Graph Builder'),
    dcc.Link('/main', href='/main'),
    html.Br(),
    dcc.Link('/filtering', href='/filtering'),
    html.Br(),
    dcc.Link('/aliasing', href='/aliasing'),
    html.Div(id='page-content',children=[main_layout,aliasing_layout,filtering_layout,graph_layout])
])

show = {'height':'auto'}
hide = {'height':'0', 'overflow':'hidden','line-height':0,'display':'block'}
@app.callback([Output('main', 'style'),
    Output('filtering', 'style'),
    Output('aliasing', 'style')],
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main':
        return show, hide, hide
    elif pathname == '/filtering':
        return hide, show, hide
    elif pathname == '/aliasing':
        return hide, hide, show

@app.callback([Output('smoother-slider', 'min'),
    Output('smoother-slider', 'max'),
    Output('smoother-slider','value'),
    Output('smoother-slider','step'),
    Output('smoother-slider', 'marks'),
    Output('smoother-slider-container', 'style')],
    [Input('smoother','value')])
def update_smoother_slider(smoother):
    if smoother == 'none':
        return 0, 10, 5, 1, dict(), hide
    elif smoother == 'whittaker':
        marks = {k:{'label':f'10^{k}'} for k in range(6)}
        return 0, 5, 2, 0.1, marks, show
    elif smoother == 'moving-average':
        marks = {k:{'label':f'{k}'} for k in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]}
        return 1, 50, 15, 1, marks, show
        

@app.callback(
    Output('plot', 'figure'),
    [Input('x-axis', 'value'),
     Input('y-axis', 'value'),
     Input('symbol', 'value'),
     Input('size', 'value'),
     Input('color', 'value'),
     Input('hover-data', 'value'),
     Input('cartesian-prod','value'),
     Input('smoother', 'value'),
     Input('smoother-slider', 'value')
     ])
def update_fig(x, y, symbol, size, color, hover_data, cartesian_prod, smoother, smoother_slider):
    fig = fig_updater(df, x, y, 
            symbol=symbol, 
            size=size, 
            color=color, 
            hover_data=hover_data, 
            cartesian_prod=cartesian_prod,
            smoother=smoother,
            smoother_parameter=smoother_slider)
    fig.update_layout(transition_duration=500)
    return fig

# column aliasing
@app.callback(
    [Output('alias-history','value'),
     Output('x-axis','options'),
     Output('y-axis','options'),
     Output('symbol','options'),
     Output('size','options'),
     Output('color','options'),
     Output('hover-data','options')],
    Input('submit-alias', 'n_clicks'),
    [State('name','value'),
     State('alias','value'),
     State('alias-history','value')]
)
def update_aliases(submit_alias, name, alias, alias_history):
    if alias is not None and name is not None:
        options = [{'label':x, 'value':x} for x in df.columns if x != alias]
        df[alias] = df[name] 
        options.append({'label': alias, 'value': alias})
        return (alias_history + '\n' +
                f'{name}\t{alias}\t{submit_alias}',) + (options,) * 6


if __name__ == '__main__':
    app.run_server(debug=True)