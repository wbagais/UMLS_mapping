#!/usr/bin/env python
# coding: utf-8

# Steven Emrick - steve.emrick@nih.gov
# usage: python crosswalk.py -k <your-api-key>
# You can specify a specific UMLS version with the -v argument, but it is not required
# This reads a file with codes from the Human Phenotype Ontology and maps them to the US Edition of SNOMED CT through UMLS CUIs

# In[2]:


from __future__ import print_function
from Authentication import *
import requests
import json
import argparse
import collections
import sys
import os
import pandas as pd
import numpy as np
import timeit


# # Cleaning the data

# In[3]:


#read the source_data 
df = pd.read_csv("source_data.csv")


# In[4]:


df.head()


# In[5]:


df.dtypes


# ## add a decimal for diagnosis colomes after the 3rd digit 

# In[6]:


columns = ['diagnosis1','diagnosis2','diagnosis3','diagnosis4','diagnosis5']
for i in columns:
    df[i] = df[i].apply(lambda x: x if(x[0] == 'V' and len(x) < 4) 
                            else (x[:3] + '.' + x[3:] if (x[0] == 'V' and len(x) >= 4) 
                            else (x if (x[0].isalpha() and len(x) < 5) 
                            else (x[:4] + '.' + x[4:] if (x[0].isalpha() and len(x) >= 5) 
                            else (x if (x[0].isnumeric() and len(x) < 4) else (x[:3] + '.' + x[3:]))))))


# In[6]:


df.head()


# ## add a decimal for procedure colomes after the 2rd digit if the procedure length greater than 2

# In[7]:


columns = ["procedure1", "procedure2", "procedure3", "procedure4", "procedure5"]
for i in columns:
    df[i] = df[i].apply(lambda x: x[:2] + "." + x[2:] if len(x) > 2 else x)


# In[8]:


df.head()


# # creating ICD9 code dataframe

# In[9]:


ICD9_Code = []
columns = ['diagnosis1','diagnosis2','diagnosis3','diagnosis4','diagnosis5', 
           'procedure1','procedure2','procedure3','procedure4','procedure5']
for i in columns:
    ICD9_Code.append(df[i].tolist())


# In[10]:


Code = [item for sublist in ICD9_Code for item in sublist]


# In[11]:


x = np.array(Code) 
Code = np.unique(x) 


# In[12]:


ICD9_CUI_mapping = pd.DataFrame(Code, columns = ['ICD9_Code'])


# In[13]:


ICD9_CUI_mapping['ICD9_Code']


# # API connection Code

# In[18]:


apikey =  "b693c885-4a5f-4cb5-a58c-1c80f7d025ee"
version = "2019AB"
source = "ICD9CM"
serch_type = "exact"
base_uri = "https://uts-ws.nlm.nih.gov"


# In[19]:


#connect to the server (Authentication part)
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')

AuthClient = Authentication(apikey)
tgt = AuthClient.gettgt()


# In[20]:


def request_code(path, query):
    r = requests.get(base_uri + path, params=query)
    r.encoding = 'utf-8'
    #print(r.url + "\n")
    items = json.loads(r.text)
    return items


# There are 2 ways to have the CUIs in ICD9_CUI_mapping table:
# 
# Using list:
# - result: has the list of CUIs
# - then add this list to ICD9_CUI_mapping table
# 
# 
# Using set_value:
# - add the CUI into ICD9_CUI_mapping inside the for loop
# 

# In[27]:


start = timeit.default_timer()
result = []

for index, row in ICD9_CUI_mapping.iterrows():
    code = row['ICD9_Code']
    name_path =  "/rest/content/"+str(version)+"/source/"+str(source)+"/"+code
    name_query = query = {'ticket': AuthClient.getst(tgt)}
    
    #cui_query = {'string':string,'searchType':serch_type, 'ticket':AuthClient.getst(tgt)}
    cui_path = "/rest/search/current"
    
    print (index)
    try:
        #request data based on ICD9CM code
        results = request_code(name_path, name_query)
        #print the IDC9CM code
        print(code)
        #get the name of code
        string = results["result"]["name"]
        #print the name of the code
        print(string)
        cui_query = {'string':string,'searchType':serch_type, 
                     'ticket':AuthClient.getst(tgt)}

        #request the cui based on the name
        results = request_code(cui_path, cui_query)
        #get the cui from the result
        jsonData = results["result"]["results"][0]['ui']
        #print the cui
        print(jsonData)
        result.append(jsonData)
        
        ICD9_CUI_mapping.set_value(index, 'CUI', jsonData) 
        ICD9_CUI_mapping.set_value(index, 'name', string)
        
    
    except ValueError:
        result.append("No result")
        pass
    print("-------------------------------------------------------------------")
    
stop = timeit.default_timer()
print('Time: ', stop - start)


# In[28]:


ICD9_CUI_mapping


# Add column to the ICD9_CUI_mapping dataframe if you use the listing method

# In[ ]:


#ICD9_CUI_mapping['CUI'] = result


# Save dataframe into csv file

# In[ ]:


ICD9_CUI_mapping.to_csv('ICD9_CUI_mapping.csv')


# # Merging the 2 dataframes 

# In[38]:


mapping = pd.read_csv('ICD9_CUI_mapping.csv')


# In[39]:


mapping.head()


# In[40]:


mapping = mapping.drop(columns=['Unnamed: 0'])


# In[44]:


df_2 = df


# In[45]:


for i in ['diagnosis1','diagnosis2','diagnosis3','diagnosis4','diagnosis5', 'procedure1','procedure2','procedure3','procedure4','procedure5']:
    df_2=df_2.merge(mapping,
         left_on=i,
         right_on='ICD9_Code')
    cui = i+"_CUI"
    name = i+"_name"
    df_2 = df_2.rename(columns={"CUI":cui})
    df_2 = df_2.rename(columns={"name":name}) 
    df_2 = df_2.drop(columns=['ICD9_Code'])


# In[46]:


df_2.head()


# In[50]:


df_2 = df_2[["patient_id", "age","gender", "race", "admission_date",
             "diagnosis1","diagnosis1_CUI", "diagnosis1_name",
             "diagnosis2", "diagnosis2_CUI", "diagnosis2_name",
             "diagnosis3", "diagnosis3_CUI", "diagnosis3_name",
             "diagnosis4","diagnosis4_CUI", "diagnosis4_name",
             "diagnosis5", "diagnosis5_CUI", "diagnosis5_name",
             "hcpcs",
             "procedure1", "procedure1_CUI", "procedure1_name",
             "procedure2", "procedure2_CUI", "procedure2_name",
             "procedure3", "procedure3_CUI", "procedure3_name",
             "procedure4", "procedure4_CUI", "procedure4_name",
             "procedure5", "procedure5_CUI","procedure5_name"]]


# In[52]:


df_2.head()


# In[54]:


df_2.to_csv('FinalResult.csv',index=False)


# In[ ]:




