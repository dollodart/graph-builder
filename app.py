# -*- coding: utf-8 -*-
"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL, MATCH
import pandas as pd
from data import df, options
from layouts import *
from fig_updater import fig_updater
from filter import assign_filter

def create_dash_app():
    fig = fig_updater(df, xs=['dateRep'], ys=['cases_weekly']) 
    graph_layout = dcc.Graph(figure=fig, id='plot')
    app = dash.Dash(suppress_callback_exceptions=True)
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
    return app

app = create_dash_app()
app = assign_filter(app)

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

from filter import apply_filter
@app.callback(
    [Output('plot', 'figure'),
     Output('current-filters', 'value')],
    [Input('x-axis', 'value'),
     Input('y-axis', 'value'),
     Input('symbol', 'value'),
     Input('size', 'value'),
     Input('color', 'value'),
     Input('hover-data', 'value'),
     Input('cartesian-prod','value'),
     Input('smoother', 'value'),
     Input('smoother-slider', 'value'),
     Input({'type': 'filter-update', 'index': ALL}, 'n_clicks')
     ],
    [State({'type': 'filter-dropdown', 'index': ALL}, 'value'),
         State({'type': 'filter-lb', 'index': ALL}, 'value'),
         State({'type': 'filter-ub', 'index': ALL}, 'value'),
         State('current-filters', 'value')])
def all_figure_callbacks(x, y, 
        symbol, size, color, hover_data, 
        cartesian_prod, 
        smoother, smoother_slider,
        filter_nclicks, filter_fields, filter_lbs, filter_ubs, filter_history):

    # if using dash callback context to selectively update boolean, need to cache the data
    # just recompute the filter for every adjust, since it isn't expensive
    #    ctx = dash.callback_context
    #    print(ctx.triggered)
    #    if 'filter-update' in ctx.triggered[0]['prop_id']: # they stringify the ID

    has_filter = False
    nnone = []
    for i in range(len(filter_fields)):
        if filter_fields[i] is not None:
            has_filter = True
            nnone.append((filter_fields[i], filter_lbs[i], filter_ubs[i]))

    if has_filter:
        f, l, u = zip(*nnone)
        gbl, filter_history_update = apply_filter(f, l, u)
        filter_history += filter_history_update
    else:
        gbl = [True]*len(df)

    fig = fig_updater(df[gbl], x, y,
            symbol=symbol,
            size=size,
            color=color,
            hover_data=hover_data,
            cartesian_prod=cartesian_prod,
            smoother=smoother,
            smoother_parameter=smoother_slider)
    fig.update_layout(transition_duration=500)
    return fig, filter_history

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
     State('alias-history','value'),
     State('x-axis', 'options')]
)
def update_aliases(submit_alias, name, alias, alias_history, current_options):
    if alias is not None and name is not None:
        options.append({'label': alias, 'value': name})
        return (alias_history + '\n' +
                f'{name}\t{alias}\t{submit_alias}',) + (options,) * 6
    return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)
