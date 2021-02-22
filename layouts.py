import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from data import options, dlists

show = {'height':'auto'}
hide = {'height':'0', 'overflow':'hidden','line-height':0,'display':'block'}

main_layout = html.Div(id='main',children=[
    # dependent and independent variables (x- and y-axes)
    html.Div(style=dict(columnCount=3), children=[html.H6("Select x-axis"),
                                                  html.H6("Select y-axis"),
                                                  html.H6("Cartesian product")]),
    html.Div(style=dict(columnCount=3), children=[dcc.Dropdown(options=options, id='x-axis', multi=True, value=['dateRep']),
                                                  dcc.Dropdown(options=options, id='y-axis', multi=True, value=['cases_weekly']),
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

filtering_layout = html.Div(id='filtering',children=[
        html.Button("Add Filter", id="add-filter", n_clicks=0),
        html.Div(id='dropdown-container', children=[]),
        html.Div(id='dropdown-container-output', children=[dcc.Textarea(value='',id='current-filters')])
    ])

for dl in dlists:
    filtering_layout.children.append(dl)
