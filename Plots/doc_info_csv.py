#Usage - Make a smaller csv for information regarding all doctors to be used for the search function on the website
import numpy as np
import pandas as pd

#Loading in All Npis to make a file of basic info of all NJ docs (the reason I can't use other CSVs I have is some docs have mulitple specialties & such which this will cover)
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI', 'Provider Gender Code', \
                           'Provider First Name','Provider Last Name (Legal Name)', \
                           'Provider Business Practice Location Address Postal Code', \
                           'Provider First Line Business Practice Location Address', \
                           'Provider Business Practice Location Address State Name', \
                           'Provider Credential Text', 'Provider Business Practice Location Address City Name'], \
                           dtype = {'Provider Business Practice Location Address Postal Code':object})
#Grabbing only the individuals from the npi database, so I can remove orgs from the dataframe
npi = npi[npi['Entity Type Code'].isin([1.0])]
#Dropping this column since I no longer need it
npi.drop(['Entity Type Code'],inplace=True,axis=1)
#Renaming columns
newcols = {'Provider Last Name (Legal Name)':'Last Name','Provider First Name':'First Name', \
           'Provider Credential Text':'Type','Provider First Line Business Practice Location Address':'Address', \
          'Provider Business Practice Location Address State Name':'State','Provider Business Practice Location Address Postal Code':'Zip Code', \
          'Provider Gender Code':'Gender','Provider Business Practice Location Address City Name':'City'}
npi.rename(columns=newcols,inplace=True)
#Grabbing only NJ docs
npi = npi[npi['State'].isin(['NJ'])]
#Grabbing only the first 5 digits of the zip
npi['Zip Code'] = npi['Zip Code'].apply(lambda x: x[:5])
#Cleaning up how I want the columns arranged
npi = npi[npi.columns.tolist()[:1]+npi.columns.tolist()[2:3]+ \
          npi.columns.tolist()[1:2] + npi.columns.tolist()[3:4] + \
          npi.columns.tolist()[-1:] + npi.columns.tolist()[4:-1]]
#Grabbing only the NPIs that I'm using
npi = npi[npi['NPI'].isin(scriptsnjfull.npi.unique())]
npi.fillna('',inplace=True)
#Saving as a csv for future use
npi.to_csv('/Volumes/Seagate/Galvanize/nj_doc_info.csv',index=False)

#Getting the Doctors that only appear in our payments database
doc_info = pd.read_csv('/Volumes/Seagate/Galvanize/nj_doc_info.csv',dtype={'Zip Code':object,'NPI':object})
doc_info.fillna(value='-',inplace=True)
paid = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_all_years_consl.csv',
                            dtype={'zip':object,'npi':object,'company_id':object}, \
                  usecols=[1,2,3,10,11,12,13,26])
notpaid = list(set(doc_info.NPI)-set(paid.npi))
doc_info_paid = doc_info[~doc_info['NPI'].isin(notpaid)]
#Saving for future use
doc_info_paid.to_csv('/Volumes/Seagate/Galvanize/nj_doc_info_paid.csv',index=False)
