________________________________________________________________________________

This was all wrong.

________________________________________________________________________________
"""Here I'm only grabbing the rows of doctors from NJ & saving these new tables as CSVs"""
#Reading only the columns we need from the NPI files
npi15 = pd.read_csv('/Volumes/Seagate/Galvanize/Medicare_Physician_and_Other_Supplier_National_Provider_Identifier__NPI__Aggregate_Report__Calendar_Year_2015.csv', \
                    usecols=np.arange(14), header=0, \
                    names=['NPI','ln','fn','mi','creds','gender','entity','address1','address2','city',
                            'zip','state','country','type'], \
                    dtype={'NPI':np.int64,'ln':object,'fn':object,'mi':object,'creds':object, \
                            'gender':object,'entity':object,'address1':object,'address2':object, \
                            'city':object,'zip':object,'state':object,'country':object,'type':object})
npi14 = pd.read_csv('/Volumes/Seagate/Galvanize/Medicare_Physician_and_Other_Supplier_National_Provider_Identifier__NPI__Aggregate_Report__Calendar_Year_2014.csv', \
                    usecols=np.arange(14), header=0, \
                    names=['NPI','ln','fn','mi','creds','gender','entity','address1','address2','city',
                            'zip','state','country','type'], \
                    dtype={'NPI':np.int64,'ln':object,'fn':object,'mi':object,'creds':object, \
                            'gender':object,'entity':object,'address1':object,'address2':object, \
                            'city':object,'zip':object,'state':object,'country':object,'type':object})
npi13 = pd.read_csv('/Volumes/Seagate/Galvanize/Medicare_Physician_and_Other_Supplier_National_Provider_Identifier__NPI__Aggregate_Report__Calendar_Year_2013.csv', \
                    usecols=np.arange(14), header=0, \
                    names=['NPI','ln','fn','mi','creds','gender','entity','address1','address2','city',
                            'zip','state','country','type'], \
                    dtype={'NPI':np.int64,'ln':object,'fn':object,'mi':object,'creds':object, \
                            'gender':object,'entity':object,'address1':object,'address2':object, \
                            'city':object,'zip':object,'state':object,'country':object,'type':object})
#Making a dataframe for each year of the NJ practioners & saving this as a CSV for each year for easier future access
npi15nj = npi15[npi15['state'].isin(['NJ'])]
npi15nj.to_csv('/Volumes/Seagate/Galvanize/nj_npi_2015.csv')

npi14nj = npi14[npi14['state'].isin(['NJ'])]
npi14nj.to_csv('/Volumes/Seagate/Galvanize/nj_npi_2014.csv')

npi13nj = npi13[npi13['state'].isin(['NJ'])]
npi13nj.to_csv('/Volumes/Seagate/Galvanize/nj_npi_2013.csv')

#Loading the supplemental file which contains info & a Unique classifer number for all practioners that recieved payments (Physician_Profile_ID which is different than NPI)
#The other columns contain information which is currently not relevant, will be revisited if there is enough time
sup = pd.read_csv('/Volumes/Seagate/Galvanize/Physician Supplement File for all Program Years/OP_PH_PRFL_SPLMTL_P01172018.csv',usecols=np.arange(17))
#Dropping this column because I will only be using New Jersey practioners currently
sup = sup.drop('Physician_Profile_Province_Name',axis=1)
#Renaming the columns so they are easier for me to utilize
sup.rename(columns={'Physician_Profile_ID':'id', 'Physician_Profile_First_Name':'fn',
       'Physician_Profile_Middle_Name':'mn', 'Physician_Profile_Last_Name':'ln',
       'Physician_Profile_Suffix':'suffix', 'Physician_Profile_Alternate_First_Name':'altfn',
       'Physician_Profile_Alternate_Middle_Name':'altmn',
       'Physician_Profile_Alternate_Last_Name':'altln',
       'Physician_Profile_Alternate_Suffix':'altsuffix',
       'Physician_Profile_Address_Line_1':'address1', 'Physician_Profile_Address_Line_2':'address2',
       'Physician_Profile_City':'city', 'Physician_Profile_State':'state',
       'Physician_Profile_Zipcode':'zip', 'Physician_Profile_Country_Name':'country',
       'Physician_Profile_Primary_Specialty':'type'},inplace=True)
#Getting only the NJ doctors
supnj = sup[sup['state'].isin(['NJ'])]
#Saving this as a CSV for easier future access
supnj.to_csv('/Volumes/Seagate/Galvanize/sup_nj.csv')


#Loading all npi data, the zip has to be read as an object otherwise the leading 0 gets cut
npi13nj = pd.read_csv('/Volumes/Seagate/Galvanize/nj_npi_2013.csv', dtype={'zip':object})
npi14nj = pd.read_csv('/Volumes/Seagate/Galvanize/nj_npi_2014.csv', dtype={'zip':object})
npi15nj = pd.read_csv('/Volumes/Seagate/Galvanize/nj_npi_2015.csv', dtype={'zip':object})
#Changing index so it's easier to work with
npi13nj = npi13nj.set_index('Unnamed: 0')
npi14nj = npi14nj.set_index('Unnamed: 0')
npi15nj = npi15nj.set_index('Unnamed: 0')
#Making a new df of all the NPI from 2015 + all the NPI from 2013 that ARE NOT in 2014 + all NPI from 2014 that ARE NOT in 2015
allnjnpi = npi15nj.append([npi13nj[~npi13nj.NPI.isin(npi14nj.NPI)], npi14nj[~npi14nj.NPI.isin(npi15nj.NPI)]])
#Renaming the index instead of 'Unnamed: 0'
allnjnpi.index.rename('index',inplace=True)
#Saving this as a CSV for easier future access
allnjnpi.to_csv('/Volumes/Seagate/Galvanize/all_nj_npi.csv')


#Loading the all npi nj data, the zip has to be read as an object otherwise the leading 0 gets cut
allnjnpi = pd.read_csv('/Volumes/Seagate/Galvanize/all_nj_npi.csv', dtype={'zip':object})
#Loading the Supplemental Data for NJ practioners
supnj = pd.read_csv('/Volumes/Seagate/Galvanize/sup_nj.csv')
#Removing the dash in between the zip & making it an integer to match our NPI zip
supnj['zip'] = supnj['zip'].map(lambda x: x.replace("-", ""))
#Dropping the old index
supnj = supnj.drop('Unnamed: 0', axis=1)




"Another NPI file/"
#Loading npi
npi = pd.read_csv('/Volumes/Seagate/Galvanize/NPPES_Data_Dissemination_May_2018/npidata_pfile_20050523-20180513.csv', \
                  usecols=['Entity Type Code','NPI','Provider Business Practice Location Address Postal Code', \
                           'Provider Middle Name','Provider First Line Business Practice Location Address', \
                           'Provider First Name','Provider Gender Code', 'Provider Last Name (Legal Name)','Provider Middle Name', \
                           'Provider Credential Text', 'Provider Business Practice Location Address State Name'])
#Getting only ones in NJ & ones that are just people (Entity Type Code = 1.0), not business NPIs
npinj = npi[npi['state'].isin(['NJ'])][npi[npi['state'].isin(['NJ'])]['Entity Type Code'].isin([1.0])]
#Renaming so its more useful for us
npinj.rename(columns={'Provider Last Name (Legal Name)':'ln',  \
                      'Provider First Name':'fn', 'Provider Middle Name':'mn', \
                      'Provider Credential Text':'cred', 'Provider First Line Business Practice Location Address':'address1', \
                      'Provider Business Practice Location Address State Name':'state', \
                      'Provider Business Practice Location Address Postal Code':'zip', \
                      'Provider Gender Code':'gender', 'Authorized Official Last Name':'oln', \
                      'Authorized Official First Name':'ofn', 'Authorized Official Middle Name':'omn'},inplace=True)
#I noticed that there was an replaced npi number, but for the one case of this in NJ it was the same number so I did not include it
#Dropping unecessary columns
npinj.drop(['Entity Type Code'],axis=1,inplace=True)
#Converting to string so we no longer lose our leading 0's
npinj['zip'] = npinj['zip'].astype('object')
#If the leading 0 is removed (len of 9 digit zip = 8, or if we have 4 digits for a 5 digit zip) add a 0 at the beginning, otherwise leave it
npinj['zip'] = [('0'+str(x)) if len(str(x))==8 or len(str(x))==4 else str(x) for x in npinj['zip']]
#Saving the df as a CSV for future use
npinj.to_csv('/Volumes/Seagate/Galvanize/nj_npi.csv')


#Reading the npinj CSV
npinj = pd.read_csv('/Volumes/Seagate/Galvanize/nj_npi.csv', dtype={'zip':object})
#Dropping the old index
npinj = npinj.drop('Unnamed: 0', axis=1)
