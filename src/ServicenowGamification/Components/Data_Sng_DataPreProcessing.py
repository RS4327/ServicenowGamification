import os 
import pandas as pd 
import numpy as np
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *

os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")

class DataPreProcessing:
    def __init__(self,config:DataPreProcessingConfig):

        self.config=config

        #create_directories([self.config.root_dir])

    def Datapreprocessing(self,df):
        df=df
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
            "reassignment_count",
            "reopen_count",
        ]
        df=df[features]
        #print(df.head(1))

        print(f"\n*----------------- Remove duplicates from Incident Data Frame -----------------*\n")
        print(f" Data Frame Shape before Remove duplicates {df.shape}")
        df=df.drop_duplicates(subset=["number"])
        print(f" Data Frame Shape after Remove duplicatess {df.shape}")

        print(f"\n*-------- Date Features: Convert to datetime from Incident Data Frame ---------*\n")
        # Convert to datetime
        df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
        df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")
        df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")
        df["sys_created_on"] = pd.to_datetime(df["sys_created_on"], errors="coerce")
        df["sys_updated_on"] = pd.to_datetime(df["sys_updated_on"], errors="coerce")

        print(f"\n*-------------- Handle missing values from Incident Data Frame ----------------*\n")
        print(f"Checking Missing Values count for every object features  before Handle missing values ")
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        fill_values = {
             
            "assigned_to": ["Venkat", "Vamsi", "Raju", "Ganesh", "Chaitanya"],
            "assignment_group": ["Network", "Database", "Data", "QA", "Cloud"],
            "category": ["Hardware", "Software", "Network", "Access", "Email"],
            "subcategory": ["Laptop", "Application", "VPN", "Password", "Outlook"],
            "description": [
                "User reported an issue",
                "Application not responding",
                "Unable to login",
                "System performance issue",
                "Email issue reported"
            ]
        }

        print("Checking Missing Values Before Handling")

        for col in fill_values.keys():

            if col not in df.columns:
                continue

            print(f"{col} : {df[col].isna().sum()}")

            # Convert to object dtype
            df[col] = df[col].astype(object)

            missing_idx = df.index[df[col].isna()].tolist()

            for i, idx in enumerate(missing_idx):

                value = fill_values[col][(i // 5) % len(fill_values[col])]

                df.loc[idx, col] = value

        print("\nChecking Missing Values After Handling")

        for col in fill_values.keys():

            if col in df.columns:
                print(f"{col} : {df[col].isna().sum()}")



        
        print(f"\nChecking Missing Values count for Date features before Handle missing values ")
        date_columns = df.select_dtypes(include=['datetime64[ns]', 'datetimetz']).columns
        for column in date_columns:
            if df[column].isnull().sum()>0:
                print(f"  {column }- Missing count :{df[column].isnull().sum()} ")

        for dt_column in date_columns:

            if dt_column=='resolved_at':
                print(f"\n{dt_column}-Handle missing values based on opened_at ")    
                for idx in df[df["resolved_at"].isna()].index:
                    days = (idx % 5) + 1      # 1,2,3,4,5 days
                    df.at[idx, "resolved_at"] = (
                        df.at[idx, "opened_at"] + pd.Timedelta(days=days)
                    )
        for dt_column in date_columns:
                    if dt_column=='closed_at':
                        print(f"\n{dt_column}-Handle missing values based on closed_at ")     
                        for idx in df[df["closed_at"].isna()].index:
                            df.at[idx, "closed_at"] = (
                                df.at[idx, "resolved_at"] + pd.Timedelta(days=1)
                            )
        local_path=self.config.local_data_file
        print(f"Preprocessed data saved to: {local_path}")
        df.to_csv(local_path, index=False)
        return df



        
            