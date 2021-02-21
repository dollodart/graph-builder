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
            html.Button('Delete', id={'type': 'filter-delete', 'index': n_clicks})
        ], id={'type': 'filter-container', 'index': n_clicks})
        children.append(new_dropdown)
        return children


    # throws object collision error since the same index is used
    #@app.callback(
    #        [Output({'type':'filter-container', 'index': MATCH}, 'children')],
    #        [Input({'type':'filter-dropdown', 'index':MATCH}, 'value'),
    #         Input({'type':'filter-delete', 'index':MATCH}, 'n_clicks')],
    #        [State({'type':'filter-dropdown', 'index':MATCH}, 'id')]) # index attribute is always None?
    #def alternate_abc(dropdown, delete_n_clicks, index):
    #    index = index['index']
    #    print(dropdown, index)
    #    if delete_n_clicks is not None:
    #        return html.Div()
    #    if dropdown is None:
    #        return dash.no_update
    #    if types[dropdown] == 'continuous':
    #        return html.Div(children=[dcc.Dropdown(
    #        id={'type': 'filter-dropdown', 'index': index},
    #        options=options),
    #        dcc.Input(id={'type': 'filter-lb', 'index': index}),
    #        dcc.Input(id={'type': 'filter-ub', 'index': index}),
    #        html.Datalist(id={'type': 'filter-discrete-list', 'index': index}),
    #        html.Button('Update', id={'type': 'filter-update', 'index': index}),
    #        html.Button('Delete', id={'type': 'filter-delete', 'index': index})
    #    ], id={'type': 'filter-container', 'index': index}),
    #    elif types[dropdown] == 'discrete':
    #        return html.Div(children=[dcc.Dropdown(
    #        id={'type': 'filter-dropdown', 'index': index},
    #        options=options),
    #        dcc.Input(id={'type': 'filter-lb', 'index': index}),
    ##        dcc.Input(id={'type': 'filter-ub', 'index': index}),
    #        html.Datalist(id={'type': 'filter-discrete-list', 'index': index}),
    #        html.Button('Update', id={'type': 'filter-update', 'index': index}),
    #        html.Button('Delete', id={'type': 'filter-delete', 'index': index})
    #    ], id={'type': 'filter-container', 'index': index}),



    @app.callback(
        [Output({'type': 'filter-lb', 'index': MATCH}, 'list'),
         Output({'type': 'filter-ub', 'index': MATCH}, 'disabled')],
        [Input({'type': 'filter-dropdown', 'index': MATCH}, 'value')],
        [State({'type': 'filter-ub', 'index': MATCH}, 'disabled')]
    )
    def change_type(dropdown, ub_disabled):
        if dropdown is None:
            return dash.no_update
        if not ub_disabled:  # currently continuous
            if types[dropdown] == 'continuous':
                return dash.no_update
            else:  # change to discrete
                return dropdown, True
        elif ub_disabled:  # currently discrete
            if types[dropdown] == 'discrete':
                return dash.no_update
            else:  # change to continuous
                return None, False


    @app.callback(
        Output({'type': 'filter-container', 'index': MATCH}, 'children'),
        [Input({'type': 'filter-delete', 'index': MATCH}, 'n_clicks')]
    )
    def delete_filter(n_clicks):
        return dash.no_update if n_clicks is None else []

    return app

# is used by
import numpy as np

def apply_filter(fields, lbs, ubs):
    st = ''
    bls = []
    for i in range(len(fields)):
        st += f'{i} {fields[i]} {lbs[i]} {ubs[i]}\n'
        if types[fields[i]] == 'continuous':
            bls.append((df[fields[i]] > lbs[i]) & (df[fields[i]] < ubs[i]))
        else:
            bls.append(df[fields[i]] == lbs[i])

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
