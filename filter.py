"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State, MATCH, ALL
from data import df, options, types

def assign_filter(app):

    @app.callback(
        Output('dropdown-container', 'children'),
        [Input('add-filter', 'n_clicks')],
        [State('dropdown-container', 'children')])
    def add_filter(n_clicks, children):
        new_dropdown = html.Div(children=[dcc.Dropdown(
            id={'type': 'filter-dropdown', 'index': n_clicks},
            options=options), 
            dcc.Input(id={'type': 'filter-lb', 'index': n_clicks}), 
            dcc.Input(id={'type': 'filter-ub', 'index': n_clicks}), 
            html.Datalist(id={'type': 'filter-discrete-list', 'index': n_clicks}), 
            html.Button('Update', id={'type': 'filter-update', 'index': n_clicks}), 
            html.Button('Delete', id={'type': 'filter-delete', 'index': n_clicks}),
            html.P('', id={'type': 'filter-description', 'index': n_clicks})
        ], id={'type': 'filter-container', 'index': n_clicks})
        children.append(new_dropdown)
        return children


    @app.callback(
        [Output({'type': 'filter-lb', 'index': MATCH}, 'list'),
         Output({'type': 'filter-ub', 'index': MATCH}, 'disabled'),
         Output({'type': 'filter-description', 'index':MATCH}, 'children')],
        [Input({'type': 'filter-dropdown', 'index': MATCH}, 'value')]
    )
    def change_type(dropdown):
        if dropdown is None:
            return dash.no_update
        elif types[dropdown] == 'continuous':
            return dropdown, False, 'quantiles: ' + str(df[dropdown].quantile(np.linspace(0, 1, 6))).replace('    ',':').replace('\n', ',')
        else:  # change to discrete
            return dropdown, True, 'unique values: ' + str(df[dropdown].unique())[:50] 


    @app.callback(
        Output({'type': 'filter-container', 'index': MATCH}, 'children'),
        [Input({'type': 'filter-delete', 'index': MATCH}, 'n_clicks')]
    )
    def delete_filter(n_clicks):
        return dash.no_update if n_clicks is None else []

    return app

import numpy as np

def apply_filter(fields, lbs, ubs):
    st = ''
    bls = []
    for i in range(len(fields)):
        st += f'{i} {fields[i]} {lbs[i]} {ubs[i]}\n'
        if types[fields[i]] == 'continuous':
            bls.append((df[fields[i]] > float(lbs[i])) & (df[fields[i]] < float(ubs[i])))
        else:
            eqs = tuple(i.strip() for i in lbs[i].split(','))
            bls.append(df[fields[i]].isin(eqs))

    gbl = np.all(bls, axis=0)

    return gbl, st


if __name__ == '__main__':
    app = dash.Dash(__name__)
    @app.callback(
        [Output('current-filters', 'value')],
        [Input({'type': 'filter-update', 'index': ALL}, 'n_clicks')],
        [State({'type': 'filter-dropdown', 'index': ALL}, 'value'),
         State({'type': 'filter-lb', 'index': ALL}, 'value'),
         State({'type': 'filter-ub', 'index': ALL}, 'value')]
    )
    def update_graph(n_clicks, fields, lbs, ubs):
        st = ''
        bls = []
        for i in range(len(fields)):
            if n_clicks[i] is not None:
                st += f'{i} {fields[i]} {lbs[i]} {ubs[i]}\n'
        return st
    from layouts import filtering_layout
    app.layout = filtering_layout
    app = assign_filter(app)
    app.run_server(debug=True)
