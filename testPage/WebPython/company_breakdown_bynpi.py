import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np

def company_breakdown(df,npi):
    """
    Graphs all payments, over all years, for that specific doctor, seperated by company
    Input
    -----
        npi: string
            NPI number for that doctor
    Output
    -----
        HTML for plotly graph to be inputted into template
    """
    #doc_df = All the payments for that specific NPI
    doc_df = df[df['npi']==str(npi)].groupby(['npi','fn','ln','year','company']).agg({'amount':'sum'}).reset_index()
    #by_company = Payments for that doc (rows = year, cols = companies)
    by_company = pd.pivot_table(doc_df, index=['year'],columns='company',values=['amount']).reset_index()
    #Fixing the index & column names
    by_company.columns = by_company.columns.droplevel()
    by_company.columns = ['year']+list(by_company.columns)[1:]
    #This will be used to store all our data
    data = []
    #Going through each year(x) & getting the values by company(y)
    length = len(by_company.columns)
    #Starting from 1 because we would then do length-0 which would be an index out of bounds (max index = length-1)
    for i in range(1,length):
        #Going by length-i so I can have it in alphabetical order & since we are only going from 1 -> length-1 we will never reach the first column (npi)
        data.append(go.Bar(x=by_company['year'],y=by_company[by_company.columns[length-i]],name=by_company.columns[length-i],hoverinfo="y+name"))
    #Stacked bar graph layout
    layout = go.Layout(
        barmode='stack',
        xaxis={'title':'Year','range':[2012.5,2015.5],'fixedrange':True,'tickmode':'array','tickvals':[2013,2014,2015]},
        yaxis={'title':'Amount Recieved by Company'},
        title='Payments Recieved by Dr. {} {}'.format(doc_df['fn'].iloc[0],doc_df['ln'].iloc[0]),
        hovermode = 'closest',
        hoverlabel={'namelength':-1}
    )
    #Figure
    fig = go.Figure(data=data, layout=layout)
    #Returning HTML to be embeeded
    return(plotly.offline.plot(fig, include_plotlyjs=False, output_type='div'))

if __name__ == '__main__':
    company_breakdown()
