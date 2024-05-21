#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt

import requests
import json

import os
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup

import boto3

from IPython.display import HTML, display
import datetime


# In[2]:


nasa = requests.get("https://api.nasa.gov/neo/rest/v1/feed?start_date=2023-09-07&end_date=2023-09-08&api_key=XwVHPFh2zHGkoQZ3QmLtDqyncNjhdloY07lr9868")


# In[3]:


nasa.json()


# In[4]:


import datetime

def iterate_over_dates(start_date_str, end_date_str):
    try:
        # Convert start and end dates to datetime objects
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # Initialize an empty list to store date strings
        date_strings = []
        
        # Iterate over each day between start and end dates
        while start_date <= end_date:
            date_strings.append(start_date.strftime("%Y-%m-%d"))
            # Your processing code here
            # For example:
            # process_date(start_date)
            
            start_date += datetime.timedelta(days=1)  # Increment the date by one day
            
        return date_strings
            
    except Exception as e:
        return str(e)


# In[ ]:





# In[5]:


def request_nasa(start_date_str, end_date_str):
    template_url = "https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={key}"
    try:
        request_url = template_url.format(
            start_date=start_date_str,
            end_date=end_date_str,
            key="XwVHPFh2zHGkoQZ3QmLtDqyncNjhdloY07lr9868")
        r = requests.get(request_url)
        return r.json()
    except Exception as e:
        print(e)


# In[6]:


request_nasa("2023-08-25","2023-08-27")


# In[7]:


def request_nasa_one_day(date_str):
    template_url = "https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={key}"
    try:
        request_url = template_url.format(
            start_date=date_str,
            end_date=date_str,
            key="XwVHPFh2zHGkoQZ3QmLtDqyncNjhdloY07lr9868")
        r = requests.get(request_url)
        return r.json()
    except Exception as e:
        print(e)


# In[8]:


days_from_period = iterate_over_dates("2023-08-25","2023-09-27")


# In[9]:


days_from_period


# 

# In[10]:


raw = pd.DataFrame()
for day in days_from_period:
    neo_data = pd.DataFrame((request_nasa_one_day(day)["near_earth_objects"][day]))
    df = pd.DataFrame(neo_data)
    df.insert(1, 'date', day)
    raw = pd.concat([raw, df], ignore_index=True)


# In[11]:


raw


# In[12]:


raw.columns


# In[13]:


dia = raw["estimated_diameter"]
close = raw['close_approach_data']
close


# In[14]:


dia_list = dia.tolist()
dia_units_df = pd.json_normalize(dia_list)


# In[15]:


col_index_1 = raw.columns.get_loc("estimated_diameter")
left = raw.iloc[:, :col_index_1]
right = raw.iloc[:, col_index_1:]


# In[16]:


result_df = pd.concat([left, dia_units_df, right], axis=1)
result_df = result_df.drop('estimated_diameter', axis=1)
result_df


# In[17]:


close_df = pd.DataFrame([x[0] for x in close])
close_df
vel = close_df['relative_velocity']
vel_list = vel.tolist()
vel_units_df = pd.json_normalize(vel_list)
miss = close_df['miss_distance']
miss_list = miss.tolist()
miss_units_df = pd.json_normalize(miss_list)


# In[18]:


close_df = close_df.drop(['relative_velocity', 'miss_distance'], axis=1)
close_df


# In[19]:


col_index_close = result_df.columns.get_loc("close_approach_data")
result_df = result_df.drop('close_approach_data', axis=1)
left_close = result_df.iloc[:, :col_index_close]
right_close = result_df.iloc[:, col_index_close:]
final_df= pd.concat([left_close, close_df, vel_units_df, miss_units_df , right_close], axis=1)
final_df


# In[20]:


column_names_mapping = {'kilometers_per_second': 'relative_velocity_km/s', 'kilometers_per_hour': 'relative_velocity_km/h','miles_per_hour': 'relative_velocity_m/h',"astronomical": "miss_dist_astromnomical","lunar": "miss_dist_lunar","kilometers": "miss_dist_km","miles": "miss_dist_miles"}


# In[21]:


final_df = final_df.rename(columns=column_names_mapping)


# In[22]:


final_df.head().style


# In[23]:


final_df.columns


# In[24]:


final_df.to_csv('final_df.csv', index=False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




