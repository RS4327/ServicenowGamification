import os
from pathlib import Path

import pandas as pd
import requests
from ServicenowGamification.Config.ConfigurationManager import *
from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Entity.Config_Entity import *

os.chdir(r"C:\Users\RSR\PYTHON\LLMIssueTracker\src")


class DataIngestion:
    def __init__(self,config:DataIngestionConfig):
        self.config=config
        
    def LoadIncidents(self):
        INSTANCE = self.config.source_url
        USERNAME = self.config.user_name
        PASSWORD = self.config.password
        # print("INSTANCE",INSTANCE)
        # print("USERNAME",USERNAME)
        # print("PASSWORD",PASSWORD)

        # INSTANCE = "https://dev394794.service-now.com"
        # USERNAME = "admin"
        # PASSWORD = "TyMdk!/WQa00"

        url = f"{INSTANCE}/api/now/table/incident"

        params = {
            "sysparm_limit": 100,
            "sysparm_display_value": "true"
        }

        response = requests.get(
            url,
            auth=(USERNAME, PASSWORD),
            headers={"Accept": "application/json"},
            params=params
        )

        response.raise_for_status()
        print(f"\n*-----------------------------Service Now Connection ----------------------------------------*\n")
        print("ServiceNow connection established successfully!")
        
        incidents = response.json()["result"]

        

        df = pd.json_normalize(incidents)
        print(type(incidents))
        print(type(df))
        local_path = self.config.local_data_file
        df.to_csv(local_path, index=False)
        print(f"\n*---------------------------- Data Frame Total Incidents ------------------------------------*\n")
        print("Data Frame : Total Incidents:", len(df))
        print(f"\n*-------------------------- Data Frame Total Columns or Features ----------------------------*\n")

        #print(f"Data Frame : Columns/Features Details: {df.columns.tolist()}")
        print(f"\n*-------------------------- Data Frame Share(Row,Clumns) ------------------------------------*\n")
        
        print(f"Data Frame Shape (Rows, Columns): {df.shape}")

        print(f"\n*------------------------------ Data Frame Sample Data -------------------------------------*\n")
        

        features = [

            "number",
            "short_description",
            "description",
            "state",
            "priority",
            "category",
            "assigned_to"]

        #print(df[features].head(2))

        #return df 