import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

#Writing a function to run a hypothesis test for each of the specialities, based on year (since over the years there could be some varaibility)
def ab_script_speciality(df,n):
    """
    Runs an A/B test on each of the specialities to see if there is a statistically significant difference in the mean % of brand name prescriptions written by doctors in that speciality recieving payments versus those in that speciality who did not recieve any payments
    Parameters
    -------------
        df : Dataframe
            Cleaned dataframe of payments (this should only be the payments for 1 year)
        n : Integer
            Threshold number; specialities where the amont of doctors recieving or not recieving payments is below this number will not be included
    Returns
    -------------
        Printsspecialities with a statistically significant difference in between the amount of brand name prescriptions written by doctors who recievied payments vs those who didn't
    """
    # Groupby to see the amount of doctors from that speciality who did & did not recieve payments
    grp = df.groupby(['specialty_description','recieved_payments'])['npi'].nunique().to_frame().reset_index()
    # I'm only going to look at the specialities where the number of doctors for this is above 30
    grp = grp[grp['npi']>=n]
    # Groupby function to only find the specialities who have > 30 docs both recieving & not recieving payments
    both = grp.groupby(['specialty_description'])['recieved_payments'].count().to_frame().reset_index()
    blist = list(both[both['recieved_payments']==2]['specialty_description'])
    # Making our list for our result
    l_spec = []
    # Using a for loop to go thorugh all the specialites that have more than 30 people reicieving & not recieiving payments to see if there's a significant difference in the means between them
    for spec in blist:
        spec_df = df[df['specialty_description']==spec].groupby(['npi','recieved_payments']).agg({'amount_brand':'sum','total_claim_count':'sum'}).reset_index()
        spec_df['%_brand'] = (spec_df['amount_brand']/spec_df['total_claim_count'])
        paid = spec_df[spec_df['recieved_payments']==True]
        notpaid = spec_df[spec_df['recieved_payments']==False]
        x, y = (ttest_ind(paid['%_brand'], notpaid['%_brand'], equal_var = False))
        # This is a 2 tailed t-test so we'll be looking at 1/2 of our p-value, also since we are running so many t-tests the probability of me encountering a Type I eroor increases greatly so I'm also going to use a Bonferroni correction (new_sig_level = sig_level(0.05)/# tests)
        if y <= (0.05/len(blist)/2) or y >= (1-(0.05/len(blist)/2)):
            print("{}: \n\tt-stat={}, pvalue={}\n\t{} paid, {} not paid".format(spec,x,y,len(paid),len(notpaid)))
    print("{} Specialities not tested for".format(len(list(set(df['specialty_description'].unique()) - set(blist)))))

#Loading the 2013 prescriptions data
s13 = pd.read_csv('/Volumes/Seagate/Galvanize/2013_scriptsnj.csv', dtype={'npi':object})
ab_script_speciality(s13,30)
"""
Dermatology:
	t-stat=3.501925811988889, pvalue=0.0005242821301110622
	262 paid, 101 not paid
Family Practice:
	t-stat=7.25842716397448, pvalue=7.061001172886413e-13
	927 paid, 719 not paid
Internal Medicine:
	t-stat=8.566627068969058, pvalue=1.9861614323018996e-17
	2034 paid, 1351 not paid
Neurology:
	t-stat=3.863386913506997, pvalue=0.00016712012461033476
	286 paid, 98 not paid
Obstetrics/Gynecology:
	t-stat=4.645070362039651, pvalue=4.6920241438591465e-06
	582 paid, 247 not paid
Ophthalmology:
	t-stat=6.277403601100644, pvalue=1.1175381702472372e-09
	375 paid, 187 not paid
71 Specialities not tested for
"""

#2014 data
s14 = pd.read_csv('/Volumes/Seagate/Galvanize/2014_scriptsnj.csv', dtype={'npi':object})
ab_script_speciality(s14,30)
"""
Family Practice:
	t-stat=6.746972374112551, pvalue=2.5761780668409462e-11
	1101 paid, 565 not paid
Internal Medicine:
	t-stat=7.360038290055856, pvalue=2.851290241576488e-13
	2356 paid, 1072 not paid
Ophthalmology:
	t-stat=6.674996232328711, pvalue=2.0693168054470714e-10
	416 paid, 144 not paid
74 Specialities not tested for
"""

#2015 data
s15 = pd.read_csv('/Volumes/Seagate/Galvanize/2015_scriptsnj.csv', dtype={'npi':object})
ab_script_speciality(s15,30)
"""
Family Practice:
	t-stat=6.240415326497377, pvalue=6.537694522526764e-10
	1121 paid, 572 not paid
Internal Medicine:
	t-stat=4.60545235172493, pvalue=4.436012627221055e-06
	2389 paid, 1086 not paid
Ophthalmology:
	t-stat=6.783029157756228, pvalue=9.990236238000692e-11
	426 paid, 147 not paid
77 Specialities not tested for
"""

#Doing it for all years now
scriptsnjfull = pd.read_csv('/Volumes/Seagate/Galvanize/nj_scripts_all_years.csv',dtype={'npi':object})
ab_script_speciality(scriptsnjfull,30)
"""
Cardiology:
	t-stat=3.618258804830928, pvalue=0.00034872277949164895
	859 paid, 221 not paid
Family Practice:
	t-stat=5.408722720841539, pvalue=7.263823618077773e-08
	1295 paid, 987 not paid
Internal Medicine:
	t-stat=3.9376890335941024, pvalue=8.401992097915463e-05
	2848 paid, 1987 not paid
Neurology:
	t-stat=3.716201284322369, pvalue=0.0002563360653319726
	361 paid, 149 not paid
Ophthalmology:
	t-stat=6.314671977786785, pvalue=6.534474929756905e-10
	474 paid, 254 not paid
75 Columns not tested for
"""
