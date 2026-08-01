import os 
import pandas as pd 

from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *

os.chdir(r"C:\Users\RSR\PYTHON\LLMIssueTracker\src")

class MetricsCalculation:
    def __init__(self,config:DataMetricsCalculationConfig):
        self.config=config
    def MTTR(self):
        df=pd.read_csv(self.config.data_path)
      
        print(f"\n*-------------- Calculate MTTR(Mean Time To Resolve) ----------------*\n")
        date_columns = ["opened_at", "resolved_at", "closed_at"]
    
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        print(df[date_columns].dtypes)    
            #Resolution Time = Resolved Time - Opened Time
            #df["resolution_time"] = (df["resolved_at"] - df["opened_at"])
        df["resolution_time"] = df["resolved_at"] - df["opened_at"]
            # Convert to hours:
            #df["resolution_hours"] = (df["resolution_time"].dt.total_seconds() / 3600)
            #df["resolution_hours"] = (df["resolution_time"].dt.total_seconds() / 3600)
        df["resolution_hours"] = ((df["resolved_at"] - df["opened_at"]).dt.total_seconds() / 3600)
           
        print(f"\n*--------------  overall MTTR (Mean Time To Resolve) ----------------*\n")
           # print(df[["number", "resolution_hours"]].head())
        mttr = df["resolution_hours"].mean()
        print("MTTR:", mttr)
    
        print(df[["number", "resolution_hours"]].head(2))   
        local_path=self.config.local_data_file
        #print(f"Preprocessed data saved to: {local_path}")
        df.to_csv(local_path, index=False)     
    
    


    