"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

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
