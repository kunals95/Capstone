import numpy as np
import pandas as pd
import re

"""2013 DATA"""
#Program year 2013 includes only data collected from August 1– December 31, 2013.
"""Cleaning the Payments Data & adding the NPI along with the payment_id"""
#Load the entire df & selecting only NJ doctors
pay13 = pd.read_csv('/Volumes/Seagate/Galvanize/2013 Open Payments/OP_DTL_GNRL_PGYR2013_P01172018.csv', \
                    dtype={'Recipient_Zip_Code':object,'NDC_of_Associated_Covered_Drug_or_Biological1':object})
#Selecting only NJ docs
pay13nj= pay13[pay13['Recipient_State']=='NJ']
#Loading our pickled NPI dict for all years
npi_full = pickle.load(open('full_linked.pkl', 'rb'))
#Linking NPIs & payment_ids in the df
pay13nj['npi'] = pay13nj['Physician_Profile_ID'].map(npi_full)
#Only getting the columns that have an NPI linked to the payments_id (this is because I'm looking at the payments (which uses payments_id) & prescriptions (which uses NPI), it's no use to me right now if I don't have data for a doctor in both tables)
p13 = pay13nj.loc[np.isfinite(pay13nj['npi'])]
#Looking at the columns so I can choose which ones i want
p13.info()
#These are the columns I found to be useful
cols = [5,6,8,10,12,13,14,19,26,27,30,33,34,38,45,48,49,50,51,52,53,54,55,56,57,63,65]
#Grabbing only those columns
payments_nj13 = p13.iloc[:,cols]
#Renaming columns
new_cols = {'Physician_Profile_ID':'payment_id','Physician_First_Name':'fn','Physician_Last_Name':'ln', \
            'Recipient_Primary_Business_Street_Address_Line1':'address','Recipient_City':'city','Recipient_State':'state', \
            'Recipient_Zip_Code':'zip','Physician_Specialty':'specialty', 'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_ID':'company_id',\
            'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name':'company','Total_Amount_of_Payment_USDollars':'amount', \
            'Form_of_Payment_or_Transfer_of_Value':'form','Nature_of_Payment_or_Transfer_of_Value':'nature', \
            'Physician_Ownership_Indicator':'phys_owns','Record_ID':'record_id', \
            'Product_Indicator':'for_product','Name_of_Associated_Covered_Drug_or_Biological1':'name_d1', \
            'Name_of_Associated_Covered_Drug_or_Biological2':'name_d2','Name_of_Associated_Covered_Drug_or_Biological3':'name_d3', \
            'Name_of_Associated_Covered_Drug_or_Biological4':'name_d4','Name_of_Associated_Covered_Drug_or_Biological5':'name_d5', \
            'NDC_of_Associated_Covered_Drug_or_Biological1':'ndc_d1','NDC_of_Associated_Covered_Drug_or_Biological2':'ndc_d2', \
            'NDC_of_Associated_Covered_Drug_or_Biological3':'ndc_d3','NDC_of_Associated_Covered_Drug_or_Biological4':'ndc_d4', \
            'NDC_of_Associated_Covered_Drug_or_Biological5':'ndc_d5','Program_Year':'year'}
payments_nj13.rename(columns=new_cols,inplace=True)
#Saving as a csv for future use
payments_nj13.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2013_consl.csv',index=False)
#Reading the csv that we saved, The NDCs have to be read as objects becuase otherwise the leading 0s get cut
payments_nj_13 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2013_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':np.int64})
#Cleaning first name, last name, drug names, cities, zip codes, & addresses
#Making a function to do this:
#Cleaning first name, last name, drug names, cities, zip codes, & addresses
#Making a function to do this:
def clean_name(df, col_list):
    """
    Cleans the first name, last name, drug names, cities, & addresses
    Input:
        df: df, name of dataframe to clean
        col: list, list of strings of the names of columns to clean
    Output:
        None
    """
    for col in col_list:
        df[col] = df[col].map(lambda x: str(x).replace(' ',''))
        df[col] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in df[col]]
        if col == 'zip':
            #Special cleaning for zip column
            df[col] = [x.replace('-','') for x in df[col]]
            #If the 9 digit zip is only 8 long, add a 0 in front (NJ zips typically have a leading 0 which might have been cut)
            #Also do the same if the 5 digit zip is only 4 long
            df[col] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in df[col]]
clean_name(payments_nj_13,['fn','ln','name_d1','name_d2','name_d3','name_d4','name_d5','city','zip'])
#I don't want to remove spaces in the addresses so I'll do that seperate:
payments_nj_13['address'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_13['address']]
#Cleaning the Company Names so 1 company_id is matched with 1 company
#I grouped companies by their company id & name (df) and then found the IDs that showed up belonging to more than 1 company (df2)
df = payments_nj_13.groupby(['company_id','company']).sum()['amount']
df = df.to_frame()
df.reset_index(inplace=True)
df2 = df[df['company_id'].isin(df['company_id'][df['company_id'].duplicated()])].sort_values("company_id")
#Removes punctuation & uppercases string
payments_nj_13['company'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_13['company']]
#Removes Extra words from company names (incorporated, corporation, inc, corp, llc, lp) & extra spacing or leading/ending spaces
payments_nj_13['company'] = payments_nj_13['company'].map(lambda x: ' '.join((str(x).replace('INCORPORATED','').replace('CORPORATION','')\
                                    .replace('INC','').replace('CORP','').replace('LLC','').replace('LP','')).split()))
"""
There were some special cases where this didn't work (Ex: SORIN CRM US != SORIN GROUP CRM USA)
Also 1 company got acquired by another (HZNP USA acquired VIDARA Therapeutics) so I'm going to hard code these special cases in
"""
#Writing a function to clean company names
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
    l = list(df[df['company']==wrong_name].index.values)
    #Replacing all the "ZOLL SERVICES AKA ZOLL LIFECOR" with "ZOLL LIFECOR"
    for i in l:
        df.at[i,'company'] = right_name
clean_company_name(payments_nj_13, 'ZOLL SERVICES AKA ZOLL LIFECOR', 'ZOLL LIFECOR')
clean_company_name(payments_nj_13, 'SORIN GROUP CRM USA','SORIN CRM USA')
clean_company_name(payments_nj_13, 'DJO','DJO GLOBAL')
#VIDARA THERAPEUTICS got bought by HZNP USA
clean_company_name(payments_nj_13, 'VIDARA THERAPEUTICS','HZNP USA')
#Saving this as a CSV for future use (it's saved as the same as the one we loaded, but now it's cleaned)
payments_nj_13.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2013_consl.csv',index=False)



"""2014 DATA"""
"""Cleaning the Payments Data & adding the NPI along with the payment_id"""
#Load the entire df & selecting only NJ doctors
pay14 = pd.read_csv('/Volumes/Seagate/Galvanize/2014 Open Payments/OP_DTL_GNRL_PGYR2014_P01172018.csv', \
                    dtype={'Recipient_Zip_Code':object,'NDC_of_Associated_Covered_Drug_or_Biological1':object})
#Selecting only NJ docs
pay14nj= pay14[pay14['Recipient_State']=='NJ']
#Linking NPIs & payment_ids in the df
pay14nj['npi'] = pay14nj['Physician_Profile_ID'].map(npi_full)
#Only getting the columns that have an NPI linked to the payments_id (this is because I'm looking at the payments (which uses payments_id) & prescriptions (which uses NPI), it's no use to me right now if I don't have data for a doctor in both tables)
p14 = pay14nj.loc[np.isfinite(pay14nj['npi'])]
#Looking at the columns so I can choose which ones i want
p14.info()
#These are the columns I found to be useful
cols = [5,6,8,10,12,13,14,19,26,27,30,33,34,38,45,48,49,50,51,52,53,54,55,56,57,63,65]
#Grabbing only those columns
payments_nj14 = p14.iloc[:,cols]
#Renaming columns
new_cols = {'Physician_Profile_ID':'payment_id','Physician_First_Name':'fn','Physician_Last_Name':'ln', \
            'Recipient_Primary_Business_Street_Address_Line1':'address','Recipient_City':'city','Recipient_State':'state', \
            'Recipient_Zip_Code':'zip','Physician_Specialty':'specialty', 'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_ID':'company_id',\
            'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name':'company','Total_Amount_of_Payment_USDollars':'amount', \
            'Form_of_Payment_or_Transfer_of_Value':'form','Nature_of_Payment_or_Transfer_of_Value':'nature', \
            'Physician_Ownership_Indicator':'phys_owns','Record_ID':'record_id', \
            'Product_Indicator':'for_product','Name_of_Associated_Covered_Drug_or_Biological1':'name_d1', \
            'Name_of_Associated_Covered_Drug_or_Biological2':'name_d2','Name_of_Associated_Covered_Drug_or_Biological3':'name_d3', \
            'Name_of_Associated_Covered_Drug_or_Biological4':'name_d4','Name_of_Associated_Covered_Drug_or_Biological5':'name_d5', \
            'NDC_of_Associated_Covered_Drug_or_Biological1':'ndc_d1','NDC_of_Associated_Covered_Drug_or_Biological2':'ndc_d2', \
            'NDC_of_Associated_Covered_Drug_or_Biological3':'ndc_d3','NDC_of_Associated_Covered_Drug_or_Biological4':'ndc_d4', \
            'NDC_of_Associated_Covered_Drug_or_Biological5':'ndc_d5','Program_Year':'year'}
payments_nj14.rename(columns=new_cols,inplace=True)
#Saving as a csv for future use
payments_nj14.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2014_consl.csv',index=False)
#Reading the csv that we saved, The NDCs have to be read as objects becuase otherwise the leading 0s get cut
payments_nj_14 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2014_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':np.int64})
#Cleaning first name, last name, drug names, cities, zip codes, & addresses
clean_name(payments_nj_14,['fn','ln','name_d1','name_d2','name_d3','name_d4','name_d5','city','zip'])
#I don't want to remove spaces in the addresses so I'll do that seperate:
payments_nj_14['address'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_14['address']]
#Cleaning the Company Names so 1 company_id is matched with 1 company
#Removes punctuation & uppercases string
payments_nj_14['company'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_14['company']]
#Removes Extra words from company names (incorporated, corporation, inc, corp, llc, lp) & extra spacing or leading/ending spaces
payments_nj_14['company'] = payments_nj_14['company'].map(lambda x: ' '.join((str(x).replace('INCORPORATED','').replace('CORPORATION','')\
                                    .replace('INC','').replace('CORP','').replace('LLC','').replace('LP','')).split()))
#I grouped companies by their company id & name (df) and then found the IDs that showed up belonging to more than 1 company (df2)
df = payments_nj_14.groupby(['company_id','company']).sum()['amount']
df = df.to_frame()
df.reset_index(inplace=True)
df2 = df[df['company_id'].isin(df['company_id'][df['company_id'].duplicated()])].sort_values("company_id")
"""
There were some special cases where this didn't work (Ex: BIOGEN IDEC != BIOGEN) so I'm going to hard code these special cases in
"""
clean_company_name(payments_nj_14, 'BIOGEN IDEC', 'BIOGEN')
#Saving this as a CSV for future use (it's saved as the same as the one we loaded, but now it's cleaned)
payments_nj_14.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2014_consl.csv',index=False)



"""2015 DATA"""
"""Cleaning the Payments Data & adding the NPI along with the payment_id"""
#Load the entire df & selecting only NJ doctors
pay15 = pd.read_csv('/Volumes/Seagate/Galvanize/2015 Open Payments/OP_DTL_GNRL_PGYR2015_P01172018.csv', \
                    dtype={'Recipient_Zip_Code':object,'NDC_of_Associated_Covered_Drug_or_Biological1':object})
#Selecting only NJ docs
pay15nj= pay15[pay15['Recipient_State']=='NJ']
#Linking NPIs & payment_ids in the df
pay15nj['npi'] = pay15nj['Physician_Profile_ID'].map(npi_full)
#Only getting the columns that have an NPI linked to the payments_id (this is because I'm looking at the payments (which uses payments_id) & prescriptions (which uses NPI), it's no use to me right now if I don't have data for a doctor in both tables)
p15 = pay15nj.loc[np.isfinite(pay15nj['npi'])]
#Looking at the columns so I can choose which ones i want
p15.info()
#These are the columns I found to be useful
cols = [5,6,8,10,12,13,14,19,26,27,30,33,34,38,45,48,49,50,51,52,53,54,55,56,57,63,65]
#Grabbing only those columns
payments_nj15 = p15.iloc[:,cols]
#Renaming columns
new_cols = {'Physician_Profile_ID':'payment_id','Physician_First_Name':'fn','Physician_Last_Name':'ln', \
            'Recipient_Primary_Business_Street_Address_Line1':'address','Recipient_City':'city','Recipient_State':'state', \
            'Recipient_Zip_Code':'zip','Physician_Specialty':'specialty', 'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_ID':'company_id',\
            'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name':'company','Total_Amount_of_Payment_USDollars':'amount', \
            'Form_of_Payment_or_Transfer_of_Value':'form','Nature_of_Payment_or_Transfer_of_Value':'nature', \
            'Physician_Ownership_Indicator':'phys_owns','Record_ID':'record_id', \
            'Product_Indicator':'for_product','Name_of_Associated_Covered_Drug_or_Biological1':'name_d1', \
            'Name_of_Associated_Covered_Drug_or_Biological2':'name_d2','Name_of_Associated_Covered_Drug_or_Biological3':'name_d3', \
            'Name_of_Associated_Covered_Drug_or_Biological4':'name_d4','Name_of_Associated_Covered_Drug_or_Biological5':'name_d5', \
            'NDC_of_Associated_Covered_Drug_or_Biological1':'ndc_d1','NDC_of_Associated_Covered_Drug_or_Biological2':'ndc_d2', \
            'NDC_of_Associated_Covered_Drug_or_Biological3':'ndc_d3','NDC_of_Associated_Covered_Drug_or_Biological4':'ndc_d4', \
            'NDC_of_Associated_Covered_Drug_or_Biological5':'ndc_d5','Program_Year':'year'}
payments_nj15.rename(columns=new_cols,inplace=True)
#Saving as a csv for future use
payments_nj15.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2015_consl.csv',index=False)
#Reading the csv that we saved, The NDCs have to be read as objects becuase otherwise the leading 0s get cut
payments_nj_15 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2015_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':np.int64})
#Cleaning first name, last name, drug names, cities, zip codes, & addresses
clean_name(payments_nj_15,['fn','ln','name_d1','name_d2','name_d3','name_d4','name_d5','city','zip'])
#I don't want to remove spaces in the addresses so I'll do that seperate:
payments_nj_15['address'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_15['address']]
#Cleaning the Company Names so 1 company_id is matched with 1 company
#I grouped companies by their company id & name (df) and then found the IDs that showed up belonging to more than 1 company (df2)
df = payments_nj_15.groupby(['company_id','company']).sum()['amount']
df = df.to_frame()
df.reset_index(inplace=True)
df2 = df[df['company_id'].isin(df['company_id'][df['company_id'].duplicated()])].sort_values("company_id")
#Removes punctuation & uppercases string
payments_nj_15['company'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_15['company']]
#Removes Extra words from company names (incorporated, corporation, inc, corp, llc, lp) & extra spacing or leading/ending spaces
payments_nj_15['company'] = payments_nj_15['company'].map(lambda x: ' '.join((str(x).replace('INCORPORATED','').replace('CORPORATION','')\
                                    .replace('INC','').replace('CORP','').replace('LLC','').replace('LP','')).split()))
"""
There were no special cases for this year where I had to hard code changing a compnay name so 1 company_id = 1 company
"""
#Saving this as a CSV for future use (it's saved as the same as the one we loaded, but now it's cleaned)
payments_nj_15.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2015_consl.csv',index=False)



"""2016 DATA"""
"""Cleaning the Payments Data & adding the NPI along with the payment_id"""
#These are the columns I found to be useful
new_cols = {'Physician_Profile_ID':'payment_id','Physician_First_Name':'fn','Physician_Last_Name':'ln', \
            'Recipient_Primary_Business_Street_Address_Line1':'address','Recipient_City':'city','Recipient_State':'state', \
            'Recipient_Zip_Code':'zip','Physician_Specialty':'specialty', 'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_ID':'company_id',\
            'Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name':'company','Total_Amount_of_Payment_USDollars':'amount', \
            'Form_of_Payment_or_Transfer_of_Value':'form','Nature_of_Payment_or_Transfer_of_Value':'nature', \
            'Physician_Ownership_Indicator':'phys_owns','Record_ID':'record_id', \
            'Product_Indicator':'for_product','Name_of_Associated_Covered_Drug_or_Biological1':'name_d1', \
            'Name_of_Associated_Covered_Drug_or_Biological2':'name_d2','Name_of_Associated_Covered_Drug_or_Biological3':'name_d3', \
            'Name_of_Associated_Covered_Drug_or_Biological4':'name_d4','Name_of_Associated_Covered_Drug_or_Biological5':'name_d5', \
            'NDC_of_Associated_Covered_Drug_or_Biological1':'ndc_d1','NDC_of_Associated_Covered_Drug_or_Biological2':'ndc_d2', \
            'NDC_of_Associated_Covered_Drug_or_Biological3':'ndc_d3','NDC_of_Associated_Covered_Drug_or_Biological4':'ndc_d4', \
            'NDC_of_Associated_Covered_Drug_or_Biological5':'ndc_d5','Program_Year':'year'}
#Load the  df & selecting only NJ doctors
pay16 = pd.read_csv('/Volumes/Seagate/Galvanize/2016 Open Payments/OP_DTL_GNRL_PGYR2016_P01172018.csv', \
                    dtype={'Recipient_Zip_Code':object,'NDC_of_Associated_Covered_Drug_or_Biological1':object}, \
                    usecols=list(new_cols.keys()))
#Selecting only NJ docs
pay16nj= pay16[pay16['Recipient_State']=='NJ']
#Linking NPIs & payment_ids in the df
pay16nj['npi'] = pay16nj['Physician_Profile_ID'].map(npi_full)
#Only getting the columns that have an NPI linked to the payments_id (this is because I'm looking at the payments (which uses payments_id) & prescriptions (which uses NPI), it's no use to me right now if I don't have data for a doctor in both tables)
payments_nj16 = pay16nj.loc[np.isfinite(pay16nj['npi'].astype(float))]
#Renaming columns
payments_nj16.rename(columns=new_cols,inplace=True)
#Saving as a csv for future use
payments_nj16.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2016_consl.csv',index=False)
#Reading the csv that we saved, The NDCs have to be read as objects becuase otherwise the leading 0s get cut
payments_nj_16 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2016_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':np.int64})
#Cleaning first name, last name, drug names, cities, zip codes, & addresses
clean_name(payments_nj_16,['fn','ln','name_d1','name_d2','name_d3','name_d4','name_d5','city','zip'])
#I don't want to remove spaces in the addresses so I'll do that seperate:
payments_nj_16['address'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_16['address']]
#Cleaning the Company Names so 1 company_id is matched with 1 company
#I grouped companies by their company id & name (df) and then found the IDs that showed up belonging to more than 1 company (df2)
df = payments_nj_16.groupby(['company_id','company']).sum()['amount']
df = df.to_frame()
df.reset_index(inplace=True)
df2 = df[df['company_id'].isin(df['company_id'][df['company_id'].duplicated()])].sort_values("company_id")
#Removes punctuation & uppercases string
payments_nj_16['company'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in payments_nj_16['company']]
#Removes Extra words from company names (incorporated, corporation, inc, corp, llc, lp) & extra spacing or leading/ending spaces
payments_nj_16['company'] = payments_nj_16['company'].map(lambda x: ' '.join((str(x).replace('INCORPORATED','').replace('CORPORATION','')\
                                    .replace('INC','').replace('CORP','').replace('LLC','').replace('LP','')).split()))
"""
There were no special cases for this year where I had to hard code changing a compnay name so 1 company_id = 1 company
"""
#Saving this as a CSV for future use (it's saved as the same as the one we loaded, but now it's cleaned)
payments_nj_16.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2016_consl.csv',index=False)




#Joining all the years into 1 df
payments_nj_full = pd.concat([payments_nj_13,payments_nj_14,payments_nj_15])
#Rearranging the columns (npi was last & I wanted it closer to the names)
payments_nj_full = payments_nj_full[payments_nj_full.columns.tolist()[-7:-6]+ payments_nj_full.columns.tolist()[-8:-7] + \
                     payments_nj_full.columns.tolist()[5:6]+payments_nj_full.columns.tolist()[7:8] + \
                     payments_nj_full.columns.tolist()[:1]+payments_nj_full.columns.tolist()[2:3] + \
                     payments_nj_full.columns.tolist()[-3:-2]+payments_nj_full.columns.tolist()[-1:] + \
                     payments_nj_full.columns.tolist()[-4:-3]+payments_nj_full.columns.tolist()[4:5]+ \
                     payments_nj_full.columns.tolist()[3:4]+payments_nj_full.columns.tolist()[1:2] + \
                     payments_nj_full.columns.tolist()[6:7]+payments_nj_full.columns.tolist()[13:14] + \
                     payments_nj_full.columns.tolist()[-6:-5] + payments_nj_full.columns.tolist()[-5:-4]+ \
                     payments_nj_full.columns.tolist()[8:13] + payments_nj_full.columns.tolist()[14:19]+ \
                     payments_nj_full.columns.tolist()[-2:-1]]
#We have some NaNs saved as strings so just converting them back
payments_nj_full.replace(to_replace='NAN',value=np.nan,inplace=True)
#Cleaning the Company Names so 1 company_id is matched with 1 company
#I grouped companies by their company id & name (df) and then found the IDs that showed up belonging to more than 1 company (df2)
df = payments_nj_full.groupby(['company_id','company']).sum()['amount']
df = df.to_frame()
df.reset_index(inplace=True)
df.head()
df2 = df[df['company_id'].isin(df['company_id'][df['company_id'].duplicated()])].sort_values("company_id")
#These won't be solved by doing a blanket cleaning so I'm going to just use the same hard coding function I used before
"""After doing some research I found that most of these companies were bought out by others or changed their names
Typically the name with the smaller sum donated was changed to the larger name (since this typically meant it was more common)
Unless the smaller sum donated company bought out the other"""
conv = {'ZIMMER HOLDING':'ZIMMER BIOMET HOLDINGS','ZOLL SERVICES AKA ZOLL LIFECOR':'ZOLL LIFECOR', \
            'BIOGEN IDEC':'BIOGEN','GRIFOLS SHARED SERVICES NORTH AMERICA':'GRIFOLS SHARED SERVICES', \
           'GRIFOLS':'GRIFOLS SHARED SERVICES','IMPLANT DIRECT INTERNATIONAL':'IMPLANT DIRECT SYBRON INTERNATIONAL', \
           'AASTROM BIOSCIENCES':'VERICEL', 'APOLLO ENDOSURGERY US':'APOLLO ENDOSURGERY', \
           'AEROCRINE':'CIRCASSIA PHARMACEUTICALS', 'VISIONCARE OPHTHALMIC TECHNOLOGIES':'VISIONCARE', \
           'THERAVANCE BIOPHARMA':'THERAVANCE', 'PROSTRAKAN':'KYOWA KIRIN','HOSPIRA WORLDWIDE':'HOSPIRA', \
           'DJO GLOBAL':'DJO','THERAVANCE BIOPHARMA':'THERAVANCE','EVERETT LABORATORIES':'EXELTIS USA', \
            'VISIONCARE':'VISIONCARE OPHTHALMIC TECHNOLOGIES','CORNERSTONE THERAPEUTICS':'CHIESI USA', \
           'CREALTA PHARMACEUTICALS':'HORIZON PHARMA RHEUMATOLOGY'}
for old_comp in conv:
    clean_company_name(payments_nj_full, old_comp, conv[old_comp])
#Saving this as a CSV for future use
payments_nj_full.to_csv('/Volumes/Seagate/Galvanize/nj_payments_all_years_consl.csv',index=False)
