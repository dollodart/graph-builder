import dash
from dash.dependencies import Input, Output, State

def assign_alias(app):
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
            current_options.append({'label': alias, 'value': name})
            return (alias_history + '\n' +
                    f'{name}\t{alias}\t{submit_alias}',) + (current_options,) * 6
        return dash.no_update

    return app
