import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np

def some_func():
    paid = pd.read_csv('/Users/kunal/Downloads/pay_script_full_onlypaid.csv',dtype={'npi':object})
    x = paid.groupby('npi')['year'].nunique().to_frame().reset_index()
    x3 = paid[paid['npi'].isin(list(x['npi'][:20]))]
    table = pd.pivot_table(x3, index=['fn','ln'],columns='year',values=['amount']).reset_index()
    table.fillna(value=0,inplace=True)
    table.columns = table.columns.droplevel()
    table.columns = ['fn','ln','2013','2014','2015']

    data = [
        go.Bar(
            x=table['fn']+' '+table['ln'],
            y=table['2013'],
            name='2013'
        ),
        go.Bar(
            x=table['fn']+' '+table['ln'],
            y=table['2014'],
            name='2014'
        ),
        go.Bar(
            x=table['fn']+' '+table['ln'],
            y=table['2015'],
            name='2015'
        ),
    ]

    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)

    return(plotly.offline.plot(fig, include_plotlyjs=False, output_type='div'))

if __name__ == '__main__':
    some_func()
