"""
Copyright (C) 2020 David Ollodart
GNU General Public License <https://www.gnu.org/licenses/>.
"""

import pandas as pd
from dash_html_components import Datalist, Option
from datetime import datetime

try:
    with open('last-update.txt', 'r') as _:
        dtime = _.read().strip('\n')
        dtime = datetime.strptime(dtime, '%Y-%m-%d')
        ddays = (datetime.now() - dtime).days # days is the largest unit of time difference
        if ddays > 7:
            1/0
        df = pd.read_csv('data.csv')
except (FileNotFoundError, ZeroDivisionError):
    with open('last-update.txt', 'w') as _:
        _.write(datetime.now().strftime('%Y-%m-%d'))
    df = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')
    with open('data.csv', 'w') as _:
        df.to_csv(_, index=False)


numeric_dtypes = ['int64', 'int32', 'float32', 'float64', 'datetime64[ns]']
x1 = 'dateRep'
gbl = df['geoId'].isin(['US', 'BR', 'IN'])
df = df[gbl] # data subset for testing
df[x1] = pd.to_datetime(df[x1], dayfirst=True)
options = [{'label': x, 'value': x} for x in df.columns]
df['dummy'] = True # dummy column used for some boolean tests

dlists = []
for col in df.columns:
    if df[col].nunique() < 15: 
        # only suggest for those with a small number of options
        uniq = df[col].unique()
        dlists.append(Datalist([Option(x) for x in uniq], id=col))

options = [{'label': i, 'value': i} for i in df.columns]
types = {k:'continuous' if v in numeric_dtypes else 'discrete' for k,v in df.dtypes.items()}
