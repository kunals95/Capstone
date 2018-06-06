import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np

#Breakdown of payments by company
def pay_company_breakdown(df,npi):
    """
    Graphs all payments, over all years, for that specific doctor, seperated by company
    Input
    -----
        df: dataframe
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
        title='Yearly Payments by Company',
        font=dict(family="Roboto Condensed"),
        titlefont=dict(size='28'),
        height=500,
        xaxis={'title':'Year','range':[2012.5,2016.5],'fixedrange':True,'tickmode':'array','tickvals':[2013,2014,2015,2016]},
        yaxis={'title':'Amount Recieved by Company'},
        hovermode = 'closest',
        hoverlabel={'namelength':-1}
    )
    #Figure
    fig = go.Figure(data=data, layout=layout)
    #Returning HTML to be embeeded
    return(plotly.offline.plot(fig, include_plotlyjs=False, output_type='div'))

#Breakdown of scripts by company
def scripts_company_breakdown(df,npi):
    """
    Graphs all PRESCRIPTIONS, over all years, for that specific doctor, seperated by company
    Input
    -----
        df: dataframe
        npi: string
            NPI number for that doctor
    Output
    -----
        HTML for plotly graph to be inputted into template
    """
    #script_doc = All the prescriptions for that specific NPI
    script_doc = df[df['npi']==str(npi)].groupby(['npi','fn','ln','year','drug_company']).agg({'total_claim_count':'sum'}).reset_index()
    #by_company = Payments for that doc (rows = year, cols = companies)
    by_company = pd.pivot_table(script_doc, index=['year'],columns='drug_company',values=['total_claim_count']).reset_index()
    #Fixing the index & column names
    by_company.columns = by_company.columns.droplevel()
    by_company.columns = ['year']+list(by_company.columns)[1:]
    #This will be used to store all our data
    data2 = []
    #Going through each year(x) & getting the values by company(y)
    length = len(by_company.columns)
    #Starting from 1 because we would then do length-0 which would be an index out of bounds (max index = length-1)
    for i in range(1,length):
        #Going by length-i so I can have it in alphabetical order & since we are only going from 1 -> length-1 we will never reach the first column (npi)
        data2.append(go.Bar(x=by_company['year'],y=by_company[by_company.columns[length-i]],name=by_company.columns[length-i],hoverinfo="y+name"))
    #Stacked bar graph layout
    layout2 = go.Layout(
        barmode='stack',
        font=dict(family="Roboto Condensed"),
        titlefont=dict(size='28'),
        title='Yearly Prescriptions by Company',
        height=500,
        xaxis={'title':'Year','range':[2012.5,2016.5],'fixedrange':True,'tickmode':'array','tickvals':[2013,2014,2015,2016]},
        yaxis={'title':'Amount Prescriptions by Company'},
        hovermode = 'closest',
        hoverlabel={'namelength':-1}
    )
    #Figure
    script_fig = go.Figure(data=data2, layout=layout2)
    #Returning HTML to be embeeded
    return(plotly.offline.plot(script_fig, include_plotlyjs=False, output_type='div'))

#Table of payments by year
def pay_table(df,npi):
    """
    Gives you a summary table of the payments, by year
    Input
    -----
        df: dataframe
        npi: string
            NPI number for that doctor
    Output
    -----
        HTML for plotly table to be inputted into template
    """
    #pay_doc = All the payments for that specific NPI
    pay_doc = df[df['npi']==str(npi)].groupby(['npi','fn','ln','year']).agg({'amount':np.sum, 'form':'count'}).reset_index()
    pay_doc['year'] = pay_doc['year'].astype(str)
    pay_doc = pay_doc.append(pay_doc.sum(numeric_only=True), ignore_index=True)
    pay_doc.fillna({'year':'ALL'},inplace=True)
    pay_doc['avg'] = (pay_doc['amount']/pay_doc['form'])
    pay_doc = pay_doc.round(2)

    pay_table = go.Table(
        type = 'table',
        columnwidth = [75, 150, 200, 200],
        header= dict(
            values = ['Year','Amount Paid','Number Payments','Average Amount'],
            line = dict(color='rgb(255,153,0,.8)'),
            fill = dict(color='rgb(255,153,0,.8)'),
            align = ['center'],
            font=dict(color='black',size=16)
        ),
        cells = dict(
            values= [pay_doc.year,pay_doc.amount,pay_doc.form,pay_doc.avg],
            line = dict(color='white'),
            fill = dict(color='white'),
            height=25,
            align = ['left','right','center','right'],
            font = dict(color='black',size=15.5)
        ))

    data3 = [pay_table]

    layout3 = dict(font=dict(family="Roboto Condensed"),title='Summary of Payments',titlefont=dict(size='28'), height=400)
    fig3 = dict(data=data3,layout=layout3)
    #Returning HTML to be embeeded
    return(plotly.offline.plot(fig3, include_plotlyjs=False, output_type='div'))

def pie_type(df,npi):
    """
    Gives you a summary pie chart of the payments broken up by nature, selectable by year,
    Input
    -----
        df: dataframe
        npi: string
            NPI number for that doctor
    Output
    -----
        HTML for plotly pie chart to be inputted into template
    """
    nature_yr = df[df['npi']==str(npi)].groupby(['year','nature']).agg({'amount':np.sum}).reset_index()
    n13 = nature_yr[nature_yr['year']==2013]
    n14 = nature_yr[nature_yr['year']==2014]
    n15 = nature_yr[nature_yr['year']==2015]
    n16 = nature_yr[nature_yr['year']==2016]
    nall = df[df['npi']==str(npi)].groupby(['nature']).agg({'amount':np.sum}).reset_index()
    pie_13 = go.Pie(
        labels= n13.nature.unique(),
        values= n13.amount,
        textinfo="none",
        hoverinfo='label+percent',
        hoverlabel=dict(namelength='0-20')
    )
    pie_14 = go.Pie(
        labels= n14.nature.unique(),
        values= n14.amount,
        textinfo="none",
        hoverinfo='label+percent',
        hoverlabel=dict(namelength='10')
    )
    pie_15 = go.Pie(
        labels= n15.nature.unique(),
        values= n15.amount,
        textinfo="none",
        hoverinfo='label+percent',
        hoverlabel=dict(namelength='10')
    )
    pie_16 = go.Pie(
        labels= n16.nature.unique(),
        values= n16.amount,
        textinfo="none",
        hoverinfo='label+percent',
        hoverlabel=dict(namelength='10')
    )
    pie_all = go.Pie(
        labels= nall.nature.unique(),
        values= nall.amount,
        textinfo="none",
        hoverinfo='label+percent',
        hoverlabel=dict(namelength='10')
    )

    data4 = [pie_13, pie_14, pie_15, pie_16, pie_all]

    updatemenus = list([
        dict(active=4,
             buttons=list([
                dict(label = '2013',
                     method = 'update',
                     args = [{'visible': [True, False, False, False, False]}]),
                dict(label = '2014',
                     method = 'update',
                     args = [{'visible': [False, True, False, False, False]}]),
                dict(label = '2015',
                     method = 'update',
                     args = [{'visible': [False, False, True, False, False]}]),
                dict(label = '2016',
                     method = 'update',
                     args = [{'visible': [False, False, False, True, False]}]),
                dict(label = 'All Years',
                     method = 'update',
                     args = [{'visible': [False, False, False, False, True]}])
                             ])
                )
            ])

    layout4 = dict(font=dict(family="Roboto Condensed"),titlefont=dict(size='28'),title='Payments by Type', showlegend=False, updatemenus=updatemenus, height=400)
    fig4 = dict(data=data4,layout=layout4)

    #Returning HTML to be embeeded
    return(plotly.offline.plot(fig4, include_plotlyjs=False, output_type='div'))
