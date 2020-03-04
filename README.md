# UMLS_mapping
This project's purpose is to convert the ICD9CM code to CUI. 
Since there is no way to request the CUI using the IDC9CM, we do it in 2 steps.
First, get the name using the ICD9CM. Then use the name to get the CUI.

# This project has the following files: 
## Authentication.py	
The Authentication code is to generate a ticket number that we will use to connect to the API

## UMLS_assignment.py
Same as UMLS_assignment.ipynb	but in python code formate

## UMLS_assignment.ipynb	
The code does the following:
- Read the source file that contains the ICD9 codes (df)
- Clean the data by adding a decimal to ICD9 codes based on the rules in https://www.cms.gov/Medicare/Quality-Initiatives-Patient-Assessment-Instruments/HospitalQualityInits/Downloads/HospitalAppendix_F.pdf
- Put the unique ICD9 codes in a new table (ICD9_CUI_mapping)
- Connect to the API and get the name and CUI code. Also, add the name and CUI into ICD9_CUI_mapping table
- Save this table into ICD9_CUI_mapping.csv
- Merge the mapping and the original (ICD9_CUI_mapping & df)
- Save the result as CSV file (FinalResult.csv)

## source_data.csv
- The patient data with ICD9 codes

## ICD9_CUI_mapping.csv	
- A table contains the unique ICD9 codes with its name and CUI code

## FinalResult.csv
- The original file with CUI codes

