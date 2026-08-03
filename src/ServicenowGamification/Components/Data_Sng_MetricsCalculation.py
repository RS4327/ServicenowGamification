import os 
import pandas as pd 
import numpy as np
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *

os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")

class MetricsCalculation:
    def __init__(self,config:DataMetricsCalculationConfig):
        self.config=config
        self.params = Read_Yaml(PARAMS_FILE_PATH)
    def MTTR(self,df):
        if df is None:
            df = pd.read_csv(self.config.data_path)
            
      
        #print(f"\n*-------------- Calculate MTTR(Mean Time To Resolve) ----------------*\n")
        date_columns = ["opened_at", "resolved_at", "closed_at"]
    
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        #print(df[date_columns].dtypes)    
            #Resolution Time = Resolved Time - Opened Time
            #df["resolution_time"] = (df["resolved_at"] - df["opened_at"])
        df["resolution_time"] = df["resolved_at"] - df["opened_at"]
            # Convert to hours:
            #df["resolution_hours"] = (df["resolution_time"].dt.total_seconds() / 3600)
            #df["resolution_hours"] = (df["resolution_time"].dt.total_seconds() / 3600)
        df["resolution_hours"] = ((df["resolved_at"] - df["opened_at"]).dt.total_seconds() / 3600)
           
        #print(f"\n*--------------  overall MTTR (Mean Time To Resolve) ----------------*\n")
           # print(df[["number", "resolution_hours"]].head())
        mttr = df["resolution_hours"].mean()
        #print("MTTR:", mttr)
    
       
        return df    

    def calculate_art(self,df):
        """
        Average Resolution Time grouped by assignment group.
        """
        df=df
        art = (

            df

            .groupby("assignment_group")["resolution_hours"]

            .mean()

            .round(2)

            .reset_index()

            .rename(
                columns={
                    "resolution_hours": "average_resolution_time"
                }
            )

        )

        print("\nAverage Resolution Time")

        print(art)

        return df,art


    def calculate_sla(self, df):
        df=df
        def get_status(row):
            priority = str(row["priority"])
                    #print(f"priority {priority}")
        
            if priority == "1 - Critical":
                return "Met" if row["resolution_hours"] <= self.params.sla.priority_1 else "Breached"
        
            elif priority == "2 - High":
                return "Met" if row["resolution_hours"] <= self.params.sla.priority_2 else "Breached"
        
            elif priority == "3 - Moderate":
                return "Met" if row["resolution_hours"] <= self.params.sla.priority_3 else "Breached"
        
            elif priority == "4 - Low":
                return "Met" if row["resolution_hours"] <= self.params.sla.priority_4 else "Breached"
        
            else:
                return "Breached"

        df["sla_status"] = df.apply(
            get_status,
            axis=1
        )

        compliance = round(

            (
                df["sla_status"]
                .eq("Met")
                .mean()
            ) * 100,

            2

        )

        print(
            f"\nOverall SLA Compliance : {compliance}%"
        )

        return df
    def calculate_fcr(self,df):

        df["fcr"] = np.where(

            (
                (df["reopen_count"] == 0)
                &
                (df["reassignment_count"] == 0)
            ),

            1,

            0

        )

        fcr = round(

            df["fcr"].mean() * 100,

            2

        )

        print(f"\nFirst Call Resolution : {fcr}%")

        return df
    def performance_metrics(self,df):
        df=df
        total = len(df)

        closed = len(

            df[
                df["state"] == "Closed"
            ]

        )

        open_incidents = len(

            df[
                df["state"] != "Closed"
            ]

        )

        sla = round(

            (
                df["sla_status"]
                .eq("Met")
                .mean()
            ) * 100,

            2

        )

        mttr = round(

            df["resolution_hours"]
            .mean(),

            2

        )

        fcr = round(

            df["fcr"]
            .mean() * 100,

            2

        )

        metrics = {

            "Total Incidents": total,

            "Closed Incidents": closed,

            "Open Incidents": open_incidents,

            "MTTR(Hours)": mttr,

            "SLA Compliance(%)": sla,

            "FCR(%)": fcr

        }

        print("\nPerformance Metrics")

        for key, value in metrics.items():

            print(f"{key} : {value}")
         #print(df[["number", "resolution_hours"]].head(1))   
        local_path=self.config.local_data_file
                #print(f"Preprocessed data saved to: {local_path}")
        df.to_csv(local_path, index=False) 
        return df,metrics
    


    