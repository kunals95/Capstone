import pandas as pd
import numpy as np
import re
import pickle

#Linking specific companies to the drugs they make
meds = pd.read_csv('/Volumes/Seagate/Galvanize/Drug_Products_in_the_Medicaid_Drug_Rebate_Program.csv',
                  usecols=['NDC','Labeler Name','FDA Product Name','Year'])
#Removing excess spacing & any symbols
meds['FDA Product Name'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in meds['FDA Product Name']]
meds['FDA Product Name'] = meds['FDA Product Name'].str.strip()
meds['Labeler Name'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in meds['Labeler Name']]
meds['Labeler Name'] = meds['Labeler Name'].str.strip()
#Basically only getting the unique medicine names
medsgrp = meds.groupby(['FDA Product Name','Labeler Name'])['NDC'].nunique().to_frame().reset_index()
#Saving for future use
medsgrp.to_csv('/Volumes/Seagate/Galvanize/medicare_drugs.csv',index=False)

scripts = pd.read_csv('/volumes/Seagate/Galvanize/nj_scripts_all_years.csv',usecols=['drug_name','generic_name'])
#Only getting brand name drugs
scripts = scripts[scripts['drug_name']!=scripts['generic_name']]
#Basiclaly only getting the unique medicine Names
scriptsgrp = scripts.groupby('drug_name')['generic_name'].nunique().to_frame().reset_index()
#Saving for future use
scriptsgrp.to_csv('/Volumes/Seagate/Galvanize/brand_drugs_scripts.csv',index=False)

#Writing a function that makes a dictionary where the keys = Drugs, values = Manufacturer
d = {}
def company_drug(x):
    if x['drug_name'] not in d:
        try:
            df = medsgrp[medsgrp['FDA Product Name'].str.contains \
                                        (x['drug_name'])].groupby('Labeler Name')['NDC'].count()
            df = df.to_frame().reset_index().sort_values('NDC',ascending=False).reset_index().drop('index',axis=1)
            d[x['drug_name']] = df['Labeler Name'][0]
        except IndexError:
            df[x['drug_name']] = np.nan
scriptsgrp.apply(company_drug,axis=1)

#Doing the same thing with a different dataset of companies & their medicines
comps = pd.read_csv('/Volumes/Seagate/Galvanize/ndcxls/product.csv', usecols=[1,3,12])
#Cleaning
#Removing excess spacing & any symbols
comps['PROPRIETARYNAME'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in comps['PROPRIETARYNAME']]
comps['PROPRIETARYNAME'] = comps['PROPRIETARYNAME'].str.strip()
comps['LABELERNAME'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in comps['LABELERNAME']]
comps['LABELERNAME'] = comps['LABELERNAME'].str.strip()
#Grouping
medsgrp = comps.groupby(['PROPRIETARYNAME','LABELERNAME'])['PRODUCTNDC'].nunique().to_frame().reset_index()
def company_drug(x):
    if x['drug_name'] not in d:
        try:
            df = medsgrp[medsgrp['PROPRIETARYNAME'].str.contains \
                                        (x['drug_name'])].groupby('LABELERNAME')['PRODUCTNDC'].count()
            df = df.to_frame().reset_index().sort_values('PRODUCTNDC',ascending=False).reset_index().drop('index',axis=1)
            d[x['drug_name']] = df['LABELERNAME'][0]
        except IndexError:
            df[x['drug_name']] = np.nan
scriptsgrp.apply(company_drug,axis=1)

#Linking all the drugs in our scripts to the companies
scripts = pd.read_csv('/volumes/Seagate/Galvanize/nj_scripts_all_years.csv')
#Writing unknown where I couln't link the company, and generic for the company
dic = {}
def unknown_and_generic(x):
    if (x['drug_name'] == x['generic_name']):
            dic[x['drug_name']] = 'GENERIC'
    elif (x['drug_name'] != x['generic_name']) and (x['drug_name'] not in dic):
        dic[x['drug_name']] = 'UNKNOWN'
scriptsgrp2 = scripts[pd.isnull(scripts['drug_company'])]
scriptsgrp2 = scriptsgrp2.groupby(['drug_name','generic_name'])['npi'].count().to_frame().reset_index()
scriptsgrp.apply(unknown_and_generic,axis=1)
#Add newly linked company names to the df
drug_comp = {**comp_dict, **dic}
scripts["drug_company"] = scripts["drug_name"].map(drug_comp)

#Cleaning
scripts['drug_company'] = scripts['drug_company'].map(lambda x: ' '.join((str(x).replace('INCORPORATED','').replace('CORPORATION','')\
                                    .replace('INC','').replace('CORP','').replace('LLC','').replace('LP','')).split()))
def clean_company_name(df,wrong_name, right_name):
    """
    Input:
        df: df, dataframe to be used
        wrong_name: Str, wrong name that is listed in df
        right_name: Str, right name to be changed to
    Output:
        None
    """
    #Getting all the locations where it says the wrong name
    l = list(df[df['drug_company']==wrong_name].index.values)
    #Replacing all the "ZOLL SERVICES AKA ZOLL LIFECOR" with "ZOLL LIFECOR"
    for i in l:
        df.at[i,'drug_company'] = right_name
#These won't be solved by doing a blanket cleaning so I'm going to just use the same hard coding function I used before
clean_company_name(scripts,'ACTAVIS KADIAN','ACTAVIS')
clean_company_name(scripts,'ACTAVIS PHARMA','ACTAVIS')
clean_company_name(scripts,'ARBOR PHARMACEUTICALS IRELAND LIMITED','ARBOR PHARMACEUTICALS')
clean_company_name(scripts,'ASTELLAS PHARMA US','ASTELLAS')
clean_company_name(scripts,'BRISTOLMYERS SQUIBB AND GILEAD SCIENCE','GILEAD SCIENCES')
clean_company_name(scripts,'BRISTOLMYERS SQUIBB COMPANY','BRISTOLMYERS SQUIBB')
clean_company_name(scripts,'BRISTOLMYERS SQUIBBSANOFI PARTNERSHIP','BRISTOLMYERS SQUIBB')
clean_company_name(scripts,'BRISTOLMYERS SQUIBB PHARMA CO','BRISTOLMYERS SQUIBB')
clean_company_name(scripts,'COVIS PHARMA SARL','COVIS PHARMACEUTICALS')
clean_company_name(scripts,'CSL BEHRING GMBH','CSL BEHRING')
clean_company_name(scripts,'GLAXOSMITHKLINE BIOLOGICALS SA','GLAXOSMITHKLINE')
clean_company_name(scripts,'GSK CONSUMER HEALTHCARE','GSK CONSUMER HEALTH')
clean_company_name(scripts,'IMPAX SPECIALTY PHARMA','IMPAX LABORATORIES')
clean_company_name(scripts,'JANSSEN BIOTECH','JANSSEN PHARMACEUTICALS')
clean_company_name(scripts,'JANSSEN PRODUCTS','JANSSEN PHARMACEUTICALS')
clean_company_name(scripts,'JAZZ PHARMACEUTICALS COMMERCIAL','JAZZ PHARMACEUTICALS')
clean_company_name(scripts,'KREMERS URBAN','KREMERS URBAN PHARMACEUTICALS')
clean_company_name(scripts,'MALLKRODT BRAND PHARMACEUTICALS','MALLKRODT PHARMACEUTICALS')
clean_company_name(scripts,'MALLKRODT','MALLKRODT PHARMACEUTICALS')
clean_company_name(scripts,'MERCK SHARP DOHME','MERCK')
clean_company_name(scripts,'MERCKSCHERINGPLOUGH JV','MERCK')
clean_company_name(scripts,'MYLAN INSTITUTIONAL','MYLAN PHARMACEUTICALS')
clean_company_name(scripts,'MYLAN SPECIALTY','MYLAN PHARMACEUTICALS')
clean_company_name(scripts,'PAR PHARMACEUTICAL','PAR PHARMACEUTICALS')
clean_company_name(scripts,'SCHERING HEALTHCARE PRODUCTS','SCHERING')
clean_company_name(scripts,'TEVA GLOBAL RESPIRATORY RESEARCH','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'TEVA NEUROSCIENCE','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'TEVA PARENTERAL MEDICINES','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'TEVA PHARMACEUTICALS USA','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'TEVA RESPIRATORY','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'TEVA WOMENS HEALTH','TEVA PHARMACEUTICALS')
clean_company_name(scripts,'UCB','UCB PHARMA')
clean_company_name(scripts,'UCB MANUFACTURING','UCB PHARMA')
clean_company_name(scripts,'WYETH LABORATORIES','PFIZER')
clean_company_name(scripts,'WYETH PHARMACEUTICALS A SUBSIDIARY OF PFIZER','PFIZER')

#Saving for future use
scripts.to_csv('/Volumes/Seagate/Galvanize/nj_scripts_all_years.csv',index=False)
#Saving pickled dictionary for future use
pickle.dump(drug_comp, open('script_company_dict.pkl', 'wb'))
