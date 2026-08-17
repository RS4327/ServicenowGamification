import os 
import pandas as pd 
import numpy as np
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *

from ServicenowGamification.Components.Data_Sns_Oracle_Loader import IncidentDataLoader
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager


os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")

class MetricsCalculation:
    def __init__(self,config:DataMetricsCalculationConfig):
        self.config=config
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        config_manager=ConfigurationManager()
        self.loader = IncidentDataLoader(config_manager.get_oracle_connect_config() )
    def MTTR(self,df):
        if df is None:
            df = pd.read_csv(self.config.data_path)            
        df=pd.read_csv(self.config.data_path)
        #print(f"\n*-------------- Calculate MTTR(Mean Time To Resolve) ----------------*\n")
        date_columns = ["opened_at", "resolved_at", "closed_at"]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        df["resolution_time"] = df["resolved_at"] - df["opened_at"]
        df["resolution_hours"] = ((df["resolved_at"] - df["opened_at"]).dt.total_seconds() / 3600)
        mttr = df["resolution_hours"].mean()
        print("MTTR:", mttr)
      
        local_path=self.config.local_data_file
        #print(f"Preprocessed data saved to: {local_path}")
        #df.to_csv(local_path, index=False) 

        # ============================================================
        # AGENT LEVEL MTTR
        # ============================================================

        # Make sure date columns are datetime
        df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")

        df["resolved_at"] = pd.to_datetime(df["resolved_at"],errors="coerce")

        df["closed_at"] = pd.to_datetime(df["closed_at"],errors="coerce" )


        # ============================================================
        # RESOLUTION HOURS
        # ============================================================

        df["resolution_hours"] = ( (df["resolved_at"] - df["opened_at"]).dt.total_seconds()/ 3600)


        # ============================================================
        # VALID INCIDENTS FOR MTTR
        # ============================================================

        mttr_df = df[ df["assigned_to"].notna()& df["opened_at"].notna()& df["resolved_at"].notna()].copy()


        # ============================================================
        # AGENT LEVEL METRICS
        # ============================================================

        agent_mttr = ( mttr_df
            .groupby("assigned_to")
            .agg(
                MTTR_hours=(
                    "resolution_hours",
                    "mean"
                ),

                Resolved_Incident_Count=(
                    "resolved_at",
                    "count"
                ),

                Closed_Incident_Count=(
                    "closed_at",
                    "count"
                )
            )
            .reset_index()
        )


        # ============================================================
        # TOTAL COMPLETED INCIDENTS
        # ============================================================

        agent_mttr["Resolved_or_Closed_Count"] = (
            agent_mttr["Resolved_Incident_Count"]
            + agent_mttr["Closed_Incident_Count"]
        )

        agent_mttr.rename(columns={"assigned_to": "Agent"},inplace=True)
        agent_mttr.rename(columns={"Resolved_or_Closed_Count": "Total"},inplace=True)
        
        # ============================================================
        # SAVE
        # ============================================================
        save_path = os.path.join(
                        self.config.root_dir,
                        "AgentLevelMTTR.csv"
                    )
        if self.params.Oracle['Loader'] is None:
         
            
            agent_mttr.to_csv(
                        save_path,
                        index=False
                    )
            
        elif self.params.Oracle['Loader']=='Oracle':
            print('InSide oracle ')
            agent_mttr.to_csv(
                save_path,
                index=False
                )
            self.loader.run(agent_mttr,'MTTR')

            agent_mttr.to_csv(
                save_path,
                index=False
            )

        print(
            "Agent Level MTTR saved to:",
            save_path
        )

        print(agent_mttr)
        return df


    def calculate_art(self,df):
        """
        Average Resolution Time grouped by assignment group.
        """
        print("Art calculation")
        df=df

        # Only resolved incidents
        resolved_df = df[
            df["resolved_at"].notna()
            & df["assignment_group"].notna()
            & df["resolution_hours"].notna()
        ].copy()
        print(resolved_df.shape)
        group_art = (
            resolved_df
            .groupby("assignment_group")
            .agg(
                Average_Resolution_Time=(
                    "resolution_hours",
                    "mean"
                ),
                Resolved_Incident_Count=(
                    "resolved_at",
                    "count"
                )
            )
            .reset_index()
        )

        group_art["Average_Resolution_Time"] = (
            group_art["Average_Resolution_Time"]
            .round(2)
        )

        group_art.rename(
            columns={
                "assignment_group": "Assignment_Group"
            },
            inplace=True
        )

        # ============================================================
        # SAVE
        # ============================================================
        save_path = os.path.join(self.config.root_dir,"GroupLevelArt.csv")
        if self.params.Oracle['Loader']   is None:
            group_art.to_csv(save_path,index=False)
            
        elif self.params.Oracle['Loader']=='Oracle':
            print("Inside oracle art group")
            group_art.to_csv(save_path,index=False)
            self.loader.run(group_art,'AgentGroupART')        
        

        #============================================================
        # Agent level ART
        # ============================================================


        agent_art = (resolved_df.groupby(["assignment_group", "assigned_to"])
                     .agg(Average_Resolution_Time=( "resolution_hours","mean"),
                          Resolved_Incident_Count=("resolved_at","count"))
                          .reset_index())

        # Round ART
        agent_art["Average_Resolution_Time"] = (
            agent_art["Average_Resolution_Time"]
            .round(2)
        )

        # Rename columns
        agent_art.rename(
            columns={
                "assignment_group": "Assignment_Group",
                "assigned_to": "Agent"
            },
            inplace=True
        )

        print("\nAgent Level ART")
        #print(agent_art)
    


        # save_path = os.path.join(
        #     self.config.root_dir,
        #     "AgentLevelArt.csv"
        #     )



        # ============================================================
        # SAVE
        # ============================================================
        save_path = os.path.join(self.config.root_dir,"GroupLevelArt.csv")
        if self.params.Oracle['Loader']   is None:
            agent_art.to_csv(save_path,index=False)
                    
        elif self.params.Oracle['Loader']=='Oracle':
            print("Inside oracle art agent")
            agent_art.to_csv(save_path,index=False)
            self.loader.run(agent_art,'AgentART')              

        return df,group_art


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
        
        resolved_df = df[
            df["resolved_at"].notna()& 
            df["resolution_hours"].notna()& 
            df["assigned_to"].notna()
            ].copy()

            # =========================================================
        # OVERALL SLA
        # =========================================================

        total_resolved = len(resolved_df)

        sla_met = (
            resolved_df["sla_status"]
            .eq("Met")
            .sum()
        )

        sla_breached = (
            resolved_df["sla_status"]
            .eq("Breached")
            .sum()
        )

        if total_resolved > 0:

            sla_met_percentage = round(
                (sla_met / total_resolved) * 100,
                2
            )

            sla_breached_percentage = round(
                (sla_breached / total_resolved) * 100,
                2
            )

        else:

            sla_met_percentage = 0

            sla_breached_percentage = 0

        # =========================================================
        # CREATE OVERALL DATAFRAME
        # =========================================================

        overall_sla = pd.DataFrame({

            "SLA_Met_Count": [
                sla_met
            ],

            "SLA_Breached_Count": [
                sla_breached
            ],

            "Total_Resolved": [
                total_resolved
            ],

            "SLA_Met_Percentage": [
                sla_met_percentage
            ],

            "SLA_Breached_Percentage": [
                sla_breached_percentage
            ],

            "SLA_Compliance": [
                sla_met_percentage
            ]

        })

        # =========================================================
        # AGENT LEVEL SLA
        # =========================================================

        # Only incidents with an assigned agent
        agent_df = resolved_df[
            resolved_df["assigned_to"].notna()
            & (
                resolved_df["assigned_to"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

        agent_sla = (
            agent_df
            .groupby("assigned_to")
            .agg(

                Total_Resolved_Incidents=(
                    "resolved_at",
                    "count"
                ),

                SLA_Met=(
                    "sla_status",
                    lambda x: (x == "Met").sum()
                ),

                SLA_Breached=(
                    "sla_status",
                    lambda x: (x == "Breached").sum()
                )

            )
            .reset_index()
        )

        # =========================================================
        # AGENT SLA PERCENTAGES
        # =========================================================

        agent_sla["SLA_Met_Percentage"] = (
            (
                agent_sla["SLA_Met"]/agent_sla["Total_Resolved_Incidents"]
            ) * 100

        ).round(2)

        agent_sla["SLA_Breached_Percentage"] = (
            (
                agent_sla["SLA_Breached"]/agent_sla["Total_Resolved_Incidents"]) * 100
        ).round(2)

        # SLA compliance = SLA Met %
        agent_sla["SLA_Compliance"] = (agent_sla["SLA_Met_Percentage"])

        # =========================================================
        # RENAME AGENT
        # =========================================================

        agent_sla.rename(
            columns={
                "assigned_to": "Agent"
            },
            inplace=True
        )

        # =========================================================
        # SAVE OVERALL SLA
        # =========================================================
        overall_path = os.path.join(
                        self.config.root_dir,
                        "OverallSLA.csv"
                        )

        if self.params.Oracle['Loader'] is None:
            overall_sla.to_csv(
                        overall_path,
                        index=False
                    )
            
        elif self.params.Oracle['Loader']=='Oracle':
            overall_sla.to_csv(overall_path,index=False)
            self.loader.run(overall_sla,'OverallSLA')  

        # =========================================================
        # SAVE AGENT SLA
        # =========================================================
        agent_path = os.path.join(
                        self.config.root_dir,
                        "AgentLevelSLA.csv"
                    )
        
        if self.params.Oracle['Loader'] is None:
            
            agent_sla.to_csv(
                agent_path,
                index=False)

            
        elif self.params.Oracle['Loader']=='Oracle':
            agent_sla.to_csv(agent_path,index=False)
            self.loader.run(agent_sla,'AgentSLA')  
            
       
        

        
        # =========================================================
        # PUT STATUS BACK INTO ORIGINAL DATAFRAME
        # =========================================================

        # df["sla_status"] = None

        # df.loc[
        #     resolved_df.index,
        #     "sla_status"
        # ] = resolved_df["sla_status"]

        

        return df

    def calculate_fcr(self, df):

        df = df.copy()

        # =========================================================
        # CONVERT DATE COLUMNS
        # =========================================================

        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce"
        )

        df["closed_at"] = pd.to_datetime(
            df["closed_at"],
            errors="coerce"
        )

        # =========================================================
        # ONLY RESOLVED / CLOSED INCIDENTS
        # =========================================================

        fcr_df = df[(df["resolved_at"].notna()|df["closed_at"].notna())].copy()

        # =========================================================
        # FCR CALCULATION
        #
        # FCR = No Reopen AND No Reassignment
        # =========================================================

        fcr_df["fcr"] = np.where(((fcr_df["reopen_count"] == 0)& 
                                  (fcr_df["reassignment_count"] == 0)),1,0)

        # =========================================================
        # OVERALL FCR
        # =========================================================

        total_incidents = len(fcr_df)

        fcr_count = (fcr_df["fcr"].eq(1).sum())

        non_fcr_count = (fcr_df["fcr"].eq(0).sum())

        if total_incidents > 0:
            fcr_percentage = round( (fcr_count / total_incidents) * 100,2)
            non_fcr_percentage = round( (non_fcr_count / total_incidents) * 100,2)
        else:
            fcr_percentage = 0
            non_fcr_percentage = 0
        # =========================================================
        # CREATE OVERALL FCR DATAFRAME
        # =========================================================
        overall_fcr = pd.DataFrame({"Total_Incidents": [total_incidents],
                                    "FCR_Count": [fcr_count],
                                    "Non_FCR_Count": [non_fcr_count],
                                    "FCR_Percentage": [fcr_percentage],
                                    "Non_FCR_Percentage": [non_fcr_percentage]
                                    }
                                    )
        # =========================================================
        # AGENT LEVEL FCR
        # =========================================================

        agent_df = fcr_df[fcr_df["assigned_to"].notna()
                          &(fcr_df["assigned_to"].astype(str).str.strip()!= "")].copy()

        # =========================================================
        # GROUP BY AGENT
        # =========================================================

        agent_fcr = (agent_df.groupby("assigned_to").
                     agg(Total_Incidents=("fcr","count"),
                         FCR_Count=("fcr","sum"))
                         .reset_index()
                         )

        # =========================================================
        # NON-FCR COUNT
        # =========================================================

        agent_fcr["Non_FCR_Count"] = (agent_fcr["Total_Incidents"]-agent_fcr["FCR_Count"])

        # =========================================================
        # FCR %
        # =========================================================

        agent_fcr["FCR_Percentage"] = ((agent_fcr["FCR_Count"]/agent_fcr["Total_Incidents"])* 100).round(2)

        # =========================================================
        # NON-FCR %
        # =========================================================

        agent_fcr["Non_FCR_Percentage"] = ((agent_fcr["Non_FCR_Count"]/
                                            agent_fcr["Total_Incidents"])* 100
                                            ).round(2)

        # =========================================================
        # RENAME AGENT
        # =========================================================

        agent_fcr.rename(columns={ "assigned_to": "Agent"},inplace=True)

  
     
    
        overall_path = os.path.join(
                        self.config.root_dir,
                        "OverallFCR.csv"
                        )

        if self.params.Oracle['Loader'] is None:
            overall_fcr.to_csv(overall_path,index=False)
            
        elif self.params.Oracle['Loader']=='Oracle':
            overall_fcr.to_csv(overall_path,index=False)
            self.loader.run(overall_fcr,'OverallFCR')  

        # =========================================================
        # SAVE AGENT SLA
        # =========================================================
        agent_path = os.path.join(self.config.root_dir,"AgentLevelFCR.csv")
        
        if self.params.Oracle['Loader'] is None:
            agent_fcr.to_csv(agent_path,index=False)
            
        elif self.params.Oracle['Loader']=='Oracle':
            agent_fcr.to_csv(agent_path,index=False)
            self.loader.run(agent_fcr,'AgentFCR')              

        df["fcr"] = np.nan
        df.loc[
            fcr_df.index,
            "fcr"
        ] = fcr_df["fcr"]
        return df


    def performance_metrics(self, df):

        # =========================================================
        # COPY DATAFRAME
        # =========================================================

        df = df.copy()

        # =========================================================
        # BASIC DATA CLEANUP
        # =========================================================

        # Make sure date columns are datetime
        for col in ["opened_at", "resolved_at", "closed_at"]:

            if col in df.columns:

                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

        # Make sure required numeric columns are numeric
        df["resolution_hours"] = pd.to_numeric(
            df["resolution_hours"],
            errors="coerce"
        )

        df["fcr"] = pd.to_numeric(
            df["fcr"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # TOTAL INCIDENTS
        # =========================================================

        total = len(df)

        # =========================================================
        # CLOSED INCIDENTS
        # =========================================================

        closed = len(
            df[
                df["state"]
                .astype(str)
                .str.strip()
                .eq("Closed")
            ]
        )

        # =========================================================
        # RESOLVED INCIDENTS
        #
        # MTTR / SLA / FCR are calculated using incidents
        # that have resolution information.
        # =========================================================

        resolved_df = df[
            df["resolved_at"].notna()
            &
            df["resolution_hours"].notna()
        ].copy()

        resolved_count = len(
            resolved_df
        )

        # =========================================================
        # OPEN INCIDENTS
        #
        # Anything which is NOT Resolved and NOT Closed
        # =========================================================

        open_incidents = len(
            df[
                ~df["state"]
                .astype(str)
                .str.strip()
                .isin(
                    [
                        "Resolved",
                        "Closed"
                    ]
                )
            ]
        )

        # =========================================================
        # OVERALL MTTR
        # =========================================================

        if resolved_count > 0:

            mttr = round(
                resolved_df[
                    "resolution_hours"
                ].mean(),
                2
            )

        else:

            mttr = 0

        # =========================================================
        # OVERALL SLA
        # =========================================================

        if resolved_count > 0:

            # -----------------------------------------------------
            # SLA MET COUNT
            # -----------------------------------------------------

            sla_met_count = int(
                resolved_df[
                    "sla_status"
                ]
                .eq("Met")
                .sum()
            )

            # -----------------------------------------------------
            # SLA BREACHED COUNT
            # -----------------------------------------------------

            sla_breached_count = int(
                resolved_df[
                    "sla_status"
                ]
                .eq("Breached")
                .sum()
            )

            # -----------------------------------------------------
            # SLA COMPLIANCE %
            # -----------------------------------------------------

            sla = round(
                (
                    sla_met_count
                    /
                    resolved_count
                ) * 100,
                2
            )

        else:

            sla_met_count = 0
            sla_breached_count = 0
            sla = 0

        # =========================================================
        # OVERALL FCR
        # =========================================================

        if resolved_count > 0:

            # -----------------------------------------------------
            # FCR COUNT
            # fcr = 1 means FCR
            # fcr = 0 means Non-FCR
            # -----------------------------------------------------

            fcr_count = int(
                resolved_df[
                    "fcr"
                ].sum()
            )

            # -----------------------------------------------------
            # FCR %
            # -----------------------------------------------------

            fcr = round(
                resolved_df[
                    "fcr"
                ].mean() * 100,
                2
            )

        else:

            fcr_count = 0
            fcr = 0

        # =========================================================
        # OVERALL METRICS DICTIONARY
        # =========================================================

        metrics = {

            "Total Incidents":
                total,

            "Resolved Incidents":
                resolved_count,

            "Closed Incidents":
                closed,

            "Open Incidents":
                open_incidents,

            "MTTR(Hours)":
                mttr,

            "SLA_Met_Count":
                sla_met_count,

            "SLA_Breached_Count":
                sla_breached_count,

            "SLA Compliance(%)":
                sla,

            "FCR_Count":
                fcr_count,

            "FCR(%)":
                fcr
        }

        # =========================================================
        # CREATE OVERALL DATAFRAME
        # =========================================================

        overall_metrics_df = pd.DataFrame(
            [metrics]
        )

        # =========================================================
        # ROUND NUMERIC VALUES
        # =========================================================

        overall_metrics_df[
            "MTTR(Hours)"
        ] = overall_metrics_df[
            "MTTR(Hours)"
        ].round(2)

        overall_metrics_df[
            "SLA Compliance(%)"
        ] = overall_metrics_df[
            "SLA Compliance(%)"
        ].round(2)

        overall_metrics_df[
            "FCR(%)"
        ] = overall_metrics_df[
            "FCR(%)"
        ].round(2)

        # =========================================================
        # PRINT OVERALL METRICS
        # =========================================================

        print("\n")
        print("=" * 80)
        print("OVERALL PERFORMANCE METRICS")
        print("=" * 80)

        print(
            overall_metrics_df.to_string(
                index=False
            )
        )

        # =========================================================
        # SAVE OVERALL CSV
        # =========================================================

        overall_save_path = os.path.join(
            self.config.root_dir,
            "OverallPerformanceMetrics.csv"
        )

        overall_metrics_df.to_csv(
            overall_save_path,
            index=False
        )

        print(
            "\nOverall metrics saved to:",
            overall_save_path
        )

        # =========================================================
        # ORACLE - OVERALL
        # =========================================================

        if self.params.Oracle["Loader"] == "Oracle":

            self.loader.run(
                overall_metrics_df,
                "OverallMTCS"
            )

        # =========================================================
        # AGENT DATA
        # =========================================================

        agent_df = df[
            df["assigned_to"].notna()
            &
            (
                df["assigned_to"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

        # =========================================================
        # AGENT METRICS LIST
        # =========================================================

        agent_metrics_list = []

        # =========================================================
        # GROUP BY AGENT
        # =========================================================

        for agent, agent_data in agent_df.groupby(
            "assigned_to"
        ):

            # =====================================================
            # TOTAL INCIDENTS
            # =====================================================

            total_incidents = len(
                agent_data
            )

            # =====================================================
            # CLOSED INCIDENTS
            # =====================================================

            closed_incidents = len(
                agent_data[
                    agent_data["state"]
                    .astype(str)
                    .str.strip()
                    .eq("Closed")
                ]
            )

            # =====================================================
            # RESOLVED INCIDENTS
            # =====================================================

            agent_resolved_df = agent_data[
                agent_data["resolved_at"].notna()
                &
                agent_data[
                    "resolution_hours"
                ].notna()
            ].copy()

            resolved_incidents = len(
                agent_resolved_df
            )

            # =====================================================
            # OPEN INCIDENTS
            # =====================================================

            open_incidents_agent = len(
                agent_data[
                    ~agent_data["state"]
                    .astype(str)
                    .str.strip()
                    .isin(
                        [
                            "Resolved",
                            "Closed"
                        ]
                    )
                ]
            )

            # =====================================================
            # AGENT MTTR
            # =====================================================

            if resolved_incidents > 0:

                mttr_agent = round(
                    agent_resolved_df[
                        "resolution_hours"
                    ].mean(),
                    2
                )

            else:

                mttr_agent = 0

            # =====================================================
            # AGENT SLA
            # =====================================================

            if resolved_incidents > 0:

                # -------------------------------------------------
                # SLA MET COUNT
                # -------------------------------------------------

                sla_met_agent_count = int(
                    agent_resolved_df[
                        "sla_status"
                    ]
                    .eq("Met")
                    .sum()
                )

                # -------------------------------------------------
                # SLA BREACHED COUNT
                # -------------------------------------------------

                sla_breached_agent_count = int(
                    agent_resolved_df[
                        "sla_status"
                    ]
                    .eq("Breached")
                    .sum()
                )

                # -------------------------------------------------
                # SLA COMPLIANCE %
                # -------------------------------------------------

                sla_agent = round(
                    (
                        sla_met_agent_count
                        /
                        resolved_incidents
                    ) * 100,
                    2
                )

            else:

                sla_met_agent_count = 0
                sla_breached_agent_count = 0
                sla_agent = 0

            # =====================================================
            # AGENT FCR
            # =====================================================

            if resolved_incidents > 0:

                # -------------------------------------------------
                # FCR COUNT
                # -------------------------------------------------

                fcr_count_agent = int(
                    agent_resolved_df[
                        "fcr"
                    ].sum()
                )

                # -------------------------------------------------
                # FCR %
                # -------------------------------------------------

                fcr_agent = round(
                    agent_resolved_df[
                        "fcr"
                    ].mean() * 100,
                    2
                )

            else:

                fcr_count_agent = 0
                fcr_agent = 0

            # =====================================================
            # ADD AGENT RECORD
            # =====================================================

            agent_metrics_list.append({

                "Agent":
                    agent,

                "Total_Incidents":
                    total_incidents,

                "Resolved_Incidents":
                    resolved_incidents,

                "Closed_Incidents":
                    closed_incidents,

                "Open_Incidents":
                    open_incidents_agent,

                "MTTR_Hours":
                    mttr_agent,

                "SLA_Met_Count":
                    sla_met_agent_count,

                "SLA_Breached_Count":
                    sla_breached_agent_count,

                "SLA_Compliance":
                    sla_agent,

                "FCR_Count":
                    fcr_count_agent,

                "FCR":
                    fcr_agent
            })

        # =========================================================
        # CREATE AGENT DATAFRAME
        # =========================================================

        agent_metrics = pd.DataFrame(
            agent_metrics_list
        )

        # =========================================================
        # ROUND AGENT VALUES
        # =========================================================

        if not agent_metrics.empty:

            agent_metrics[
                "MTTR_Hours"
            ] = agent_metrics[
                "MTTR_Hours"
            ].round(2)

            agent_metrics[
                "SLA_Compliance"
            ] = agent_metrics[
                "SLA_Compliance"
            ].round(2)

            agent_metrics[
                "FCR"
            ] = agent_metrics[
                "FCR"
            ].round(2)

        # =========================================================
        # PRINT AGENT METRICS
        # =========================================================

        print("\n")
        print("=" * 80)
        print("AGENT PERFORMANCE METRICS")
        print("=" * 80)

        print(
            agent_metrics.to_string(
                index=False
            )
        )

        # =========================================================
        # SAVE AGENT CSV
        # =========================================================

        agent_save_path = os.path.join(
            self.config.root_dir,
            "AgentPerformanceMetrics.csv"
        )

        agent_metrics.to_csv(
            agent_save_path,
            index=False
        )

        print(
            "\nAgent metrics saved to:",
            agent_save_path
        )

        # =========================================================
        # ORACLE - AGENT
        # =========================================================

        if self.params.Oracle["Loader"] == "Oracle":

            self.loader.run(
                agent_metrics,
                "AgentMTCS"
            )

        # =========================================================
        # RETURN
        # =========================================================
        
        mttr_save_path = os.path.join(
                    self.config.root_dir,
                    "mttr.csv"
                )
        
        df.to_csv(
                    mttr_save_path,
                    index=False
                )
        
        return df, metrics



    