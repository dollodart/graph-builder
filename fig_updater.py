"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from smooth import whittaker_smooth
from data import df, gbl, numeric_dtypes
from dash.dependencies import Input, Output

#from scipy.interpolate import UnivariateSpline
# for spline interpolation
#from numpy import ones, convolve
# for moving average (series method used instead)
color_cycle = px.colors.qualitative.Plotly
ncolors = len(color_cycle)

def cartesian_product(xs, ys):
    """
    Cartesian product in which xs "run fastest".
    """

    xys = []
    for cy, y in enumerate(ys):
        for cx, x in enumerate(xs):
            xys.append( ((cx, cy), (x, y)) )
    return xys

def fig_updater(df, xs, ys, size=None, color=None, symbol=None, 
        hover_data = None, smoother = None, smoother_parameter=None, 
        max_size=35, cartesian_prod = False):
    """Evaluate inputs and updates the figure correctly based on inputs 

    x:
      sequence of labels (column names)
    y: 
      sequence of labels (column names)
    size:
      string, label (column name)
    color:
      string, label (column name)
    symbol:
      string, label (column name)

    cartesian_prod:
      bool, whether the list should be expanded

    Relevant variables:
        Number of x variables
        Number of y variables
        Data type(s) of x variable(s)
        Data type(s) of y variable(s)
        Data types of size (must be numeric or will be "factorized"), color, symbol (must be categorical or will be histogramed)
    """

    dtypes = df.dtypes.to_dict()

    shared_xaxes = shared_yaxes = False 

    if cartesian_prod:
        shared_xaxes = shared_yaxes = True
        xys = cartesian_product(xs, ys)
        rows = len(ys)
        cols = len(xs)
    elif len(xs) > 1 and len(ys) == 1:
        xys = tuple( ((i, 0),(xs[i], ys[0])) for i in range(len(xs)) )
        shared_yaxes = True
        rows = 1
        cols = len(xs)
    elif len(xs) == 1 and len(ys) > 1:
        xys = tuple( ((0, i),(xs[0], ys[i])) for i in range(len(ys)) )
        shared_xaxes = True
        rows = len(ys)
        cols = 1
    elif len(xs) == 1 and len(ys) == 1:
        rows = cols = 1
        xys = ((0, 0),(xs[0], ys[0])), 
    else:
        n = max(len(xs), len(ys))
        m = min(len(xs), len(ys))
        cols = 2
        rows = 1 + (n - 1) // 2

        if len(xs) < len(ys):
            xys = tuple( ((i % 2, i // 2), (xs[i % m], ys[i])) for i in range(n))
        else:
            xys = tuple( ((i % 2, i // 2), (xs[i], ys[i % m])) for i in range(n))

    fig = make_subplots(rows=rows,
            cols=cols, 
            shared_yaxes=shared_yaxes,
            shared_xaxes=shared_xaxes)

    if size is not None:
        if not dtypes[size] in numeric_dtypes:
            dfsize = disc2cont(df[size]) * max_size
        else:
            dfsize = df[size] * max_size / df[size].max()

    if color is not None: # color is used for legending, not quantitative heat maps
        if dtypes[color] in numeric_dtypes:
            dfcolor = cont2disc(df[color])
        else:
            dfcolor = df[color]
        coloriter = dfcolor.unique()
    else:
        dfcolor = df['dummy']
        coloriter = [True]

    if symbol is not None: 
        if dtypes[symbol] in numeric_dtypes:
            dfsymbol = cont2disc(df[symbol]) # interval type
        else:
            dfsymbol = df[symbol]
        symboliter = dfsymbol.unique()
    else:
        dfsymbol = df['dummy']
        symboliter = [True]

    for ccounter, c in enumerate(coloriter):
        for scounter, s in enumerate(symboliter):
            bl = (dfcolor == c) & (dfsymbol == s)
            if bl.sum() < 2:
                continue

            gr = df[bl]
            name = (str(c) if c is not None and c is not True else '') +\
                   ('-' + str(s) if s is not None and s is not True else '')

            if size is not None:
                size_array = dfsize[bl]
            else:
                size_array = None

            marker_array = dict(color=color_cycle[ccounter % ncolors],
            symbol=scounter,
            size=size_array)

            # hovertext must be sequence
            if hover_data is not None:
                hovertext_array = []
                for hii, hi in gr[list(hover_data)].iterrows(): # allow passing tuples
                    hr = []
                    for hvt in hover_data:
                        hr.append(f'{hvt}: {hi[hvt]}')
                    hovertext_array.append('\n\n'.join(hr))
            else:
                hovertext_array = None

            for (xcounter, ycounter), (xinst, yinst) in xys:
                fig.update_yaxes(title_text=yinst,
                        row=1+ycounter,
                        col=1+xcounter)
                fig.update_xaxes(title_text=xinst,
                        row=1+ycounter,
                        col=1+xcounter)
                trace = go.Scattergl(x=gr[xinst],
                        y=gr[yinst],
                        mode='markers',
                        name=name + '-' + xinst + '-' + yinst,
                        hovertext=hovertext_array,
                        marker=marker_array)
                fig.add_trace(trace, row=ycounter+1, col=xcounter+1)

                gr = gr.sort_values(by=xinst)
                if smoother == 'whittaker':
                    y2 = whittaker_smooth(gr[yinst].values, 10**smoother_parameter) # input is a linear range of 0 to 5
                elif smoother == 'moving-average':
                    y2 = gr[yinst].rolling(window=smoother_parameter, center=False).mean()
                else:
                    continue

                trace = go.Scattergl(x=gr[xinst],
                        y=y2,
                        mode='lines',
                        name=name + '-' + xinst + '-' + yinst + '-smooth',
                        hovertext=None,
                        marker=dict(color=color_cycle[ccounter % ncolors]))
                fig.add_trace(trace, row=ycounter+1, col=xcounter+1)

    return fig



def cont2disc(series, ncategories=5):
    """
    Converts continuous into intervals to be treated as discrete (intervals represented as strings).
    """
    q = series.quantile(np.linspace(0, 1, ncategories))
    return pd.cut(series, pd.unique(q)).astype(str)


def disc2cont(series):
    """
    Converts discrete (str or other) to continuous numeric in interval [0, 1].
    """
    return series.map(dict(zip(series.unique(), np.linspace(0, 1, series.nunique()))))

if __name__ == '__main__':
    x1 = 'dateRep'
    df = pd.read_csv('data.csv')
    df = df[df['geoId'].isin(['US', 'BR', 'IN'])]
    df[x1] = pd.to_datetime(df[x1], dayfirst=True)

    x2 = 'cases'

    y1 = 'cases'
    y2 = 'deaths'
    shape = 'continentExp'
    color = 'geoId'
    size = 'popData2019'
    hover_data = ('countriesAndTerritories',
        'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000')

    # don't throw errors, but may not be correct
    #color, size = size, color
    #shape, size = size, shape

    color = shape = None

    xs = (x1, x2)
    ys = (y1, y2)

    fig = fig_updater(df, xs, ys, size=size, color=color, symbol=shape,hover_data=hover_data,smoother='whittaker',cartesian_prod=False)
    fig.show()
