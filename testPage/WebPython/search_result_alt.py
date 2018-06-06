import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

def make_link(x):
    for ind in x.index:
        doc_npi = ''
        for col in x.columns:
            if col == 'NPI':
                doc_npi = x.at[ind,col]
                x.at[ind,col] = ('<a href=\"../../graph/npi/{}\">{}</a>'.format(doc_npi,doc_npi))
            else:
                x.at[ind,col] = ('<a href=\"../../graph/npi/{}\">{}</a>'.format(doc_npi,x.at[ind,col]))

def makelist(df):
    l =[]
    for i in range(len(df.columns)):
        l.append(df.iloc[:,i])
    return l
#If you change the name of the inputted df, this wont work

#More customizable way
def results_py(df,dic):
    """
    inputs:
        df = Dataframe of doc_info
        dict = Dictionary of user input of values
    """
    orig_df_len = len(df)
    d_true_values = {}
    for key, value in dic.items():
        #Basically making a new dict with only values where a user inputted
        if value:
            d_true_values[key] = value
    for k in d_true_values:
        #Go through all the values that were inputted
        #If we're not going to get no results back:
        if len(df[df[k]==str(d_true_values[k]).upper()]) != 0:
            df = df[df[k]==str(d_true_values[k]).upper()]
        else:
            #If our query makes it so we get no results, break & don't change the df
            break
    if len(df) == 0 or len(df) == orig_df_len:
        return('<p><u><h4><b>Your search returned no results, <a href="../" target="">would you like to search again?</a></b></h4></u></p>')
    else:
        make_link(df)
        bold = lambda x: '<b>'+x+'</b>'
        def colors(df):
            if len(df) == 1:
                return([['white']])
            elif len(df)!=1 & len(df) %2 !=0:
                return([int((len(df)/2))*['white','rgb(240, 240, 240)']+['white']])
            else:
                return([['white','rgb(240, 240, 240)'] * int((len(df)/2))])
        table = go.Table(
            type='table',
            columnwidth=[65,55,55,40,35,80,70,40],
            header = dict(
                values=bold(df.columns),
                fill=dict(color='rgb(240, 240, 240)'),
                align=['center'],
                font=dict(color='black',size=16, family="Roboto Condensed"),
                line=dict(width=0,color='black')
                ),
            cells = dict(
                values=makelist(df),
                fill=dict(color=colors(df)),
                font=dict(color='black',size=13, family="Roboto Condensed"),
                height=15,
                line=dict(width=0),
                ))
        data = [table]
        return(plotly.offline.plot(data, include_plotlyjs=False, output_type='div'))
        #You'll get an error if you switch the df name
