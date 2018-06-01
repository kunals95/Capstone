import pandas as pd
import numpy as np
import re


"""2013 Prescriptions Cleaning"""

"""First I load a small subset of the data to get an idea of the columns I'll need"""
scripts13 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2013.csv', nrows=1)
scripts13.info()
#Grabbing only the columns I want
"""
npi
last name
first name
city
state
specialty
drug name
generic name
total claim count
total day supply
total drug cost
"""
cols = [0,1,2,3,4,5,7,8,10,12,13]
scripts13 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2013.csv', usecols=cols)
#Grabbing only the NJ docs
scriptsnj13 = scripts13[scripts13['nppes_provider_state']=='NJ']
#Loading in All Npis to remove organizations
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI','Provider Middle Name', \
                           'Provider First Name','Provider Last Name (Legal Name)'])
#Grabbing only the individuals from the npi database, so I can remove orgs from the dataframe
npi = npi[npi['Entity Type Code'].isin([1.0])]
scriptsnj13 = scriptsnj13.merge(npi, left_on='npi',right_on='NPI')
#Dropping the added columns from the NPI
scriptsnj13.drop(['NPI','Entity Type Code','Provider Last Name (Legal Name)','Provider First Name','Provider Middle Name'],axis=1,inplace=True)
scriptsnj13.to_csv('/Volumes/Seagate/Galvanize/2013_scriptsnj.csv',index=False)
#Cleaning up generic & drug names of symbols as this could cause mismatching of names (I'll replace symbols with a space)
scriptsnj13['drug_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj13['drug_name']]
scriptsnj13['generic_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj13['generic_name']]
#Removing some common extras from the names of our drugs since I want to compare name brand vs generic, not go into specifc drugs
"""
Ex:
HCl - this doesn't change the drug but simply is an additive for certain drugs to keep them in their pure form
the drug dissociates into it's pure form when dissolved into water, HCl is not an actual active ingrident of the drug
XL, ER, XR - Extended Release version of the drug, again this should not be considered a different drug than a generic for my purpose
PF - Preservatve free
HBR - Similar concept as HCl, actually going to write this one out because a lot of the generic includes it like this
"""
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
#I noticed some drug names & generic names weren't matching up due to the word 'with', even when a doc prescribed the generic
#Also removes exra spaces
scriptsnj13['drug_name'] = scriptsnj13['drug_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
scriptsnj13['generic_name'] = scriptsnj13['generic_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
#Some drug names that weren't match that I had to hard code in
#I used the same function that i wrote for cleaning the company name here, just changed it up
#Writing a function to clean company names
def clean_drug_name(df,wrong_name, right_name):
    """
    Input:
        df: df, dataframe to be used
        wrong_name: Str, wrong name that is listed in df
        right_name: Str, right name to be changed to
    Output:
        None
    """
    #Getting all the locations where it says the wrong name
    for col in ['drug_name','generic_name']:
        l = list(df[df[col]==wrong_name].index.values)
        for i in l:
            df.at[i,col] = right_name
#How I was looking for some mismatched names
scriptsnj13[scriptsnj13['drug_name']!=scriptsnj13['generic_name']].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})
#Making this a bit easier on myself & going through and looking at the columns where the drug names are in the generic name
#This basically lets me see where a shorthand is being used & is not being linked as a generic, even when it is
d1 = (scriptsnj13[([x[0] in x[1] for x in zip(scriptsnj13['drug_name'], scriptsnj13['generic_name'])])&(scriptsnj13['drug_name']!=scriptsnj13['generic_name'])].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d1.drop(list(d1[d1['drug_name']=='ERY'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DIGOX'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DILT'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='FROVA'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='TOPROL'].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d1['generic_name']),list(d1['drug_name'])):
    clean_drug_name(scriptsnj13,generic,drug)
#Doing the same for the opposite now
d2 = (scriptsnj13[([x[0] in x[1] for x in zip(scriptsnj13['generic_name'], \
                                              scriptsnj13['drug_name'])]) & \
                  (scriptsnj13['drug_name']!=scriptsnj13['generic_name'])].groupby(['generic_name','drug_name']). \
      agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d2.drop(list(d2[d2['generic_name']=='INSULIN SYRINGE'].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d2['generic_name']),list(d2['drug_name'])):
    clean_drug_name(scriptsnj13,generic,drug)
#Checking where I have swapped for generics names Ex: PROBENECID COLCHICINE != COLCHICINE PROBENECID
d3 = (scriptsnj13[([sorted(x[0].split(' ')) == sorted(x[1].split(' ')) for x in zip(scriptsnj13['generic_name'], \
                                                                    scriptsnj13['drug_name'])]) & \
                  (scriptsnj13['drug_name']!=scriptsnj13['generic_name'])]).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'count'}).reset_index()
#Dropping the columns where these are actually name brand drugs
for generic, drug in zip(list(d3['generic_name']),list(d3['drug_name'])):
    clean_drug_name(scriptsnj13,generic,drug)
#There's a special case where insulin syringe falls under 2 generic names (insulin syringe and syring w ndl ...)
(scriptsnj13[scriptsnj13['drug_name']=='INSULIN SYRINGE']).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'sum'})
#I'm just going to set all insulin syringe (drug) = insulin syringe (generic) becuase I only care about if the drug prescribed is a generic or not
#I don't care if it is a sep drug or not
for i in (scriptsnj13[scriptsnj13['drug_name']=='INSULIN SYRINGE']).index.values:
    scriptsnj13.at[i,'generic_name'] = 'INSULIN SYRINGE'

"""Hopefully this gives you an idea of how messy some data is :)"""

clean_drug_name(scriptsnj13,'DORZOLAMIDE TIMOLOL MALEAT','DORZOLAMIDE TIMOLOL')
clean_drug_name(scriptsnj13,'CEFUROXIME AXETIL','CEFUROXIME')
clean_drug_name(scriptsnj13,'CLOPIDOGREL BISULFATE','CLOPIDOGREL')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj13,'DEXTROSE 70 IN WATER','DEXTROSE IN WATER')
clean_drug_name(scriptsnj13,'DEXTROSE 5 IN WATER','DEXTROSE IN WATER')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj13,'SYRING W NDL DISP INSUL 0 3ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj13,'SYRING W NDL DISP INSUL,0 5ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj13,'SYRINGE NEEDLE INSULIN 1 ML', 'INSULIN SYRINGE')
clean_drug_name(scriptsnj13,'SYR W NDL INS 0 3 ML HALF MARK',"INSULIN SYRINGE")
#   NITROFURANTOIN MONO MACRO is also known as NITROFURANTOIN MONOHYD M CRYST, both are the same generic
clean_drug_name(scriptsnj13,'NITROFURANTOIN MONO MACRO','NITROFURANTOIN')
clean_drug_name(scriptsnj13,'NITROFURANTOIN MONOHYD M CRYST,','NITROFURANTOIN')
clean_drug_name(scriptsnj13,'NITROFURANTOIN MACROCRYSTAL','NITROFURANTOIN')
#   Generic that got cut off
clean_drug_name(scriptsnj13,'ACETIC ACID ALUMINUM','ACETIC ACID ALUMINUM ACETATE')
clean_drug_name(scriptsnj13,'ALCOHOL ANTISEPTIC PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'ALCOHOL PREP PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'ALCOHOL SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'ALCOHOL SWABS','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'ALCOHOL WIPES','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'SINGLE USE SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj13,'YF VAX','YELLOW FEVER VACCINE LIVE')
clean_drug_name(scriptsnj13,'0 9 SODIUM CHLORIDE','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj13,'SODIUM CHLORIDE 0 45','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj13,'ABACAVIR','ABACAVIR SULFATE')
clean_drug_name(scriptsnj13,'ABATACEPT MALTOSE','ABATACEPT')
clean_drug_name(scriptsnj13,'TYLENOL CODEINE NO 3','TYLENOL CODEINE')
clean_drug_name(scriptsnj13,'TYLENOL CODEINE NO 4','TYLENOL CODEINE')
clean_drug_name(scriptsnj13,'ACETIC ACID HYDROCORTISONE','HYDROCORTISONE ACETIC ACID')
clean_drug_name(scriptsnj13,'WATER FOR IRRIGATION STERILE','WATER')
clean_drug_name(scriptsnj13,'VERAPAMIL PM','VERAPAMIL')
clean_drug_name(scriptsnj13,'CHLORDIAZEPOXIDE AMITRIPTYLINE', 'AMITRIP CHLORDIAZEPOXIDE')
clean_drug_name(scriptsnj13,'AMOXICILLIN POTASSIUM CLAV','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj13,'AMOX TR POTASSIUM CLAVULANATE','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj13,'AMPICILLIN SODIUM SULBACTAM NA','AMPICILLIN SULBACTAM')
clean_drug_name(scriptsnj13,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj13,'AZACTAM ISO OSMOTIC DEXTROSE','AZTREONAM DEXTROSE WATER')
clean_drug_name(scriptsnj13,'BETAMETHASONEROPIONATE','BETAMETHASONE PROPYLENE GLYCOL')
clean_drug_name(scriptsnj13,'BUTALBITAL ACETAMINOPHEN CAFFE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj13,'BUTALB ACETAMINOPHEN CAFFEINE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj13,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj13,'BISOPROLOL HYDROCHLOROTHIAZIDE','BISOPROLOL FUMARATE HCTZ')
clean_drug_name(scriptsnj13,'BUTALB CAFF ACETAMINOPH CODEIN','BUTALBIT ACETAMIN CAFF CODEIN')
clean_drug_name(scriptsnj13,'CALCIUM FOLIC ACID PLUS D','CAL CARB MGOX D3 B12 FA B6 BOR')
clean_drug_name(scriptsnj13,'CIPROFLOXACIN LACTATE D5W','CIPROFLOXACIN D5W')
clean_drug_name(scriptsnj13,'CITALOPRAM HYDROBROMIDE','CITALOPRAM HBR')
clean_drug_name(scriptsnj13,'CLINDAMYCIN PHOS BENZOYL PEROX','CLINDAMYCIN BENZOYL PEROXIDE')
clean_drug_name(scriptsnj13,'CLOBETASOL EMULSION','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj13,'CLOBETASOL EMOLLIENT','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj13,'CODEINE BUTALBITAL ASA CAFFEIN','BUTALBITAL COMPOUND CODEINE')
clean_drug_name(scriptsnj13,'FOLIC ACID VIT B6 VIT B12','CYANOCOBALAMIN FA PYRIDOXINE')
clean_drug_name(scriptsnj13,'CYANOCOBALAMIN INJECTION','CYANOCOBALAMIN VITAMIN B 12')
clean_drug_name(scriptsnj13,'DESMOPRESSIN NONREFRIGERATED','DESMOPRESSIN ACETATE')
clean_drug_name(scriptsnj13,'DEXAMETHASONE SOD PHOSPHATE','DEXAMETHASONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj13,'AMPHETAMINE SALT COMBO','DEXTROAMPHETAMINE AMPHETAMINE')
clean_drug_name(scriptsnj13,'DEXTROSE 5 0 45 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj13,'DEXTROSE 5 AND 0 9 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj13,'FLUCONAZOLE IN SALINE','FLUCONAZOLE IN NACL ISO OSM')
clean_drug_name(scriptsnj13,'FLUOCINOLONE ACETONIDE','FLUOCINOLONE SHOWER CAP')
clean_drug_name(scriptsnj13,'GLUCAGON EMERGENCY KIT','GLUCAGON HUMAN RECOMBINANT')
clean_drug_name(scriptsnj13,'HALDOL DECANOATE 100','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj13,'HALDOL DECANOATE 50','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj13,'HYDROCODONE BT HOMATROPINE MBR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj13,'HYDROCODONE BIT HOMATROP ME BR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj13,'HYDROCODONE CHLORPHEN POLIS','HYDROCODONE CHLORPHENIRAMINE')
clean_drug_name(scriptsnj13,'HYDROCODONE BIT IBUPROFEN','HYDROCODONE IBUPROFEN')
clean_drug_name(scriptsnj13,'LIDOCAINE HYDROCORTISON','HYDROCORTISONE AC LIDOCAINE')
clean_drug_name(scriptsnj13,'L METHYLFOLATE CALCIUM','LEVOMEFOLATE CALCIUM')
clean_drug_name(scriptsnj13,'L METHYL B6 B12','METHYL B12 L MEFOLATE B6 PHOS')
clean_drug_name(scriptsnj13,'METHYLPHENIDATE LA','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj13,'METHYLPHENIDATE SR','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj13,'PEN NEEDLE','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj13,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj13,'NEOMYCIN POLYMYXIN HC','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj13,'NEOMYCIN POLYMYXIN HYDROCORT','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj13,'NEOMYCIN POLYMYXN B GRAMICIDIN','NEOMYCIN POLYMYXIN GRAMICIDIN')
clean_drug_name(scriptsnj13,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj13,'MULTIVITAMINS FLUORIDE','PEDI M VIT NO 17 FLUORIDE')
clean_drug_name(scriptsnj13,'PEG 3350 AND ELECTROLYTES','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj13,'PEG 3350 ELECTROLYTE','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj13,'PIPERACILLIN TAZOBACTAM','PIPERACILLIN SODIUM TAZOBACTAM')
clean_drug_name(scriptsnj13,'POLYMYXIN B SUL TRIMETHOPRIM','POLYMYXIN B SULF TRIMETHOPRIM')
clean_drug_name(scriptsnj13,'DEXTROSE 5 0 45 NACL KCL','POTASSIUM CHLORIDE D5 0 45NACL')
clean_drug_name(scriptsnj13,'PREDNISOLONE SOD PHOSPHATE','PREDNISOLONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj13,'PROMETHAZINE VC CODEINE','PROMETHAZINE PHENYLEPH CODEINE')
clean_drug_name(scriptsnj13,'SSD','SILVER SULFADIAZINE')
clean_drug_name(scriptsnj13,'PEG 3350','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj13,'PEG 3350 FLAVOR PACKS','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj13,'SF','SODIUM FLUORIDE')
clean_drug_name(scriptsnj13,'SF 5000 PLUS','SODIUM FLUORIDE')
clean_drug_name(scriptsnj13,'SPS','SODIUM POLYSTYRENE SULFONATE')
clean_drug_name(scriptsnj13,'SPIRONOLACTONE HCTZ','SPIRONOLACT HYDROCHLOROTHIAZID')
clean_drug_name(scriptsnj13,'TETANUSHTHERIA TOXOIDS','TETANUS HTHERIA TOX ADULT')
clean_drug_name(scriptsnj13,'TRIAMTERENE HCTZ','TRIAMTERENE HYDROCHLOROTHIAZID')

#Now that the data is cleaned ... Making a new column to see if the drug prescibed is a generic or brand name
scriptsnj13['brand_drug?'] = scriptsnj13['drug_name']!=scriptsnj13['generic_name']
#Making an amount of brand drugs column so we know how many brand drugs they wrote presciptions for
scriptsnj13['amount_brand'] = (scriptsnj13['total_claim_count']*scriptsnj13['brand_drug?'])
#Converted the drug cost from a string to a float
#Removing the dollar sign
scriptsnj13['total_drug_cost'] = scriptsnj13['total_drug_cost'].map(lambda x: x.replace('$', ''))
#Converting
scriptsnj13['total_drug_cost'] = scriptsnj13['total_drug_cost'].astype('float')
#Making a new column of the year
scriptsnj13['year'] = 2013
#Few doctors who's specialty desc was listed as unknown, I looked them up and found the correct specialty
#How I looked for unknowns
scriptsnj13['specialty_description'].unique()
scriptsnj13[scriptsnj13['specialty_description'].isin(['Unknown Supplier/Provider','Unknown Physician Specialty Code'])]['npi'].unique()
#Replacing, I replaced based on what it said on the NPI registry and specialites already in the df
for i in scriptsnj13[scriptsnj13['npi']=='1073774691'].index.values:
    scriptsnj13.at[i,'specialty_description'] = 'Sleep Medicine'
for i in scriptsnj13[scriptsnj13['npi']=='1881686376'].index.values:
    scriptsnj13.at[i,'specialty_description'] = 'Sleep Medicine'
for i in scriptsnj13[scriptsnj13['npi']=='1912966276'].index.values:
    scriptsnj13.at[i,'specialty_description'] = 'Cardiac Electrophysiology'
for i in scriptsnj13[scriptsnj13['npi']=='1497872824'].index.values:
    scriptsnj13.at[i,'specialty_description'] = 'Sports Medicine'
#Making a new column satting whether the doc received payments or not by searching for their npi in the payments df for that year
paymentsnj13 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2013_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':object,'company_id':object, \
                                  'payment_id':object,'record_id':object})
paid_docs = list(set(paymentsnj13.npi).intersection(set(scriptsnj13.npi)))
scriptsnj13['recieved_payments'] = scriptsnj13['npi'].isin(paid_docs)
#Saving the hardwork
scriptsnj13.to_csv('/Volumes/Seagate/Galvanize/2013_scriptsnj.csv',index=False)





"""2014 Prescriptions Cleaning"""

"""First I load a small subset of the data to get an idea of the columns I'll need"""
scripts14 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2014.csv', nrows=1)
scripts14.info()
#Grabbing only the columns I want
scripts14 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2014.csv', usecols=cols)
#Grabbing only the NJ docs
scriptsnj14 = scripts14[scripts14['nppes_provider_state']=='NJ']
#Loading in All Npis to remove organizations
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI','Provider Middle Name', \
                           'Provider First Name','Provider Last Name (Legal Name)'])
#Grabbing only the individuals from the npi database, so I can remove orgs from the dataframe
npi = npi[npi['Entity Type Code'].isin([1.0])]
scriptsnj14 = scriptsnj14.merge(npi, left_on='npi',right_on='NPI')
#Dropping the added columns from the NPI
scriptsnj14.drop(['NPI','Entity Type Code','Provider Last Name (Legal Name)','Provider First Name','Provider Middle Name'],axis=1,inplace=True)
scriptsnj14.to_csv('/Volumes/Seagate/Galvanize/2014_scriptsnj.csv',index=False)
#Cleaning up generic & drug names of symbols as this could cause mismatching of names (I'll replace symbols with a space)
scriptsnj14['drug_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj14['drug_name']]
scriptsnj14['generic_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj14['generic_name']]
#Removing some common extras from the names of our drugs since I want to compare name brand vs generic, not go into specifc drugs
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
#I noticed some drug names & generic names weren't matching up due to the word 'with', even when a doc prescribed the generic
#Also removes exra spaces
scriptsnj14['drug_name'] = scriptsnj14['drug_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
scriptsnj14['generic_name'] = scriptsnj14['generic_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
#Some drug names that weren't match that I had to hard code in
#I used the same functoin that I used for the 2013 data
#How I was looking for some mismatched names
scriptsnj14[scriptsnj14['drug_name']!=scriptsnj14['generic_name']].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})
#Making this a bit easier on myself & going through and looking at the columns where the drug names are in the generic name
#This basically lets me see where a shorthand is being used & is not being linked as a generic, even when it is
d1 = (scriptsnj14[([x[0] in x[1] for x in zip(scriptsnj14['drug_name'], scriptsnj14['generic_name'])])&(scriptsnj14['drug_name']!=scriptsnj14['generic_name'])].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d1.drop(list(d1[d1['drug_name']=='CIPRO'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DIGOX'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DILT'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='ERY'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='FROVA'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='TOPROL'].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d1['generic_name']),list(d1['drug_name'])):
    clean_drug_name(scriptsnj14,generic,drug)
#Doing the same for the opposite now
d2 = (scriptsnj14[([x[0] in x[1] for x in zip(scriptsnj14['generic_name'], \
                                              scriptsnj14['drug_name'])]) & \
                  (scriptsnj14['drug_name']!=scriptsnj14['generic_name'])].groupby(['generic_name','drug_name']). \
      agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d2.drop(list(d2[d2['generic_name']=='FIRST OMEPRAZOLE'].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d2['generic_name']),list(d2['drug_name'])):
    clean_drug_name(scriptsnj14,generic,drug)
#Checking where I have swapped for generics names Ex: PROBENECID COLCHICINE != COLCHICINE PROBENECID
d3 = (scriptsnj14[([sorted(x[0].split(' ')) == sorted(x[1].split(' ')) for x in zip(scriptsnj14['generic_name'], \
                                                                    scriptsnj14['drug_name'])]) & \
                  (scriptsnj14['drug_name']!=scriptsnj14['generic_name'])]).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'count'}).reset_index()
#Dropping the columns where these are actually name brand drugs
for generic, drug in zip(list(d3['generic_name']),list(d3['drug_name'])):
    clean_drug_name(scriptsnj14,generic,drug)
#There's a special case where insulin syringe falls under 2 generic names (insulin syringe and syring w ndl ...)
(scriptsnj14[scriptsnj14['drug_name']=='INSULIN SYRINGE']).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'sum'})
#I'm just going to set all insulin syringe (drug) = insulin syringe (generic) becuase I only care about if the drug prescribed is a generic or not
#I don't care if it is a sep drug or not
for i in (scriptsnj14[scriptsnj14['drug_name']=='INSULIN SYRINGE']).index.values:
    scriptsnj14.at[i,'generic_name'] = 'INSULIN SYRINGE'

"""Hopefully this gives you an idea of how messy some data is :)"""
#Same ones from 2013, just incase
clean_drug_name(scriptsnj14,'DORZOLAMIDE TIMOLOL MALEAT','DORZOLAMIDE TIMOLOL')
clean_drug_name(scriptsnj14,'CEFUROXIME AXETIL','CEFUROXIME')
clean_drug_name(scriptsnj14,'CLOPIDOGREL BISULFATE','CLOPIDOGREL')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj14,'DEXTROSE 70 IN WATER','DEXTROSE IN WATER')
clean_drug_name(scriptsnj14,'DEXTROSE 5 IN WATER','DEXTROSE IN WATER')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj14,'SYRING W NDL DISP INSUL 0 3ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj14,'SYRING W NDL DISP INSUL,0 5ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj14,'SYRINGE NEEDLE INSULIN 1 ML', 'INSULIN SYRINGE')
clean_drug_name(scriptsnj14,'SYR W NDL INS 0 3 ML HALF MARK',"INSULIN SYRINGE")
#   NITROFURANTOIN MONO MACRO is also known as NITROFURANTOIN MONOHYD M CRYST, both are the same generic
clean_drug_name(scriptsnj14,'NITROFURANTOIN MONO MACRO','NITROFURANTOIN')
clean_drug_name(scriptsnj14,'NITROFURANTOIN MONOHYD M CRYST,','NITROFURANTOIN')
clean_drug_name(scriptsnj14,'NITROFURANTOIN MACROCRYSTAL','NITROFURANTOIN')
#   Generic that got cut off
clean_drug_name(scriptsnj14,'ACETIC ACID ALUMINUM','ACETIC ACID ALUMINUM ACETATE')
clean_drug_name(scriptsnj14,'ALCOHOL ANTISEPTIC PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'ALCOHOL PREP PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'ALCOHOL SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'ALCOHOL SWABS','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'ALCOHOL WIPES','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'SINGLE USE SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj14,'YF VAX','YELLOW FEVER VACCINE LIVE')
clean_drug_name(scriptsnj14,'0 9 SODIUM CHLORIDE','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj14,'SODIUM CHLORIDE 0 45','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj14,'ABACAVIR','ABACAVIR SULFATE')
clean_drug_name(scriptsnj14,'ABATACEPT MALTOSE','ABATACEPT')
clean_drug_name(scriptsnj14,'TYLENOL CODEINE NO 3','TYLENOL CODEINE')
clean_drug_name(scriptsnj14,'TYLENOL CODEINE NO 4','TYLENOL CODEINE')
clean_drug_name(scriptsnj14,'ACETIC ACID HYDROCORTISONE','HYDROCORTISONE ACETIC ACID')
clean_drug_name(scriptsnj14,'WATER FOR IRRIGATION STERILE','WATER')
clean_drug_name(scriptsnj14,'VERAPAMIL PM','VERAPAMIL')
clean_drug_name(scriptsnj14,'CHLORDIAZEPOXIDE AMITRIPTYLINE', 'AMITRIP CHLORDIAZEPOXIDE')
clean_drug_name(scriptsnj14,'AMOXICILLIN POTASSIUM CLAV','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj14,'AMOX TR POTASSIUM CLAVULANATE','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj14,'AMPICILLIN SODIUM SULBACTAM NA','AMPICILLIN SULBACTAM')
clean_drug_name(scriptsnj14,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj14,'AZACTAM ISO OSMOTIC DEXTROSE','AZTREONAM DEXTROSE WATER')
clean_drug_name(scriptsnj14,'BETAMETHASONEROPIONATE','BETAMETHASONE PROPYLENE GLYCOL')
clean_drug_name(scriptsnj14,'BUTALBITAL ACETAMINOPHEN CAFFE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj14,'BUTALB ACETAMINOPHEN CAFFEINE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj14,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj14,'BISOPROLOL HYDROCHLOROTHIAZIDE','BISOPROLOL FUMARATE HCTZ')
clean_drug_name(scriptsnj14,'BUTALB CAFF ACETAMINOPH CODEIN','BUTALBIT ACETAMIN CAFF CODEIN')
clean_drug_name(scriptsnj14,'CALCIUM FOLIC ACID PLUS D','CAL CARB MGOX D3 B12 FA B6 BOR')
clean_drug_name(scriptsnj14,'CIPROFLOXACIN LACTATE D5W','CIPROFLOXACIN D5W')
clean_drug_name(scriptsnj14,'CITALOPRAM HYDROBROMIDE','CITALOPRAM HBR')
clean_drug_name(scriptsnj14,'CLINDAMYCIN PHOS BENZOYL PEROX','CLINDAMYCIN BENZOYL PEROXIDE')
clean_drug_name(scriptsnj14,'CLOBETASOL EMULSION','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj14,'CLOBETASOL EMOLLIENT','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj14,'CODEINE BUTALBITAL ASA CAFFEIN','BUTALBITAL COMPOUND CODEINE')
clean_drug_name(scriptsnj14,'FOLIC ACID VIT B6 VIT B12','CYANOCOBALAMIN FA PYRIDOXINE')
clean_drug_name(scriptsnj14,'CYANOCOBALAMIN INJECTION','CYANOCOBALAMIN VITAMIN B 12')
clean_drug_name(scriptsnj14,'DESMOPRESSIN NONREFRIGERATED','DESMOPRESSIN ACETATE')
clean_drug_name(scriptsnj14,'DEXAMETHASONE SOD PHOSPHATE','DEXAMETHASONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj14,'AMPHETAMINE SALT COMBO','DEXTROAMPHETAMINE AMPHETAMINE')
clean_drug_name(scriptsnj14,'DEXTROSE 5 0 45 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj14,'DEXTROSE 5 AND 0 9 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj14,'FLUCONAZOLE IN SALINE','FLUCONAZOLE IN NACL ISO OSM')
clean_drug_name(scriptsnj14,'FLUOCINOLONE ACETONIDE','FLUOCINOLONE SHOWER CAP')
clean_drug_name(scriptsnj14,'GLUCAGON EMERGENCY KIT','GLUCAGON HUMAN RECOMBINANT')
clean_drug_name(scriptsnj14,'HALDOL DECANOATE 100','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj14,'HALDOL DECANOATE 50','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj14,'HYDROCODONE BT HOMATROPINE MBR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj14,'HYDROCODONE BIT HOMATROP ME BR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj14,'HYDROCODONE CHLORPHEN POLIS','HYDROCODONE CHLORPHENIRAMINE')
clean_drug_name(scriptsnj14,'HYDROCODONE BIT IBUPROFEN','HYDROCODONE IBUPROFEN')
clean_drug_name(scriptsnj14,'LIDOCAINE HYDROCORTISON','HYDROCORTISONE AC LIDOCAINE')
clean_drug_name(scriptsnj14,'L METHYLFOLATE CALCIUM','LEVOMEFOLATE CALCIUM')
clean_drug_name(scriptsnj14,'L METHYL B6 B12','METHYL B12 L MEFOLATE B6 PHOS')
clean_drug_name(scriptsnj14,'METHYLPHENIDATE LA','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj14,'METHYLPHENIDATE SR','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj14,'PEN NEEDLE','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj14,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj14,'NEOMYCIN POLYMYXIN HC','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj14,'NEOMYCIN POLYMYXIN HYDROCORT','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj14,'NEOMYCIN POLYMYXN B GRAMICIDIN','NEOMYCIN POLYMYXIN GRAMICIDIN')
clean_drug_name(scriptsnj14,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj14,'MULTIVITAMINS FLUORIDE','PEDI M VIT NO 17 FLUORIDE')
clean_drug_name(scriptsnj14,'PEG 3350 AND ELECTROLYTES','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj14,'PEG 3350 ELECTROLYTE','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj14,'PIPERACILLIN TAZOBACTAM','PIPERACILLIN SODIUM TAZOBACTAM')
clean_drug_name(scriptsnj14,'POLYMYXIN B SUL TRIMETHOPRIM','POLYMYXIN B SULF TRIMETHOPRIM')
clean_drug_name(scriptsnj14,'DEXTROSE 5 0 45 NACL KCL','POTASSIUM CHLORIDE D5 0 45NACL')
clean_drug_name(scriptsnj14,'PREDNISOLONE SOD PHOSPHATE','PREDNISOLONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj14,'PROMETHAZINE VC CODEINE','PROMETHAZINE PHENYLEPH CODEINE')
clean_drug_name(scriptsnj14,'SSD','SILVER SULFADIAZINE')
clean_drug_name(scriptsnj14,'PEG 3350','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj14,'PEG 3350 FLAVOR PACKS','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj14,'SF','SODIUM FLUORIDE')
clean_drug_name(scriptsnj14,'SF 5000 PLUS','SODIUM FLUORIDE')
clean_drug_name(scriptsnj14,'SPS','SODIUM POLYSTYRENE SULFONATE')
clean_drug_name(scriptsnj14,'SPIRONOLACTONE HCTZ','SPIRONOLACT HYDROCHLOROTHIAZID')
clean_drug_name(scriptsnj14,'TETANUSHTHERIA TOXOIDS','TETANUS HTHERIA TOX ADULT')
clean_drug_name(scriptsnj14,'TRIAMTERENE HCTZ','TRIAMTERENE HYDROCHLOROTHIAZID')
#New ones from 2014
clean_drug_name(scriptsnj14,'RENAL CAPS','B COMPLEX C NO 20 FOLIC ACID')
clean_drug_name(scriptsnj14,'BETAMETHASONE PROPYLENE GLYCOL','BETAMETHASONE PROPYLENE GLYC')
clean_drug_name(scriptsnj14,'BUTALB ACETAMINOPH CAFF CODEIN','BUTALBIT ACETAMIN CAFF CODEINE')
clean_drug_name(scriptsnj14,'BUTALBIT ACETAMIN CAFF CODEIN','BUTALBIT ACETAMIN CAFF CODEINE')
clean_drug_name(scriptsnj14,'CHOLESTYRAMINE LIGHT','CHOLESTYRAMINE ASPARTAME')
clean_drug_name(scriptsnj14,'CARISOPRODOL COMPOUND CODEINE','CODEINE CARISOPRODOL ASPIRIN')
clean_drug_name(scriptsnj14,'DEXTROAMPHETAMINE AMPHETAMINE','DEXTROAMPHETAMINE AMPHET')
clean_drug_name(scriptsnj14,'DEXTROSE IN LACTATED RINGERS','DEXTROSE 5 LACTATED RINGERS')
clean_drug_name(scriptsnj14,'DEXTROSE 5 0 9 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj14,'DILTIAZEM 24HR','DILTIAZEM')
clean_drug_name(scriptsnj14,'DILTIAZEM 12HR','DILTIAZEM')
clean_drug_name(scriptsnj14,'DILTIAZEM 24HR CD','DILTIAZEM')
clean_drug_name(scriptsnj14,'DOBUTAMINE IN DEXTROSE','DOBUTAMINE D5W')
clean_drug_name(scriptsnj14,'DOXORUBICIN PEG LIPOSOMAL','DOXORUBICIN LIPOSOMAL')
clean_drug_name(scriptsnj14,'HYDROCODONE CHLORPHENIRAMNE','HYDROCODONE CHLORPHEN P STIREX')
clean_drug_name(scriptsnj14,'LANSOPRAZOL AMOXICIL CLARITHRO','LANSOPRAZOLE AMOXICILN CLARITH')
clean_drug_name(scriptsnj14,'MYCOPHENOLATE SODIUM','MYCOPHENOLIC ACID')
clean_drug_name(scriptsnj14,'INSULIN PEN NEEDLE','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj14,'NEOMYCIN POLYMYXIN DEXAMETH','NEO POLYMYX B SULF DEXAMETH')
clean_drug_name(scriptsnj14,'NEOMYCIN BACITRACIN POLY HC','NEOMY SULF BACITRAC ZN POLY HC')
clean_drug_name(scriptsnj14,'NITROFURANTOIN','NITROFURANTOIN MONOHYD M CRYST')
clean_drug_name(scriptsnj14,'MULTIVITAMIN FLUORIDE','PEDI M VIT NO 17 FLUORIDE')
clean_drug_name(scriptsnj14,'DEXTROSE 5 1 2NS KCL','POTASSIUM CHLORIDE D5 0 45NACL')
clean_drug_name(scriptsnj14,'LACTATED RINGERS','RINGERS SOLUTION LACTATED')
clean_drug_name(scriptsnj14,'VERAPAMIL SR','VERAPAMIL')

#Now that the data is cleaned ... Making a new column to see if the drug prescibed is a generic or brand name
scriptsnj14['brand_drug?'] = scriptsnj14['drug_name']!=scriptsnj14['generic_name']
#Making an amount of brand drugs column so we know how many brand drugs they wrote presciptions for
scriptsnj14['amount_brand'] = (scriptsnj14['total_claim_count']*scriptsnj14['brand_drug?'])
#The cost was already a float so I did not need to convert it for this one
#Making a new column of the year
scriptsnj14['year'] = 2014
#Few doctors who's specialty desc was listed as unknown, I looked them up and found the correct specialty
#How I looked for unknowns
scriptsnj14['specialty_description'].unique()
scriptsnj14[scriptsnj14['specialty_description'].isin(['Unknown Supplier/Provider','Unknown Physician Specialty Code'])]['npi'].unique()
#Replacing, I replaced based on what it said on the NPI registry and specialites already in the df
for i in scriptsnj14[scriptsnj14['npi']=='1528079654'].index.values:
    scriptsnj14.at[i,'specialty_description'] = 'Orthopaedic Surgery'
for i in scriptsnj14[scriptsnj14['npi']=='1497872824'].index.values:
    scriptsnj14.at[i,'specialty_description'] = 'Sports Medicine'
#Making a new column satting whether the doc received payments or not by searching for their npi in the payments df for that year
paymentsnj14 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2014_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':object,'company_id':object, \
                                  'payment_id':object,'record_id':object})
paid_docs = list(set(paymentsnj14.npi).intersection(set(scriptsnj14.npi)))
scriptsnj14['recieved_payments'] = scriptsnj14['npi'].isin(paid_docs)
#Saving the hardwork
scriptsnj14.to_csv('/Volumes/Seagate/Galvanize/2014_scriptsnj.csv',index=False)





"""2015 Prescriptions Cleaning"""

"""First I load a small subset of the data to get an idea of the columns I'll need"""
scripts15 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2015.csv', nrows=1)
scripts15.info()
#Grabbing only the columns I want
scripts15 = pd.read_csv('/Volumes/Seagate/Galvanize/Prescriptions 2015.csv', usecols=cols)
#Grabbing only the NJ docs
scriptsnj15 = scripts15[scripts15['nppes_provider_state']=='NJ']
#Loading in All Npis to remove organizations
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI','Provider Middle Name', \
                           'Provider First Name','Provider Last Name (Legal Name)'])
#Grabbing only the individuals from the npi database, so I can remove orgs from the dataframe
npi = npi[npi['Entity Type Code'].isin([1.0])]
scriptsnj15 = scriptsnj15.merge(npi, left_on='npi',right_on='NPI')
#Dropping the added columns from the NPI
scriptsnj15.drop(['NPI','Entity Type Code','Provider Last Name (Legal Name)','Provider First Name','Provider Middle Name'],axis=1,inplace=True)
scriptsnj15.to_csv('/Volumes/Seagate/Galvanize/2015_scriptsnj.csv',index=False)
#Cleaning up generic & drug names of symbols as this could cause mismatching of names (I'll replace symbols with a space)
scriptsnj15['drug_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj15['drug_name']]
scriptsnj15['generic_name'] = [re.sub(r'[^\w\s]',' ',str(x).upper()) for x in scriptsnj15['generic_name']]
#Removing some common extras from the names of our drugs since I want to compare name brand vs generic, not go into specifc drugs
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' HCL', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' XL', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' ER', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' DIP', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' PF', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' XR', ''))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: x.replace(' HBR', '  HYDROBROMIDE'))
#I noticed some drug names & generic names weren't matching up due to the word 'with', even when a doc prescribed the generic
#Also removes exra spaces
scriptsnj15['drug_name'] = scriptsnj15['drug_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
scriptsnj15['generic_name'] = scriptsnj15['generic_name'].map(lambda x: ' '.join(str(x).replace(' WITH','').split()))
#Some drug names that weren't match that I had to hard code in
#I used the same functoin that I used for the 2013 data
#How I was looking for some mismatched names
scriptsnj15[scriptsnj15['drug_name']!=scriptsnj15['generic_name']].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})
#Making this a bit easier on myself & going through and looking at the columns where the drug names are in the generic name
#This basically lets me see where a shorthand is being used & is not being linked as a generic, even when it is
d1 = (scriptsnj15[([x[0] in x[1] for x in zip(scriptsnj15['drug_name'], scriptsnj15['generic_name'])])&(scriptsnj15['drug_name']!=scriptsnj15['generic_name'])].groupby(['generic_name','drug_name']).agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d1.drop(list(d1[d1['drug_name']=='CIPRO'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DIGOX'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='DILT'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='ERY'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='FROVA'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='TOPROL'].index.values),inplace=True)
d1.drop(list(d1[d1['drug_name']=='URSO'].index.values),inplace=True)
d1.drop(list(d1[d1['generic_name']=='FENOFIBRATE MICRONIZED'].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d1['generic_name']),list(d1['drug_name'])):
    clean_drug_name(scriptsnj15,generic,drug)
#Doing the same for the opposite now
d2 = (scriptsnj15[([x[0] in x[1] for x in zip(scriptsnj15['generic_name'], \
                                              scriptsnj15['drug_name'])]) & \
                  (scriptsnj15['drug_name']!=scriptsnj15['generic_name'])].groupby(['generic_name','drug_name']). \
      agg({'total_claim_count':'count'})).reset_index()
#Dropping the columns where these are actually name brand drugs
d2.drop(list(d2[(d2['generic_name']=='PEN NEEDLE') & (d2['drug_name']!='PEN NEEDLES')].index.values),inplace=True)
#Using a for loop to go through & fix the names
for generic, drug in zip(list(d2['generic_name']),list(d2['drug_name'])):
    clean_drug_name(scriptsnj15,generic,drug)
#Checking where I have swapped for generics names Ex: PROBENECID COLCHICINE != COLCHICINE PROBENECID
d3 = (scriptsnj15[([sorted(x[0].split(' ')) == sorted(x[1].split(' ')) for x in zip(scriptsnj15['generic_name'], \
                                                                    scriptsnj15['drug_name'])]) & \
                  (scriptsnj15['drug_name']!=scriptsnj15['generic_name'])]).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'count'}).reset_index()
#Dropping the columns where these are actually name brand drugs
for generic, drug in zip(list(d3['generic_name']),list(d3['drug_name'])):
    clean_drug_name(scriptsnj15,generic,drug)
#There's a special case where insulin syringe falls under 2 generic names (insulin syringe and syring w ndl ...)
(scriptsnj15[scriptsnj15['drug_name']=='INSULIN SYRINGE']).groupby(['generic_name','drug_name']). \
agg({'total_claim_count':'sum'})
#I'm just going to set all insulin syringe (drug) = insulin syringe (generic) becuase I only care about if the drug prescribed is a generic or not
#I don't care if it is a sep drug or not
for i in (scriptsnj15[scriptsnj15['drug_name']=='INSULIN SYRINGE']).index.values:
    scriptsnj15.at[i,'generic_name'] = 'INSULIN SYRINGE'

"""Hopefully this gives you an idea of how messy some data is :)"""
#Same ones from 2013, just incase
clean_drug_name(scriptsnj15,'DORZOLAMIDE TIMOLOL MALEAT','DORZOLAMIDE TIMOLOL')
clean_drug_name(scriptsnj15,'CEFUROXIME AXETIL','CEFUROXIME')
clean_drug_name(scriptsnj15,'CLOPIDOGREL BISULFATE','CLOPIDOGREL')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj15,'DEXTROSE 70 IN WATER','DEXTROSE IN WATER')
clean_drug_name(scriptsnj15,'DEXTROSE 5 IN WATER','DEXTROSE IN WATER')
#   Still the same generic for my purposes of brand name v generic
clean_drug_name(scriptsnj15,'SYRING W NDL DISP INSUL 0 3ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj15,'SYRING W NDL DISP INSUL,0 5ML','INSULIN SYRINGE')
clean_drug_name(scriptsnj15,'SYRINGE NEEDLE INSULIN 1 ML', 'INSULIN SYRINGE')
clean_drug_name(scriptsnj15,'SYR W NDL INS 0 3 ML HALF MARK',"INSULIN SYRINGE")
#   NITROFURANTOIN MONO MACRO is also known as NITROFURANTOIN MONOHYD M CRYST, both are the same generic
clean_drug_name(scriptsnj15,'NITROFURANTOIN MONO MACRO','NITROFURANTOIN')
clean_drug_name(scriptsnj15,'NITROFURANTOIN MONOHYD M CRYST,','NITROFURANTOIN')
clean_drug_name(scriptsnj15,'NITROFURANTOIN MACROCRYSTAL','NITROFURANTOIN')
#   Generic that got cut off
clean_drug_name(scriptsnj15,'ACETIC ACID ALUMINUM','ACETIC ACID ALUMINUM ACETATE')
clean_drug_name(scriptsnj15,'ALCOHOL ANTISEPTIC PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'ALCOHOL PREP PADS','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'ALCOHOL SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'ALCOHOL SWABS','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'ALCOHOL WIPES','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'SINGLE USE SWAB','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'YF VAX','YELLOW FEVER VACCINE LIVE')
clean_drug_name(scriptsnj15,'0 9 SODIUM CHLORIDE','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj15,'SODIUM CHLORIDE 0 45','SODIUM CHLORIDE IRRIG SOLUTION')
clean_drug_name(scriptsnj15,'ABACAVIR','ABACAVIR SULFATE')
clean_drug_name(scriptsnj15,'ABATACEPT MALTOSE','ABATACEPT')
clean_drug_name(scriptsnj15,'TYLENOL CODEINE NO 3','TYLENOL CODEINE')
clean_drug_name(scriptsnj15,'TYLENOL CODEINE NO 4','TYLENOL CODEINE')
clean_drug_name(scriptsnj15,'ACETIC ACID HYDROCORTISONE','HYDROCORTISONE ACETIC ACID')
clean_drug_name(scriptsnj15,'WATER FOR IRRIGATION STERILE','WATER')
clean_drug_name(scriptsnj15,'VERAPAMIL PM','VERAPAMIL')
clean_drug_name(scriptsnj15,'CHLORDIAZEPOXIDE AMITRIPTYLINE', 'AMITRIP CHLORDIAZEPOXIDE')
clean_drug_name(scriptsnj15,'AMOXICILLIN POTASSIUM CLAV','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj15,'AMOX TR POTASSIUM CLAVULANATE','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj15,'AMPICILLIN SODIUM SULBACTAM NA','AMPICILLIN SULBACTAM')
clean_drug_name(scriptsnj15,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj15,'AZACTAM ISO OSMOTIC DEXTROSE','AZTREONAM DEXTROSE WATER')
clean_drug_name(scriptsnj15,'BETAMETHASONEROPIONATE','BETAMETHASONE PROPYLENE GLYCOL')
clean_drug_name(scriptsnj15,'BUTALBITAL ACETAMINOPHEN CAFFE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj15,'BUTALB ACETAMINOPHEN CAFFEINE','BUTALBITAL ACETAMINOPHEN CAFFEINE')
clean_drug_name(scriptsnj15,'ATROPINE CARE','ATROPINE SULFATE')
clean_drug_name(scriptsnj15,'BISOPROLOL HYDROCHLOROTHIAZIDE','BISOPROLOL FUMARATE HCTZ')
clean_drug_name(scriptsnj15,'BUTALB CAFF ACETAMINOPH CODEIN','BUTALBIT ACETAMIN CAFF CODEIN')
clean_drug_name(scriptsnj15,'CALCIUM FOLIC ACID PLUS D','CAL CARB MGOX D3 B12 FA B6 BOR')
clean_drug_name(scriptsnj15,'CIPROFLOXACIN LACTATE D5W','CIPROFLOXACIN D5W')
clean_drug_name(scriptsnj15,'CITALOPRAM HYDROBROMIDE','CITALOPRAM HBR')
clean_drug_name(scriptsnj15,'CLINDAMYCIN PHOS BENZOYL PEROX','CLINDAMYCIN BENZOYL PEROXIDE')
clean_drug_name(scriptsnj15,'CLOBETASOL EMULSION','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj15,'CLOBETASOL EMOLLIENT','CLOBETASOL PROPIONATE EMOLL')
clean_drug_name(scriptsnj15,'CODEINE BUTALBITAL ASA CAFFEIN','BUTALBITAL COMPOUND CODEINE')
clean_drug_name(scriptsnj15,'FOLIC ACID VIT B6 VIT B12','CYANOCOBALAMIN FA PYRIDOXINE')
clean_drug_name(scriptsnj15,'CYANOCOBALAMIN INJECTION','CYANOCOBALAMIN VITAMIN B 12')
clean_drug_name(scriptsnj15,'DESMOPRESSIN NONREFRIGERATED','DESMOPRESSIN ACETATE')
clean_drug_name(scriptsnj15,'DEXAMETHASONE SOD PHOSPHATE','DEXAMETHASONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj15,'AMPHETAMINE SALT COMBO','DEXTROAMPHETAMINE AMPHETAMINE')
clean_drug_name(scriptsnj15,'DEXTROSE 5 0 45 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj15,'DEXTROSE 5 AND 0 9 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj15,'FLUCONAZOLE IN SALINE','FLUCONAZOLE IN NACL ISO OSM')
clean_drug_name(scriptsnj15,'FLUOCINOLONE ACETONIDE','FLUOCINOLONE SHOWER CAP')
clean_drug_name(scriptsnj15,'GLUCAGON EMERGENCY KIT','GLUCAGON HUMAN RECOMBINANT')
clean_drug_name(scriptsnj15,'HALDOL DECANOATE 100','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj15,'HALDOL DECANOATE 50','HALOPERIDOL DECANOATE 100')
clean_drug_name(scriptsnj15,'HYDROCODONE BT HOMATROPINE MBR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj15,'HYDROCODONE BIT HOMATROP ME BR','HYDROCODONE HOMATROPINE MBR')
clean_drug_name(scriptsnj15,'HYDROCODONE CHLORPHEN POLIS','HYDROCODONE CHLORPHENIRAMINE')
clean_drug_name(scriptsnj15,'HYDROCODONE BIT IBUPROFEN','HYDROCODONE IBUPROFEN')
clean_drug_name(scriptsnj15,'LIDOCAINE HYDROCORTISON','HYDROCORTISONE AC LIDOCAINE')
clean_drug_name(scriptsnj15,'L METHYLFOLATE CALCIUM','LEVOMEFOLATE CALCIUM')
clean_drug_name(scriptsnj15,'L METHYL B6 B12','METHYL B12 L MEFOLATE B6 PHOS')
clean_drug_name(scriptsnj15,'METHYLPHENIDATE LA','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj15,'METHYLPHENIDATE SR','METHYLPHENIDATE CD')
clean_drug_name(scriptsnj15,'PEN NEEDLE','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj15,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj15,'NEOMYCIN POLYMYXIN HC','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj15,'NEOMYCIN POLYMYXIN HYDROCORT','NEOMYCIN POLYMYXIN B SULF HC')
clean_drug_name(scriptsnj15,'NEOMYCIN POLYMYXN B GRAMICIDIN','NEOMYCIN POLYMYXIN GRAMICIDIN')
clean_drug_name(scriptsnj15,'PEN NEEDLES','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj15,'MULTIVITAMINS FLUORIDE','PEDI M VIT NO 17 FLUORIDE')
clean_drug_name(scriptsnj15,'PEG 3350 AND ELECTROLYTES','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj15,'PEG 3350 ELECTROLYTE','PEG 3350 NA SULF BICARB CL KCL')
clean_drug_name(scriptsnj15,'PIPERACILLIN TAZOBACTAM','PIPERACILLIN SODIUM TAZOBACTAM')
clean_drug_name(scriptsnj15,'POLYMYXIN B SUL TRIMETHOPRIM','POLYMYXIN B SULF TRIMETHOPRIM')
clean_drug_name(scriptsnj15,'DEXTROSE 5 0 45 NACL KCL','POTASSIUM CHLORIDE D5 0 45NACL')
clean_drug_name(scriptsnj15,'PREDNISOLONE SOD PHOSPHATE','PREDNISOLONE SODIUM PHOSPHATE')
clean_drug_name(scriptsnj15,'PROMETHAZINE VC CODEINE','PROMETHAZINE PHENYLEPH CODEINE')
clean_drug_name(scriptsnj15,'SSD','SILVER SULFADIAZINE')
clean_drug_name(scriptsnj15,'PEG 3350','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj15,'PEG 3350 FLAVOR PACKS','SODIUM CHLORIDE NAHCO3 KCL PEG')
clean_drug_name(scriptsnj15,'SF','SODIUM FLUORIDE')
clean_drug_name(scriptsnj15,'SF 5000 PLUS','SODIUM FLUORIDE')
clean_drug_name(scriptsnj15,'SPS','SODIUM POLYSTYRENE SULFONATE')
clean_drug_name(scriptsnj15,'SPIRONOLACTONE HCTZ','SPIRONOLACT HYDROCHLOROTHIAZID')
clean_drug_name(scriptsnj15,'TETANUSHTHERIA TOXOIDS','TETANUS HTHERIA TOX ADULT')
clean_drug_name(scriptsnj15,'TRIAMTERENE HCTZ','TRIAMTERENE HYDROCHLOROTHIAZID')
#New ones from 2014
clean_drug_name(scriptsnj15,'RENAL CAPS','B COMPLEX C NO 20 FOLIC ACID')
clean_drug_name(scriptsnj15,'BETAMETHASONE PROPYLENE GLYCOL','BETAMETHASONE PROPYLENE GLYC')
clean_drug_name(scriptsnj15,'BUTALB ACETAMINOPH CAFF CODEIN','BUTALBIT ACETAMIN CAFF CODEINE')
clean_drug_name(scriptsnj15,'BUTALBIT ACETAMIN CAFF CODEIN','BUTALBIT ACETAMIN CAFF CODEINE')
clean_drug_name(scriptsnj15,'CHOLESTYRAMINE LIGHT','CHOLESTYRAMINE ASPARTAME')
clean_drug_name(scriptsnj15,'CARISOPRODOL COMPOUND CODEINE','CODEINE CARISOPRODOL ASPIRIN')
clean_drug_name(scriptsnj15,'DEXTROAMPHETAMINE AMPHETAMINE','DEXTROAMPHETAMINE AMPHET')
clean_drug_name(scriptsnj15,'DEXTROSE IN LACTATED RINGERS','DEXTROSE 5 LACTATED RINGERS')
clean_drug_name(scriptsnj15,'DEXTROSE 5 0 9 NACL','DEXTROSE SODIUM CHLORIDE')
clean_drug_name(scriptsnj15,'DILTIAZEM 24HR','DILTIAZEM')
clean_drug_name(scriptsnj15,'DILTIAZEM 12HR','DILTIAZEM')
clean_drug_name(scriptsnj15,'DILTIAZEM 24HR CD','DILTIAZEM')
clean_drug_name(scriptsnj15,'DOBUTAMINE IN DEXTROSE','DOBUTAMINE D5W')
clean_drug_name(scriptsnj15,'DOXORUBICIN PEG LIPOSOMAL','DOXORUBICIN LIPOSOMAL')
clean_drug_name(scriptsnj15,'HYDROCODONE CHLORPHENIRAMNE','HYDROCODONE CHLORPHEN P STIREX')
clean_drug_name(scriptsnj15,'LANSOPRAZOL AMOXICIL CLARITHRO','LANSOPRAZOLE AMOXICILN CLARITH')
clean_drug_name(scriptsnj15,'MYCOPHENOLATE SODIUM','MYCOPHENOLIC ACID')
clean_drug_name(scriptsnj15,'INSULIN PEN NEEDLE','NEEDLES INSULIN DISPOSABLE')
clean_drug_name(scriptsnj15,'NEOMYCIN POLYMYXIN DEXAMETH','NEO POLYMYX B SULF DEXAMETH')
clean_drug_name(scriptsnj15,'NEOMYCIN BACITRACIN POLY HC','NEOMY SULF BACITRAC ZN POLY HC')
clean_drug_name(scriptsnj15,'NITROFURANTOIN','NITROFURANTOIN MONOHYD M CRYST')
clean_drug_name(scriptsnj15,'MULTIVITAMIN FLUORIDE','PEDI M VIT NO 17 FLUORIDE')
clean_drug_name(scriptsnj15,'DEXTROSE 5 1 2NS KCL','POTASSIUM CHLORIDE D5 0 45NACL')
clean_drug_name(scriptsnj15,'LACTATED RINGERS','RINGERS SOLUTION LACTATED')
clean_drug_name(scriptsnj15,'VERAPAMIL SR','VERAPAMIL')
#New ones form 2015
clean_drug_name(scriptsnj15,'ALCOHOL PREP SWABS','ALCOHOL PADS')
clean_drug_name(scriptsnj15,'AMLODIPINE VALSARTAN HCTZ','AMLODIPINE VALSARTAN HCTHIAZID')
clean_drug_name(scriptsnj15,'AMOXICILLIN CLAVULANATE POT','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj15,'AMOXICILLIN CLAVULANATE POTASS','AMOXICILLIN CLAVULANATE')
clean_drug_name(scriptsnj15,'DOXYCYCLINE IR DR','DOXYCYCLINE MONOHYDRATE')
clean_drug_name(scriptsnj15,'FLUCONAZOLE IN NACL ISO OSM','FLUCONAZOLE NACL')
clean_drug_name(scriptsnj15,'GENTAMICIN SULFATE IN NS','GENTAMICIN IN NACL ISO OSM')
clean_drug_name(scriptsnj15,'LEVONORGESTREL ETH ESTRADIOL','LEVONORGESTREL ETHIN ESTRADIOL')
clean_drug_name(scriptsnj15,'MILRINONE IN 5 DEXTROSE','MILRINONE LACTATE D5W')
clean_drug_name(scriptsnj15,'NORETHINDRON ETHINYL ESTRADIOL','NORETHINDRON AC ETH ESTRADIOL')
clean_drug_name(scriptsnj15,'K EFFERVESCENT','POTASSIUM BICARBONATE CIT AC')

#Now that the data is cleaned ... Making a new column to see if the drug prescibed is a generic or brand name
scriptsnj15['brand_drug?'] = scriptsnj15['drug_name']!=scriptsnj15['generic_name']
#Making an amount of brand drugs column so we know how many brand drugs they wrote presciptions for
scriptsnj15['amount_brand'] = (scriptsnj15['total_claim_count']*scriptsnj15['brand_drug?'])
#Converted the drug cost from a string to a float
#Removing the dollar sign
scriptsnj15['total_drug_cost'] = scriptsnj15['total_drug_cost'].map(lambda x: x.replace('$', ''))
#Converting
scriptsnj15['total_drug_cost'] = scriptsnj15['total_drug_cost'].astype('float')
#Making a new column of the year
scriptsnj15['year'] = 2015
#Few doctors who's specialty desc was listed as unknown, I looked them up and found the correct specialty
#How I looked for unknowns
scriptsnj15['specialty_description'].unique()
scriptsnj15[scriptsnj15['specialty_description'].isin(['Unknown Supplier/Provider','Unknown Physician Specialty Code'])]['npi'].unique()
#Replacing, I replaced based on what it said on the NPI registry and specialites already in the df
for i in scriptsnj15[scriptsnj15['npi']=='1164606034'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Sports Medicine'
for i in scriptsnj15[scriptsnj15['npi']=='1497722060'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Interventional Cardiology'
for i in scriptsnj15[scriptsnj15['npi']=='1043219876'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Specialist'
for i in scriptsnj15[scriptsnj15['npi']=='1528079654'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Orthopaedic Surgery'
for i in scriptsnj15[scriptsnj15['npi']=='1659382604'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Interventional Cardiology'
for i in scriptsnj15[scriptsnj15['npi']=='1699927566'].index.values:
    scriptsnj15.at[i,'specialty_description'] = 'Surgical Oncology'
#Making a new column satting whether the doc received payments or not by searching for their npi in the payments df for that year
paymentsnj15 = pd.read_csv('/Volumes/Seagate/Galvanize/nj_payments_2015_consl.csv',
                            dtype={'zip':object,'name_d1':object,'name_d5':object,'ndc_d1':object,'ndc_d2':object, \
                                   'ndc_d3':object, 'ndc_d4':object,'ndc_d5':object, 'npi':object,'company_id':object, \
                                  'payment_id':object,'record_id':object})
paid_docs = list(set(paymentsnj15.npi).intersection(set(scriptsnj15.npi)))
scriptsnj15['recieved_payments'] = scriptsnj15['npi'].isin(paid_docs)
#Saving the hardwork
scriptsnj15.to_csv('/Volumes/Seagate/Galvanize/2015_scriptsnj.csv',index=False)

#Joining all the years into 1 df
scriptsnjfull = pd.concat([scriptsnj13,scriptsnj14,scriptsnj15])
#Cleaning up how I want the columns arranged
scriptsnjfull = scriptsnjfull[scriptsnjfull.columns.tolist()[:6]+scriptsnjfull.columns.tolist()[-3:-2]+ \
                            scriptsnjfull.columns.tolist()[-1:] + scriptsnjfull.columns.tolist()[8:9] + \
                            scriptsnjfull.columns.tolist()[-2:-1] + scriptsnjfull.columns.tolist()[6:7] + \
                            scriptsnjfull.columns.tolist()[7:8] + scriptsnjfull.columns.tolist()[-4:-3] + \
                            scriptsnjfull.columns.tolist()[9:-4]]
#Saving this as a CSV for future use
scriptsnjfull.to_csv('/Volumes/Seagate/Galvanize/nj_scripts_all_years.csv',index=False)
