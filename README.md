# Drug Money

<h3><b>Introduction</b></h3>
Every year pharmaceutical and biological manufacturing companies spend upwards of $3 Billion in various forms of payments for healthcare professionals. Whether it be food, travel, gifts, or licensing fees each payment must be disclosed to the Centers of Medicare & Medicaid Services. In 2014, the government decided to make this information publicly available as a part of a dataset call Open Payments.

I wanted to dive in to not only see how these companies are paying doctors but also the effects that these payments may have. Utilizing other datasets also publicly available through the Centers of Medicare & Medicaid Services, I analyzed payments received by doctors along with the prescriptions written by them to see if any insight could be found. With **over 30 GB** in CSV files, I was able to find trends within certain specialties displaying statistically significant differences in the number of brand name prescriptions written by doctors receiving payments versus their colleagues who were not receiving payments.


<h3><b>Background</b></h3>
<em><h5>The Sunshine Act</h5></em>
</div>
<div>
<p class="text-primary">In 2013, the United States Centers for Medicare & Medicaid Services (CMS) introduced a new program that mandated pharmaceutical companies and manufacturers submit records of payments made to healthcare professionals. The CMS published this data under the Open Payments dataset to provide increased transparency regarding the types of financial relationships between the corporate healthcare industry and healthcare providers. It is important to note that this data is not meant to denote any sort of inappropriate or unlawful behavior. Yet, these relationships may influence the behavior of doctors potentially resulting in impaired patient care, compromised integrity, and increased healthcare costs.<br>With this knowledge at hand, I wanted to explore the potential impacts these payments may have on healthcare providers, specifically on the types of prescriptions they write.</p>
</div>
<div class="title">
<h3><b>Data</b></h3>
<em><h5>The Open Payments & Medicare Part D Provider Utilization & Payment datasets</h5></em>
</div>
<div>
<p class="text-primary"><b>Open Payments</b><br>
  When the Open Payments data was first released in 2013, only data for the months of August - December 2013 were gathered and released. Yet in subsequent years, full yearly data has been released. This data encompasses two main types of payments, those for research purposes and general payments for things such as travel, food/beverages, gifts, speaking fees, licensing fees, etc. Altogether, over 40 Million payment records have been released for the years of 2013 through 2016, totaling an amount of $25 Billion. From these 40 Million records I focused on the 38 Million general payments going directly healthcare providers rather than the 2.5 Million for research purposes. Beyond the number of payments, this dataset provided basic information regarding both the doctor receiving  and the company providing the payment, along with a classification for the type of payment, and details about form and nature of the payment.<br>

  <b>Medicare Part D Provider Utilization & Payments</b><br>
  In order to get a basis for the type of prescriptions doctors write, I utilized yearly Medicare Part D Prescription datasets which provided aggregate information about the prescriptions a doctor wrote for that year. This dataset outlined the amount and costs of each prescription written for and utilized by Medicare Part D participants along with basic information regarding the prescribing individual and drug itself. Altogether, these yearly datasets contained more than 100 Million aggregate records between the years of 2013 and 2016.
</p>
</div>
<div class="title">
<h3><b>Approach</b></h3>
<em><h5>Matching the payments providers received to the prescriptions they wrote</h5></em>
</div>
<div>
<p class="text-primary">
  Every single healthcare provider in the United States is given a unique National Provider Identifier (NPI) through the National Plan and Provider Enumeration System (NPPES), which is used to track them and their data, in this instance, over multiple datasets and situations. Practically all datasets about healthcare providers include this number and the Medicare Part D Prescriptions database is no different.<br>
  While the Open Payments data is reported by pharmaceutical companies utilizing providers' NPIs, <b>by law the government is prohibited from releasing NPIs in the Open Payments database.</b> Instead, a randomly generated unique payment ID is utilized to link providers within all Open Payments databases, but not outside of them. While NPIs are prohibited from being released, the government was able to release contact information for all providers in the database.<br>
  Utilizing a provider's first name, last name, specialty, and full address along with complementary information from the Medicare Prescriptions database I was able to successfully link Payments IDs and NPIs for practically all healthcare providers in the Open Payments database.<br>
  This linkage allowed me to work through the Prescriptions database to compare the mean brand-name prescribing rates of doctors who received and did not receive payments within the same specialty. Using an <b>unequal variances t-test</b> (Welch's t-test) on each group's mean I was able to find statistically significant results displaying that within certain specialties, doctors who receive payments from pharmaceutical companies write brand-name prescriptions at higher rates than their colleagues who do not receive payments. Furthermore, I was able to create an interactive search which allows users to search for their doctor and see a breakdown of the payments they have received as well as the type of prescriptions they received.
</p>
</div>
<div class="title">
<h3><b>Limitations</b></h3>
<em><h5>Correlation & Causation</h5></em>
</div>
<div>
<p class="text-primary">
  It is important to note that this analysis is not all-encompassing and has many limitations which could significantly alter it's results.<br>
  <ol>
    <li><b>Generic Alternatives</b><br>
      A factor that I was not able to account for was checking if there are any current generic alternatives for the <i>name brand</i> drug a doctor prescribed. This is important as doctors who have to prescribe their patients medications without any generic alternatives would naturally have higher brand name percentages compared to those with the choice to prescribe generic alternatives.
    </li>
    <li><b>Medicare Part D</b><br>
      The prescriptions data was drastically limited to only a small subset of the entire American population. Due to the fact that these prescriptions were mainly written for an older population and certain people with disabilities, it is very unlikely to be indicative of the prescriptions for the entire American population. I expect very different results if an analysis would have been done on a complete dataset for the entire American population, rather than just Medicare participants.
    </li>
    <li><b>NPI linkage</b><br>
      Due to the vast amount of data and my own time constraints I was unable to ensure every NPI had been linked to the proper healthcare provider in the Open Payments database. While I did not encounter any issues while processing and handling the data, there is a possibility that some values were mismatched, introducing some error into the analysis as well.<br>
      Furthermore, since my primary focus was the doctors who received payments as well as the doctors who wrote Medicare Part D prescriptions, I did not link the NPIs to doctors who did not appear in the Medicare Part D Prescriptions dataset for that year. Meaning, I was only looking at the doctors who were apart of the Medicare Part D dataset, not ones outside of it.
    </li>
    <li><b>Confounding Factors</b><br>
      There are numerous other factors that could possibly affect that percentage of brand-name prescriptions that a doctor writes, which I did not have access to here. Whether it be a doctor's patient base, location, drug recalls, etc., without more information it is hard to determine whether receiving payments has an effect on the number of brand-name drugs a doctor prescribes. <b style="color:crimson">My findings show a correlation between the two but do NOT imply causation.</b><br>
      </li>
      </ol>

  <h2>Findings</h2>
  <h4>
    <b>Basis</b>
  </h4>
  <p class="text-primary">In order to determine if there was a significant difference in the number of brand name prescriptions written by doctors who were paid and their colleagues who were not, I performed A/B testing on various specialties by utilizing <b>unequal variances t-tests</b> (Welch's t-tests). Due to the large number of t-tests that were being done, the probability of encountering a Type I error increases greatly. In order to reduce Type I error I utilized a Bonferroni correction where my significance level was divided by the number of tests being run, thereby increasing our threshold even further and limiting error.<br>Since there are many confounding factors that could come into play I took a couple of approaches in order to help eliminate as much error as I could.<br>
  <ol>
    <li>
      I only compared doctors within the same specialty. This was primarily due to the fact that the type of prescriptions a doctor in a specialty like Anesthesiology is going to be drastically different than the prescriptions a Pediatrician would write. This could cause disparities between the percentage of brand name prescriptions certain specialties wrote, due to availability for different drugs.
    </li>
    <li>
      I only performed t-tests on prescriptions and payments within the same year due to the fact that new drug releases, drug recalls, and copyright expirations could also drastically change the percentage of brand-name drugs prescribed.
    </li>
    <li>
      I only utilized specialties where the number of unique doctors who received and the number that did not receive payments were both greater than 30. This eliminated a number of the 100+ specialties I was testing. The primary reasoning behind this was that too small of a sample size in an already limited frame, would not be indicative of the population and results should not be viewed heavily. In addition, certain specialties such as Nurse Practitioners, Physician Assistants, etc. were not included in the Open Payments database since corporations were not required to release details regarding payments made to these specialties. I could not perform testing on these specialties since the positive class was 0.
    </li>
  </ol>

<h4>
  <b>Results</b>
</h4>
<p class="text-primary">Overall, my results were fairly common throughout, through all years there were only 3 specialties which displayed a significant difference in the mean percentage of brand name prescriptions written by paid doctors to those who weren't paid, even when they were compared for all years combined.<br>The specialties with a statistically significant difference were:
  <ol>
    <li>
      <b>Family Practice</b>
      <ul>
        <li>Non-paid Doctors mean brand name prescriptions: <b>12.8%</b></li>
        <li>Paid Doctors mean brand name prescriptions: <b>15.2%</b></li>
        <li>P-value: <b>9.41 x 10<sup>-6</sup></b></li>
      </ul>
    </li>
    <li>
      <b>Internal Medicine</b>
      <ul>
        <li>Non-paid Doctors mean brand name prescriptions: <b>14.8%</b></li>
        <li>Paid Doctors mean brand name prescriptions: <b>17.6%</b></li>
        <li>P-value: <b>2.77 x 10<sup>-4</sup></b></li>
      </ul>
    </li>
    <li>
      <b>Ophthalmology</b>
      <ul>
        <li>Non-paid Doctors mean brand name prescriptions: <b>41.4%</b></li>
        <li>Paid Doctors mean brand name prescriptions: <b>50.1%</b></li>
        <li>P-value: <b>1.43 x 10<sup>-8</sup></b></li>
      </ul>
    </li>
  </ol>
