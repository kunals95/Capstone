import numpy as np
import pandas as pd
import re
import os

"""2013 DATA"""

"""Cleaning the Payments Data for joining & grabbing only the NJ data"""
#First I load only a small subset of the data to get an idea of the columns I'll need to use for joining
payments13 = pd.read_csv('/Volumes/Seagate/Galvanize/2013 Open Payments/OP_DTL_GNRL_PGYR2013_P01172018.csv', nrows=100)
#This is so I can view all the columns since otherwise they get cut off
payments13[:1].to_dict('index')
#Then I pick only the columns I want & load the entire csv
pay13 = pd.read_csv('/Volumes/Seagate/Galvanize/2013 Open Payments/OP_DTL_GNRL_PGYR2013_P01172018.csv', \
                    usecols=['Physician_Profile_ID','Physician_First_Name','Physician_Middle_Name', \
                             'Physician_Last_Name','Recipient_State','Total_Amount_of_Payment_USDollars', \
                            'Recipient_Primary_Business_Street_Address_Line1', 'Physician_Specialty', 'Recipient_Zip_Code'], \
                            dtype={'Recipient_Zip_Code':object})
#Grabbing only the NJ practioners
p13 = pay13[pay13['Recipient_State'].isin(['NJ'])]
"""Saving as a CSV for future use"""
p13.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2013.csv')
#Renaming the columns so they're easier to call
l = p13.columns
p13.rename(columns={l[0]:'id',l[1]:'fn',l[2]:'mn',l[3]:'ln',l[4]:'address1',l[5]:'state',l[6]:'zip',l[-2]:'specialty',l[-1]:'amount'},inplace=True)
#Cleaning the first & last name (removing space & symbols) and the address (removing any symbols)
p13['ln'] = p13['ln'].map(lambda str(x): x.replace(' ',''))
p13['fn'] = p13['fn'].map(lambda str(x): x.replace(' ',''))
p13['mn'] = p13['mn'].map(lambda str(x): x.replace(' ',''))
p13['ln'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p13['ln']]
p13['fn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p13['fn']]
p13['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p13['mn']]
p13['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p13['address1']]
#Cleaning the zip codes (removing dashes & making sure they are not missing the leading 0 that most NJ zip codes have)
p13['zip'] = [x.replace('-','') for x in p13['zip']]
p13['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in p13['zip']]
#Making a column for the 5 digit zip
p13['zip5'] = p13['zip'].map(lambda x: x[:5])

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
p13.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Groupby the ID so we can shrink our df
payids = p13.groupby(['id','fn','ln','mn','zip','specialty','address1']).count()['amount'].to_frame().reset_index(inplace=True)
#Dropping amount column because it's not necessary rn
payids.drop('amount',axis=1,inplace=True)
#Finding all the mispelled names/addresses/etc.
mis = payids[payids['id'].isin(payids['id'][payids['id'].duplicated()])].sort_values("id")
#Saving as a CSV for future use
payids.to_csv('/Volumes/Seagate/Galvanize/nj_13_payment_ids.csv')
mis.to_csv('/Volumes/Seagate/Galvanize/nj_13_multi_name_payment_ids.csv')


"""Cleaning the Prescriptions Data for joining & grabbing only the NJ data"""
#First I load only a small subset of the data to get an idea of the columns I'll need to use for joining
prescrip13 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2013.csv', nrows=100)
#This is so I can view all the columns since otherwise they get cut off
prescrip13[:1].to_dict('index')
#Then I pick only the columns I want & load the entire csv
scripts13 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2013.csv',usecols=list(pres13.columns[:6]))
#Grabbing only the NJ practioners
scripts13nj = scripts13[scripts13['nppes_provider_state'].isin(['NJ'])]
#Renaming the columns so they're easier to call
l = scripts13nj.columns
scripts13nj.rename(columns={l[0]:'npi',l[1]:'ln',l[2]:'fn',l[3]:'city',l[4]:'state',l[5]:'specialty'},inplace=True)
#Upper casing the first name, last name, and city
scripts13nj['ln'] = [x.upper() for x in scripts13nj['ln']]
scripts13nj['fn'] = [str(x).upper() for x in scripts13nj['fn']]
scripts13nj['city'] = [x.upper() for x in scripts13nj['city']]
"""Saving as a csv for future use"""
scripts13nj.to_csv('/Volumes/Seagate/Galvanize/2013_scriptsnj.csv')
#Grouping so I don't have a bunch of duplicate NPIs & I can look for mispellings
s13 = scripts13nj.groupby(['npi','ln','fn','city','specialty']).count()['state'].to_frame()
#Resetting the index becuase all my groupbys are now the index, which wont work for a merge
s13.reset_index(inplace=True)
#Checking if any of the people's names are misspelled
dup13 = s13[s13['npi'].isin(s13['npi'][s13['npi'].duplicated()])].sort_values("npi")
    #There were none
"""Combining with NPI df so I can remove all the organizations"""
#First I load only a small subset of the data to get an idea of the columns I'll need to use for joining
npifull = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', nrows=100)
#This is so I can view all the columns since otherwise they get cut off
npifull[:1].to_dict('index')
#Then I pick only the columns I want & load the entire csv
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI','Provider Middle Name', \
                           'Provider First Name','Provider Last Name (Legal Name)', \
                           'Provider Business Practice Location Address Postal Code', \
                           'Provider First Line Business Practice Location Address', \
                           'Provider Business Practice Location Address State Name'], \
                           dtype = {'Provider Business Practice Location Address Postal Code':object})
#Grabbing only the NJ practioners
npi_nj = npi[npi['Provider Business Practice Location Address State Name'].isin(['NJ'])]
#Grabbing only the INDIVIDUALS not ORGANIZATIONS (who also have an NPI)
npi_idv = npi_nj[npi_nj['Entity Type Code'].isin([1.0])]
#Renaming so its easier for me to use later on
npi_idv.rename(columns={'Provider Last Name (Legal Name)':'ln',  \
                      'Provider First Name':'fn', 'Provider Middle Name':'mn', \
                      'Provider First Line Business Practice Location Address':'address1', \
                      'Provider Business Practice Location Address State Name':'state', \
                      'Provider Business Practice Location Address Postal Code':'zip'},inplace=True)
#Saving as a csv for future use
npi_idv.to_csv('/Volumes/Seagate/Galvanize/nj_idv_npi_may.csv')
#Joining the Scripts & NPI
"""Reasons for doing this:
    1. To get the Middle name of the individual
    2. To remove all organizations from the prescriptions data
    3. To get the address & zip of the individual
"""
script_npi = s13.merge(npi_idv, left_on='npi',right_on='NPI')
#Checking to make sure the ones not in the joined df are actually only organizations
notjoined = npi_nj[npi_nj['NPI'].isin(list(s13[~s13.npi.isin(script_npi.NPI)]['npi']))]
len(notjoined[notjoined['Entity Type Code'].isin([1.0])])
    #1 = Indivduals, There were none
#Dropping unecessary column & the NPI column because it's repeated
script_npi.drop(['Entity Type Code','NPI','state_x','state_y'],axis=1,inplace=True)
#Cleaning the joined dataframe, removing essentially all punctuation & spaces from the first or last name
script_npi['ln_x'] = script_npi['ln_x'].map(lambda x: x.replace(' ',''))
script_npi['ln_y'] = script_npi['ln_y'].map(lambda x: x.replace(' ',''))
script_npi['fn_x'] = script_npi['fn_x'].map(lambda x: x.replace(' ',''))
script_npi['fn_y'] = script_npi['fn_y'].map(lambda x: x.replace(' ',''))
script_npi['mn'] = script_npi['mn'].map(lambda x: str(x).replace(' ',''))
script_npi['ln_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_x']]
script_npi['ln_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_y']]
script_npi['fn_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_x']]
script_npi['fn_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_y']]
script_npi['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['mn']]
script_npi['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['address1']]
#Cleaning the zip codes, NJ has a leading 0 in the zip so it might of been dropped
script_npi['zip'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['zip']]
script_npi['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in script_npi['zip']]

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
script_npi.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Making a column for the 5 digit zip
script_npi['zip5'] = script_npi['zip'].map(lambda x: x[:5])
"""Dealing with mismatched/mispelled names"""
#This just lets me see names where the first name & last name don't match up
script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) & (script_npi['fn_x']!=script_npi['fn_y'])]
#There's a really mismatched name here, (ABDELGHANI, WALEED) vs (SHOMAN, ADAM)
#I looked it up and Adam is the right one so I'm going to change it manually
script_npi.at[6940,'ln_x'] = 'SHOMAN'
script_npi.at[6940,'fn_x'] = 'ADAM'
#Making a new table of the mismatched names
mis_name = script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) | (script_npi['fn_x']!=script_npi['fn_y'])]
#Saving these as CSVs for future use
script_npi.to_csv('/Volumes/Seagate/Galvanize/nj_13_scrip_npi.csv')
mis_name.to_csv('/Volumes/Seagate/Galvanize/nj_13_multi_name_npi.csv')


"""Making 1 dictionary for each NPI & 1 dictionary for each Payment_ID
Keys = NPI or Payment ID
Values = Dictionary of:
    Keys: first name(fn), last name(ln), 5 digit zip(zip5), address(address1), Physician Specialty (specialty)
    Values: All the values that are listed in the NPI/Prescriptions or Payments data for that Key
        This is due to misspellings, extra info (Ex: Road instead of Rd), etc.
"""
#Payment ID function
d = {}
def payment_id(x):
    if x['id'] in d:
        d[x['id']]['fn'].add(x['fn'])
        d[x['id']]['ln'].add(x['ln'])
        d[x['id']]['zip5'].add(x['zip5'])
        d[x['id']]['address1'].add(x['address1'])
        d[x['id']]['specialty'].update(list(x['specialty'].split('|')))
    elif x['id'] not in d:
        d[x['id']] = {'fn':set([x['fn']]), \
                     'ln':set([x['ln']]), \
                     'zip5':set([x['zip5']]), \
                     'address1':set([x['address1']]), \
                     'specialty':set(list(x['specialty'].split('|')))}
#Applying the function to our payment_ids
payids.apply(payment_id,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(d, open('13paydict.pkl', 'wb'))

#Prescriptions & NPI function
n = {}
def script_npi_dict(x):
    if x['npi'] in n:
        n[x['npi']]['fn'].update([x['fn_x'],x['fn_y']])
        n[x['npi']]['ln'].update([x['ln_y'],x['ln_y']])
        n[x['npi']]['zip5'].add(x['zip5'])
        n[x['npi']]['address1'].add(x['address1'])
        n[x['npi']]['specialty'].add(x['specialty'])
    elif x['npi'] not in n:
        n[x['npi']] = {'fn':set([x['fn_x'],x['fn_y']]), \
                     'ln':set([x['ln_x'],x['ln_y']]), \
                     'zip5':set([x['zip5']]), \
                     'address1':set([x['address1']]), \
                     'specialty':set([x['specialty']])}
#Applying the function to our payment_ids
script_npi.apply(script_npi_dict,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(n, open('13npidict.pkl', 'wb'))
#Just renaming the 2 dictionaries from above
pay_id_13_dict = d
npi_13_dict = n

"""Combining the NPI & Payment_ID dictionaries to match them up"""
npi_pay_dict = {}
#Function
def combine_npi_payid(d,n):
    """
    Input:
        d - Dict of pay_ids as keys with dict as value containing address, fn, ln, specialty, zip5 as keys
                & all possible alts. for that pay_id as values
        n - Dict of npis as keys with dict as value containing address, fn, ln, specialty, zip5 as keys
                & all possible alts. for that npi as values
    Output:
        None
    """
    for pay_id in d:
        for npi in n:
            t_count = 0
            for val in d[pay_id]:
                if len(d[pay_id][val].intersection(n[npi][val])) >0:
                    t_count += 1
            if t_count >= 4:
                npi_pay_dict[pay_id] = npi
#Combining them
combine_npi_payid(pay_id_13_dict, npi_13_dict)
#Pickling it so I can utilize it with ease later
pickle.dump(npi_pay_dict, open('13_linked.pkl', 'wb'))




"""2014 DATA"""

"""Cleaning the Payments Data for joining & grabbing only the NJ data"""
#Loading csv
pay14 = pd.read_csv('/Volumes/Seagate/Galvanize/2014 Open Payments/OP_DTL_GNRL_PGYR2014_P01172018.csv', \
                    usecols=['Physician_Profile_ID','Physician_First_Name','Physician_Middle_Name', \
                             'Physician_Last_Name','Recipient_State','Total_Amount_of_Payment_USDollars', \
                            'Recipient_Primary_Business_Street_Address_Line1', 'Physician_Specialty', 'Recipient_Zip_Code'], \
                            dtype={'Recipient_Zip_Code':object})
#Grabbing only the NJ practioners
p14 = pay14[pay14['Recipient_State'].isin(['NJ'])]
"""Saving as a CSV for future use"""
p14.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2014.csv')
#Renaming the columns so they're easier to call
l = p14.columns
p14.rename(columns={l[0]:'id',l[1]:'fn',l[2]:'mn',l[3]:'ln',l[4]:'address1',l[5]:'state',l[6]:'zip',l[-2]:'specialty',l[-1]:'amount'},inplace=True)
#Cleaning the first & last name (removing space & symbols) and the address (removing any symbols)
p14['ln'] = p14['ln'].map(lambda x: str(x).replace(' ',''))
p14['fn'] = p14['fn'].map(lambda x: str(x).replace(' ',''))
p14['mn'] = p14['mn'].map(lambda x: str(x).replace(' ',''))
p14['ln'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p14['ln']]
p14['fn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p14['fn']]
p14['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p14['mn']]
p14['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p14['address1']]
#Cleaning the zip codes (removing dashes & making sure they are not missing the leading 0 that most NJ zip codes have)
p14['zip'] = [x.replace('-','') for x in p14['zip']]
p14['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in p14['zip']]
#Making a column for the 5 digit zip
p14['zip5'] = p14['zip'].map(lambda x: x[:5])

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
p14.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Groupby the ID so we can shrink our df
payids = p14.groupby(['id','fn','ln','mn','zip','specialty','address1']).count()['amount'].to_frame().reset_index(inplace=True)
#Dropping amount column because it's not necessary rn
payids.drop('amount',axis=1,inplace=True)
#Finding all the mispelled names/addresses/etc.
mis = payids[payids['id'].isin(payids['id'][payids['id'].duplicated()])].sort_values("id")
#Saving as a CSV for future use
payids.to_csv('/Volumes/Seagate/Galvanize/nj_14_payment_ids.csv')
mis.to_csv('/Volumes/Seagate/Galvanize/nj_14_multi_name_payment_ids.csv')


"""Cleaning the Prescriptions Data for joining & grabbing only the NJ data"""
#First I load only a small subset of the data to get an idea of the columns I'll need to use for joining
prescrip14 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2014.csv', nrows=100)
#This is so I can view all the columns since otherwise they get cut off
prescrip14[:1].to_dict('index')
#Then I pick only the columns I want & load the entire csv
scripts14 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2014.csv',usecols=list(pres14.columns[:6]))
#Grabbing only the NJ practioners
scripts14nj = scripts14[scripts14['nppes_provider_state'].isin(['NJ'])]
#Renaming the columns so they're easier to call
l = scripts14nj.columns
scripts14nj.rename(columns={l[0]:'npi',l[1]:'ln',l[2]:'fn',l[3]:'city',l[4]:'state',l[5]:'specialty'},inplace=True)
#Upper casing the first name, last name, and city
scripts14nj['ln'] = [x.upper() for x in scripts14nj['ln']]
scripts14nj['fn'] = [str(x).upper() for x in scripts14nj['fn']]
scripts14nj['city'] = [x.upper() for x in scripts14nj['city']]
"""Saving as a csv for future use"""
scripts14nj.to_csv('/Volumes/Seagate/Galvanize/2014_scriptsnj.csv')
#Grouping so I don't have a bunch of duplicate NPIs & I can look for mispellings
s14 = scripts14nj.groupby(['npi','ln','fn','city','specialty']).count()['state'].to_frame()
#Resetting the index becuase all my groupbys are now the index, which wont work for a merge
s14.reset_index(inplace=True)
#Checking if any of the people's names are misspelled
dup14 = s14[s14['npi'].isin(s14['npi'][s14['npi'].duplicated()])].sort_values("npi")
    #There were none
"""Combining with NPI df so I can remove all the organizations"""
#Joining the Scripts & NPI
"""Reasons for doing this:
    1. To get the Middle name of the individual
    2. To remove all organizations from the prescriptions data
    3. To get the address & zip of the individual
"""
script_npi = s14.merge(npi_idv, left_on='npi',right_on='NPI')
#Checking to make sure the ones not in the joined df are actually only organizations
notjoined = npi_nj[npi_nj['NPI'].isin(list(s14[~s14.npi.isin(script_npi.NPI)]['npi']))]
len(notjoined[notjoined['Entity Type Code'].isin([1.0])])
    #1 = Indivduals, There were none
#Dropping unecessary column & the NPI column because it's repeated
script_npi.drop(['Entity Type Code','NPI','state_x','state_y'],axis=1,inplace=True)
#Cleaning the joined dataframe, removing essentially all punctuation & spaces from the first or last name
script_npi['ln_x'] = script_npi['ln_x'].map(lambda x: x.replace(' ',''))
script_npi['ln_y'] = script_npi['ln_y'].map(lambda x: x.replace(' ',''))
script_npi['fn_x'] = script_npi['fn_x'].map(lambda x: x.replace(' ',''))
script_npi['fn_y'] = script_npi['fn_y'].map(lambda x: x.replace(' ',''))
script_npi['mn'] = script_npi['mn'].map(lambda x: str(x).replace(' ',''))
script_npi['ln_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_x']]
script_npi['ln_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_y']]
script_npi['fn_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_x']]
script_npi['fn_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_y']]
script_npi['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['mn']]
script_npi['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['address1']]
#Cleaning the zip codes, NJ has a leading 0 in the zip so it might of been dropped
script_npi['zip'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['zip']]
script_npi['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in script_npi['zip']]

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
script_npi.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Making a column for the 5 digit zip
script_npi['zip5'] = script_npi['zip'].map(lambda x: x[:5])
"""Dealing with mismatched/mispelled names"""
#This just lets me see names where the first name & last name don't match up
script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) & (script_npi['fn_x']!=script_npi['fn_y'])]
#Making a new table of the mismatched names
mis_name = script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) | (script_npi['fn_x']!=script_npi['fn_y'])]
#Saving these as CSVs for future use
script_npi.to_csv('/Volumes/Seagate/Galvanize/nj_14_scrip_npi.csv')
mis_name.to_csv('/Volumes/Seagate/Galvanize/nj_14_multi_name_npi.csv')


"""Making 1 dictionary for each NPI & 1 dictionary for each Payment_ID
Keys = NPI or Payment ID
Values = Dictionary of:
    Keys: first name(fn), last name(ln), 5 digit zip(zip5), address(address1), Physician Specialty (specialty)
    Values: All the values that are listed in the NPI/Prescriptions or Payments data for that Key
        This is due to misspellings, extra info (Ex: Road instead of Rd), etc.
"""
#Clearing the the Payment ID dictionary
d = {}
#Applying the function to our payment_ids
payids.apply(payment_id,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(d, open('14paydict.pkl', 'wb'))

#Clearing the NPI dictioanry
n = {}
#Applying the function to our payment_ids
script_npi.apply(script_npi_dict,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(n, open('14npidict.pkl', 'wb'))
#Just renaming the 2 dictionaries from above
pay_id_14_dict = d
npi_14_dict = n

"""Combining the NPI & Payment_ID dictionaries to match them up"""
npi_pay_dict = {}
#Combining them
combine_npi_payid(pay_id_14_dict, npi_14_dict)
#Pickling it so I can utilize it with ease later
pickle.dump(npi_pay_dict, open('14_linked.pkl', 'wb'))



"""2015 DATA"""

"""Cleaning the Payments Data for joining & grabbing only the NJ data"""
#Loading csv
pay15 = pd.read_csv('/Volumes/Seagate/Galvanize/2015 Open Payments/OP_DTL_GNRL_PGYR2015_P01172018.csv', \
                    usecols=['Physician_Profile_ID','Physician_First_Name','Physician_Middle_Name', \
                             'Physician_Last_Name','Recipient_State','Total_Amount_of_Payment_USDollars', \
                            'Recipient_Primary_Business_Street_Address_Line1', 'Physician_Specialty', 'Recipient_Zip_Code'], \
                            dtype={'Recipient_Zip_Code':object})
#Grabbing only the NJ practioners
p15 = pay15[pay15['Recipient_State'].isin(['NJ'])]
"""Saving as a CSV for future use"""
p15.to_csv('/Volumes/Seagate/Galvanize/nj_payments_2015.csv')
#Renaming the columns so they're easier to call
l = p15.columns
p15.rename(columns={l[0]:'id',l[1]:'fn',l[2]:'mn',l[3]:'ln',l[4]:'address1',l[5]:'state',l[6]:'zip',l[-2]:'specialty',l[-1]:'amount'},inplace=True)
#Cleaning the first & last name (removing space & symbols) and the address (removing any symbols)
p15['ln'] = p15['ln'].map(lambda x: str(x).replace(' ',''))
p15['fn'] = p15['fn'].map(lambda x: str(x).replace(' ',''))
p15['mn'] = p15['mn'].map(lambda x: str(x).replace(' ',''))
p15['ln'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p15['ln']]
p15['fn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p15['fn']]
p15['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p15['mn']]
p15['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in p15['address1']]
#Cleaning the zip codes (removing dashes & making sure they are not missing the leading 0 that most NJ zip codes have)
p15['zip'] = [x.replace('-','') for x in p15['zip']]
p15['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in p15['zip']]
#Making a column for the 5 digit zip
p15['zip5'] = p15['zip'].map(lambda x: x[:5])

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
p15.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Groupby the ID so we can shrink our df
payids = p15.groupby(['id','fn','ln','mn','zip','specialty','address1']).count()['amount'].to_frame().reset_index(inplace=True)
#Dropping amount column because it's not necessary rn
payids.drop('amount',axis=1,inplace=True)
#Finding all the mispelled names/addresses/etc.
mis = payids[payids['id'].isin(payids['id'][payids['id'].duplicated()])].sort_values("id")
#Saving as a CSV for future use
payids.to_csv('/Volumes/Seagate/Galvanize/nj_15_payment_ids.csv')
mis.to_csv('/Volumes/Seagate/Galvanize/nj_15_multi_name_payment_ids.csv')


"""Cleaning the Prescriptions Data for joining & grabbing only the NJ data"""
#First I load only a small subset of the data to get an idea of the columns I'll need to use for joining
prescrip15 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2015.csv', nrows=100)
#This is so I can view all the columns since otherwise they get cut off
prescrip15[:1].to_dict('index')
#Then I pick only the columns I want & load the entire csv
scripts15 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2015.csv',usecols=list(pres15.columns[:6]))
#Grabbing only the NJ practioners
scripts15nj = scripts15[scripts15['nppes_provider_state'].isin(['NJ'])]
#Renaming the columns so they're easier to call
l = scripts15nj.columns
scripts15nj.rename(columns={l[0]:'npi',l[1]:'ln',l[2]:'fn',l[3]:'city',l[4]:'state',l[5]:'specialty'},inplace=True)
#Upper casing the first name, last name, and city
scripts15nj['ln'] = [x.upper() for x in scripts15nj['ln']]
scripts15nj['fn'] = [str(x).upper() for x in scripts15nj['fn']]
scripts15nj['city'] = [x.upper() for x in scripts15nj['city']]
"""Saving as a csv for future use"""
scripts15nj.to_csv('/Volumes/Seagate/Galvanize/2015_scriptsnj.csv')
#Grouping so I don't have a bunch of duplicate NPIs & I can look for mispellings
s15 = scripts15nj.groupby(['npi','ln','fn','city','specialty']).count()['state'].to_frame()
#Resetting the index becuase all my groupbys are now the index, which wont work for a merge
s15.reset_index(inplace=True)
#Checking if any of the people's names are misspelled
dup15 = s15[s15['npi'].isin(s15['npi'][s15['npi'].duplicated()])].sort_values("npi")
    #There were none
"""Combining with NPI df so I can remove all the organizations"""
#Joining the Scripts & NPI
"""Reasons for doing this:
    1. To get the Middle name of the individual
    2. To remove all organizations from the prescriptions data
    3. To get the address & zip of the individual
"""
script_npi = s15.merge(npi_idv, left_on='npi',right_on='NPI')
#Checking to make sure the ones not in the joined df are actually only organizations
notjoined = npi_nj[npi_nj['NPI'].isin(list(s15[~s15.npi.isin(script_npi.NPI)]['npi']))]
len(notjoined[notjoined['Entity Type Code'].isin([1.0])])
    #1 = Indivduals, There were none
#Dropping unecessary column & the NPI column because it's repeated
script_npi.drop(['Entity Type Code','NPI','state_x','state_y'],axis=1,inplace=True)
#Cleaning the joined dataframe, removing essentially all punctuation & spaces from the first or last name
script_npi['ln_x'] = script_npi['ln_x'].map(lambda x: x.replace(' ',''))
script_npi['ln_y'] = script_npi['ln_y'].map(lambda x: x.replace(' ',''))
script_npi['fn_x'] = script_npi['fn_x'].map(lambda x: x.replace(' ',''))
script_npi['fn_y'] = script_npi['fn_y'].map(lambda x: x.replace(' ',''))
script_npi['mn'] = script_npi['mn'].map(lambda x: str(x).replace(' ',''))
script_npi['ln_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_x']]
script_npi['ln_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['ln_y']]
script_npi['fn_x'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_x']]
script_npi['fn_y'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['fn_y']]
script_npi['mn'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['mn']]
script_npi['address1'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['address1']]
#Cleaning the zip codes, NJ has a leading 0 in the zip so it might of been dropped
script_npi['zip'] = [re.sub(r'[^\w\s]','',str(x).upper()) for x in script_npi['zip']]
script_npi['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in script_npi['zip']]

"""#Changing the NAN strings back to np.NaN (this happened while we were cleaning)
script_npi.replace('NAN', np.NaN,inplace=True)"""
#I dropped this rn

#Making a column for the 5 digit zip
script_npi['zip5'] = script_npi['zip'].map(lambda x: x[:5])
"""Dealing with mismatched/mispelled names"""
#This just lets me see names where the first name & last name don't match up
script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) & (script_npi['fn_x']!=script_npi['fn_y'])]
#Making a new table of the mismatched names
mis_name = script_npi.loc[(script_npi['ln_x']!=script_npi['ln_y']) | (script_npi['fn_x']!=script_npi['fn_y'])]
#Saving these as CSVs for future use
script_npi.to_csv('/Volumes/Seagate/Galvanize/nj_15_scrip_npi.csv')
mis_name.to_csv('/Volumes/Seagate/Galvanize/nj_15_multi_name_npi.csv')


"""Making 1 dictionary for each NPI & 1 dictionary for each Payment_ID
Keys = NPI or Payment ID
Values = Dictionary of:
    Keys: first name(fn), last name(ln), 5 digit zip(zip5), address(address1), Physician Specialty (specialty)
    Values: All the values that are listed in the NPI/Prescriptions or Payments data for that Key
        This is due to misspellings, extra info (Ex: Road instead of Rd), etc.
"""
#Clearing the the Payment ID dictionary
d = {}
#Applying the function to our payment_ids
payids.apply(payment_id,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(d, open('15paydict.pkl', 'wb'))

#Clearing the NPI dictioanry
n = {}
#Applying the function to our payment_ids
script_npi.apply(script_npi_dict,axis=1)
#Pickling it so I can utilize it with ease later
pickle.dump(n, open('15npidict.pkl', 'wb'))
#Just renaming the 2 dictionaries from above
pay_id_15_dict = d
npi_15_dict = n

"""Combining the NPI & Payment_ID dictionaries to match them up"""
npi_pay_dict = {}
#Combining them using the function i created
combine_npi_payid(pay_id_15_dict, npi_15_dict)
#Pickling it so I can utilize it with ease later
pickle.dump(npi_pay_dict, open('15_linked.pkl', 'wb'))


"""Master dictionary of all NPIs & Payment ID links for 2013-2015
Note, this does not include NPIs for individuals who are not apart
of the Prescriptions database from that year
Essentially if the indivudal didn't write a prescription for medicare for that year OR they didn't get a payment for that year = THEY ARE NOT INCLUDED"""
#Making a master dictionary
#Grabbing all the values that are in 2014, but NOT in 2013
dif_13_14 = {k:v for k,v in npi_pay_dict_14.items() if k not in npi_pay_dict_13}
#All the NPIs added between 14 & 13
npi_pay_dict_13_14 = {**npi_pay_dict_13, **dif_13_14}
#Grabbing all the values that are in 2015, but NOT in 2013 or 2014
dif_13_14_15 = {k:v for k,v in npi_pay_dict_15.items() if k not in npi_pay_dict_13_14}
npi_pay_dict_all = {**npi_pay_dict_13_14, **dif_13_14_15}
#Pickling so I can easily use it later
pickle.dump(npi_pay_dict_all, open('full_linked.pkl', 'wb'))
