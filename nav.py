from layouts import show, hide
from dash.dependencies import Input, Output

def assign_nav(app):
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

    return app
