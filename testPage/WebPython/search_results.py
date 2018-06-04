import pandas as pd
import numpy as np
import plotly
import plotly.plotly as py
import plotly.figure_factory as ff

def make_link(x):
    for ind in x.index:
        doc_npi = ''
        for col in x.columns:
            if col == 'NPI':
                doc_npi = x.at[ind,col]
                x.at[ind,col] = ('<a href="../../graph/npi/{}">{}</a>'.format(x.at[ind,col],x.at[ind,col]))
            else:
                x.at[ind,col] = ('<a href="../../graph/npi/{}">{}</a>'.format(doc_npi,x.at[ind,col]))

def results_py(df,dict):
    """
    inputs:
        df = Dataframe of doc_info
        dict = Dictionary of user input of values
    """
    orig_df_len = len(df)
    d_true_values = {}
    for key, value in dict.items():
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
        table = ff.create_table(df)
        return(plotly.offline.plot(table, include_plotlyjs=False, output_type='div'))

if __name__ == '__main__':
    results_py()
