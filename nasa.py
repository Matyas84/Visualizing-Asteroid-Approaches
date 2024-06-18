import matplotlib.pyplot as plt

import requests
import json

import os
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup

import boto3
import datetime
from IPython.display import HTML, display
import datetime
import config
import time
#key: XwVHPFh2zHGkoQZ3QmLtDqyncNjhdloY07lr9868
key = "XwVHPFh2zHGkoQZ3QmLtDqyncNjhdloY07lr9868"


def request_nasa(start_date: str, end_date: str):
    request_url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={key}"
    try:
        r = requests.get(request_url)
        return r.json()
    except Exception as e:
        print(e)

def download_data(start_date, end_date):
    days_from_period = iterate_over_dates(start_date, end_date)
    raw = pd.DataFrame()
    for d in days_from_period[::7]:
        df1 = ((seven_days(d,days_from_period)))
        raw = pd.concat([raw, df1], ignore_index=True)
    return raw


def iterate_over_dates(start_date_str, end_date_str):
    try:
        # Convert start and end dates to datetime objects
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        
        date_strings = []
        
        # Iterate over each day between start and end dates
        while start_date <= end_date:
            date_strings.append(start_date.strftime("%Y-%m-%d"))
            
            
            start_date += datetime.timedelta(days=1)  # Increment the date by one day
            
        return date_strings
            
    except Exception as e:
        return str(e)


def find_date_after(days_after, input_date_str, date_list):
    if input_date_str not in date_list:
        return "Input date is not in the list."
    
    input_index = date_list.index(input_date_str)
    target_index = min(input_index + days_after, len(date_list) - 1)
    
    return date_list[target_index]


def iterate_dates(start_date_str, days_from_period):
    end_date_str = find_date_after(6,start_date_str,days_from_period)
    start_index = days_from_period.index(start_date_str)
    end_index = days_from_period.index(end_date_str)
    return days_from_period[start_index:end_index + 1]



def seven_days(start_d, days_from_period):
    end_date=(find_date_after(6,start_d,days_from_period))
    week = iterate_dates(start_d,days_from_period)
    raw1=pd.DataFrame()

    for day in week:
        neo_data = pd.DataFrame((request_nasa(start_d,end_date)["near_earth_objects"][day]))
        df = pd.DataFrame(neo_data)
        df.insert(1, 'date', day)
        raw1 = pd.concat([raw1, df], ignore_index=True)
    return(raw1)

