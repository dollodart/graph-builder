"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from dash.dependencies import Input, Output
from layouts import show, hide

def whittaker_smooth(y, lmbd):

    """
    Whittaker smoothing algorithm.
    Second order differences used.

    Reference:
    Paul H. C. Eilers, "A perfect smoother",
    Anal. Chem. 2003, (75), 3631-3636


    Inputs:
      y: data vector
      lmbd: smoothing parameter 
    Outputs:
      z: smoothed data
    """

    L = len(y)
    E = sparse.eye(L, format='csc')
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L))
    Z = E + lmbd * D.transpose() @ D
    z = sparse.linalg.spsolve(Z, y)
    return z

def assign_smooth(app):

    @app.callback([Output('smoother-slider', 'min'),
        Output('smoother-slider', 'max'),
        Output('smoother-slider', 'value'),
        Output('smoother-slider', 'step'),
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

    return app
