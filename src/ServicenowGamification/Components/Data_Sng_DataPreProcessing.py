import os 
import pandas as pd 

from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *

os.chdir(r"C:\Users\RSR\PYTHON\LLMIssueTracker\src")

class DataPreProcessing:
    def __init__(self,config:DataPreProcessingConfig):

        self.config=config

        create_directories([self.config.root_dir])

    def Datapreprocessing(self):
        df=pd.read_csv(self.config.data_path)
        #print(df.head(2))
        #print(df.shape)           
        features=[
            "number",
            "opened_at",
            "resolved_at",
            "closed_at",
            "priority",
            "state",
            "assigned_to",
            "assignment_group",
            "category",
            "subcategory",
            "short_description",
            "description",
            "sys_created_on",
            "sys_updated_on",
        ]
        dp=df[features]
        #print(dp.head(1))

        print(f"\n*----------------- Remove duplicates from Incident Data Frame -----------------*\n")
        print(f" Data Frame Shape before Remove duplicates {dp.shape}")
        dp=dp.drop_duplicates(subset=["number"])
        print(f" Data Frame Shape after Remove duplicatess {dp.shape}")

        print(f"\n*-------- Date Features: Convert to datetime from Incident Data Frame ---------*\n")
        # Convert to datetime
        dp["opened_at"] = pd.to_datetime(dp["opened_at"], errors="coerce")
        dp["resolved_at"] = pd.to_datetime(dp["resolved_at"], errors="coerce")
        dp["closed_at"] = pd.to_datetime(dp["closed_at"], errors="coerce")
        dp["sys_created_on"] = pd.to_datetime(dp["sys_created_on"], errors="coerce")
        dp["sys_updated_on"] = pd.to_datetime(dp["sys_updated_on"], errors="coerce")

        print(f"\n*-------------- Handle missing values from Incident Data Frame ----------------*\n")
        print(f"Checking Missing Values count for every object features  before Handle missing values ")
       
        object_columns = dp.select_dtypes(include=['object', 'string']).columns
        for column in object_columns:
            if dp[column].isnull().sum()>0:
                fill_values = {

                    "assigned_to": ["Venakt", "Vamsi", "Raju", "Ganesh", "Chaitanya"],
                    "assignment_group": ["Network", "Database", "Data", "QA", "Cloud"],
                    "category": ["Hardware", "Software", "Network", "Access", "Email"],
                    "subcategory": ["Laptop", "Application", "VPN", "Password", "Outlook"],

                    "description": [
                        "User reported an issue",
                        "Application not responding",
                        "Unable to login",
                        "System performance issue",
                        "Email issue reported"]
                    }

                for column in object_columns:
                    if dp[column].isnull().sum()>0:
                        print(f"   {column }- Missing count :{dp[column].isnull().sum()} ")

                
                for column, values in fill_values.items():
                    if column in object_columns:
                        missing_index = dp[dp[column].isna()].index

                        for i, idx in enumerate(missing_index):
                            dp.at[idx, column] = values[(i // 5) % len(values)]
                print(f"Checking Missing Values count for every object features  After Handle missing values ")
                if dp[column].isnull().sum()>0:
                    for column in object_columns:
                        if dp[column].isnull().sum()>0:
                            print(f"  {column }- Missing count :{dp[column].isnull().sum()} ")
                else :
                    print(f"No Missing values ")
        print(f"\nChecking Missing Values count for Date features before Handle missing values ")
        date_columns = dp.select_dtypes(include=['datetime64[ns]', 'datetimetz']).columns
        for column in date_columns:
            if dp[column].isnull().sum()>0:
                print(f"  {column }- Missing count :{dp[column].isnull().sum()} ")

        for dt_column in date_columns:

            if dt_column=='resolved_at':
                print(f"\n{dt_column}-Handle missing values based on opened_at ")    
                for idx in dp[dp["resolved_at"].isna()].index:
                    days = (idx % 5) + 1      # 1,2,3,4,5 days
                    dp.at[idx, "resolved_at"] = (
                        dp.at[idx, "opened_at"] + pd.Timedelta(days=days)
                    )
        for dt_column in date_columns:
                    if dt_column=='closed_at':
                        print(f"\n{dt_column}-Handle missing values based on closed_at ")     
                        for idx in dp[dp["closed_at"].isna()].index:
                            dp.at[idx, "closed_at"] = (
                                dp.at[idx, "resolved_at"] + pd.Timedelta(days=1)
                            )



        
            