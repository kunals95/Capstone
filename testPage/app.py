import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from pythonfiles.company_breakdown_bynpi import *
from pythonfiles.search_result_alt import *
#Importing my variables

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
    output2 = results_py(doc_info,{'First Name':input_fn,'Last Name':input_ln,'City':input_city,'Zip Code':input_zip,'State':input_state})
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
        pay_by_comp = pay_company_breakdown(paid,NPI)
        scripts_by_comp = scripts_company_breakdown(scripts,NPI)
        paid_table = pay_table(paid,NPI)
        pie_type1 = pie_type(paid,NPI)
        return render_template('graph_npi.html', pay_by_comp=pay_by_comp, paid_table=paid_table, pie_chart=pie_type1, scripts_by_comp=scripts_by_comp, fn=fn_df, ln=ln_df, address=address_df, city=city_df, zip=zip_df, state=state_df, type=type_df, spec=spec_df)
    except IndexError:
        return render_template('404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
