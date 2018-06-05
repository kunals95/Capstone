import pandas as pd
import numpy as np
import re
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pickle

pays = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_all_years_consl.csv', \
                   usecols=['company','amount','npi','year','payment_id'])
def top10_comp(df):
    pay_by_comp = df.groupby(['company']).agg({"amount": np.sum, "npi": pd.Series.nunique,'payment_id':'count'}).reset_index()
    top10 = pay_by_comp.sort_values(['amount','npi','payment_id'],ascending=False).round(decimals=2)
    top10['amount'] = top10.apply(lambda x: "{:,}".format(x['amount']), axis=1)
    top10['amount'] = '$'+top10['amount']
    top10 = top10.iloc[:10]
    data = [go.Bar(
            x=top10['company'],
            y=top10['amount'],
            text=top10['amount'],
            textposition='outside',
            textfont={'size':14,'color':'black'},
            name='Total Amount Paid',
            marker=dict(color=['FireBrick','Navy','Green','DarkMagenta',
                               'DarkOrange','Indigo','LightSkyBlue','DarkSlateGrey',
                               'MediumVioletRed','Peru']),)]
    layout = go.Layout(
        title='Companies paying the most to Doctors - NJ',xaxis={'tickfont':{'size':8}},yaxis={'tickfont':{'size':14}})
    fig = go.Figure(data=data, layout=layout)
    return(plotly.offline.plot(fig,filename='top10companies.html'))

top10_comp(pays)

def yearly_amount(df):
    pay_by_year = df.groupby(['year']).agg({"amount": np.sum, "npi": pd.Series.nunique,'payment_id':'count'}).reset_index()
    pay_by_year = pay_by_year.sort_values(['amount','npi','payment_id'],ascending=False).round(decimals=2)
    pay_by_year['amount'] = pay_by_year.apply(lambda x: "{:,}".format(x['amount']), axis=1)
    pay_by_year['amount'] = '$'+pay_by_year['amount']
    data = [go.Bar(
            x=pay_by_year['year'],
            y=pay_by_year['amount'],
            text=pay_by_year['amount'],
            textposition='outside',
            textfont={'size':16,'color':'black'},
            marker=dict(color=['FireBrick','Navy','Green']),)]
    layout = go.Layout(
        title='Yearly Amounts Paid to NJ Doctors', xaxis={'title':'Year','range':[2012.5,2015.5],'fixedrange':True,'tickmode':'array','tickvals':[2013,2014,2015],'tickfont':{'size':16}},
        yaxis={'tickfont':{'size':16}})
    fig = go.Figure(data=data, layout=layout)
    return(plotly.offline.plot(fig,filename='yearly_amount.html'))

yearly_amount(pays)


scripts = pd.read_csv('/volumes/Seagate/Galvanize/nj_scripts_all_years.csv', \
    usecols=['drug_name','generic_name','amount_brand','total_drug_cost','drug_company')


def top10_comp_scripts(df):
    comp_scripts = df[df['amount_brand']!=0]
    scripts_by_comp = comp_scripts.groupby('company').agg({"total_drug_cost": np.sum})
    top10 = scripts_by_comp.sort_values(['total_drug_cost'],ascending=False).round(decimals=2)
    top10['total_drug_cost'] = top10.apply(lambda x: "{:,}".format(x['total_drug_cost']), axis=1)
    top10['total_drug_cost'] = '$'+top10['total_drug_cost']
    top10 = top10.reset_index().iloc[:10]
    data = [go.Bar(
            x=top10['company'],
            y=top10['total_drug_cost'],
            text=top10['total_drug_cost'],
            textposition='outside',
            textfont={'size':14,'color':'black'},
            marker=dict(color=['FireBrick','Navy','Green','DarkMagenta',
                               'DarkOrange','Indigo','LightSkyBlue','DarkSlateGrey',
                               'MediumVioletRed','Peru']),)]
    layout = go.Layout(
        title='Companies Recieving Highest Medicare Part D Payments', xaxis={'tickfont':{'size':8}},yaxis={'tickfont':{'size':14}})
    fig = go.Figure(data=data, layout=layout)
    return(plotly.offline.plot(fig,filename='top10_comp_scripts.html'))

top10_comp_scripts(scripts)
