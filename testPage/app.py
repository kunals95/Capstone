import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import sys
sys.path.append('/Users/kunal/Galvanize/Capstone/testPage/WebPython')
#Name of folder containing file
import company_breakdown_bynpi
import search_result_alt, search_results
#Name of file

from flask import Flask, request, render_template
app = Flask(__name__)

doc_info = pd.read_csv('/Volumes/Seagate/Galvanize/nj_doc_info_paid.csv',dtype={'Zip Code':object,'NPI':object})
doc_info.fillna(value='-',inplace=True)
paid = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_all_years_consl.csv',
                            dtype={'zip':object,'npi':object,'company_id':object}, \
                  usecols=[1,2,3,10,11,12,13,26])
scripts = pd.read_csv('/Volumes/Seagate/Galvanize/nj_scripts_all_years.csv',dtype={'zip':object,'npi':object})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/findings/')
def testing():
    return render_template('findings.html')

@app.route('/methods/')
def method():
    return render_template('methods.html')

@app.route('/raw-data/')
def raw_data():
    return render_template('raw_data.html')

@app.route('/search/', methods=["POST","GET"])
def search():
    #In this HTML file you must include action="{{ url_for('results')}}"method="POST" in the form
    if request.method == "POST":
        input_fn = request.form['fn']
        input_ln = request.form['ln']
        input_city = request.form['city']
        input_zip = request.form['zip']
        input_state = str(request.form['state'])
        return redirect(url_for("/search/results", fn=input_fn,ln=input_ln,city=input_city,zip=input_zip,state=input_state))
        #URL for html file name
    else:
        return render_template('search.html')

@app.route('/search/results/', methods=["POST","GET"])
def results():
    input_fn = request.form.get('fn')
    input_ln = request.form.get('ln')
    input_city = request.form.get('city')
    input_zip = request.form.get('zip')
    input_state = request.form.get('state')
    output2 = search_result_alt.results_py(doc_info,{'First Name':input_fn,'Last Name':input_ln,'City':input_city,'Zip Code':input_zip,'State':input_state})
    return render_template('search_results.html',output2=output2,fn=input_fn,ln=input_ln,city=input_city,zip=input_zip,state=input_state)

@app.route('/graph/npi/<int:NPI>')
def graph_npi(NPI):
    try:
        info_df = doc_info[doc_info['NPI']==str(NPI)]
        fn_df = list(info_df['First Name'].values)[0]
        ln_df = list(info_df['Last Name'].values)[0]
        city_df = list(info_df['City'].values)[0]
        address_df = list(info_df['Address'].values)[0]
        zip_df = list(info_df['Zip Code'].values)[0]
        state_df = list(info_df['State'].values)[0]
        type_df = list(info_df['Type'].values)[0]
        spec_df = list(scripts[scripts['npi']==str(NPI)]['specialty_description'].values)[0]
        pay_by_comp = company_breakdown_bynpi.pay_company_breakdown(paid,NPI)
        scripts_by_comp = company_breakdown_bynpi.scripts_company_breakdown(scripts,NPI)
        paid_table = company_breakdown_bynpi.pay_table(paid,NPI)
        pie_type = company_breakdown_bynpi.pie_type(paid,NPI)
        return render_template('graph_npi.html', pay_by_comp=pay_by_comp, paid_table=paid_table, pie_type=pie_type, scripts_by_comp=scripts_by_comp, fn=fn_df, ln=ln_df, address=address_df, city=city_df, zip=zip_df, state=state_df, type=type_df, spec=spec_df)
    except IndexError:
        return render_template('404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#DON'T USE THIS
"""
@app.route('/test_graph/', methods=["POST","GET"])
def doc_graph():
    input_ln = request.form.get('ln')
    output = company_breakdown_bynpi.company_breakdown(input_ln)
    return render_template('test_graph.html',output=output, ln=input_ln)
    #I have the HTML file askign for the input of ln to print on the webpage that's why it's included here.
"""
#Also see line 8, include at end of your py file:
"""
if __name__ == '__main__':
    NAME OF FUNCTION()
"""
#Have to include this in your HTML:
"""
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
{{ output|safe }}
"""
"""
@app.route('/search/npi/1922188184')
def graph_pay():
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

    for i in range(1,len(tb.columns)):
        data.append(
            go.Bar(
                x=tb['year'],
                y=tb[tb.columns[len(tb.columns)-i]],
                name=tb.columns[len(tb.columns)-i],
                hoverinfo='y+name',
                hoverlabel={
                    'font':{'size':11},
                    'namelength':-1
                    }
                )
            )

    layout = go.Layout(
        barmode='stack',
        xaxis={'title':'Year','fixedrange':True,'dtick':1},
        yaxis={'title':'Amount Recieved by Company','fixedrange':True},
        title='Payments Recieved by Dr. {} {}'.format(x['fn'].iloc[0],x['ln'].iloc[0]),
        hovermode='closest'
    )

    fig = go.Figure(data=data, layout=layout)

    return plotly.offline.plot(fig, output_type='div',show_link=False)
"""
