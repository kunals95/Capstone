import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np

paid = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_all_years_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':object,'company_id':object, \
                                  'payment_id':object,'record_id':object})
#Just replace the npi here for the doctor you're searching for
x = paid[paid['npi']=='1922188184'].groupby(['npi','fn','ln','year','company']).agg({'amount':'sum'}).reset_index()
tb = pd.pivot_table(x, index=['year'],columns='company',values=['amount']).reset_index()
tb.columns = tb.columns.droplevel()
tb.columns = ['year']+list(tb.columns)[1:]

data = []

for i in range(len(tb.columns)):
    data.append(go.Bar(x=tb['year'],y=tb[tb.columns[i]],name=tb.columns[i]))

layout = go.Layout(
    barmode='stack',
    xaxis={'title':'Year'},
    yaxis={'title':'Amount Recieved by Company'},
    title='Payments Recieved by Dr. {} {}'.format(x['fn'].iloc[0],x['ln'].iloc[0])
)

fig = go.Figure(data=data, layout=layout)

plotly.offline.plot(fig, output_type='div',show_link=False)

#filename='doc_pay.html'
