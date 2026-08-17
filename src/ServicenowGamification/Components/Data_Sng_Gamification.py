import os 
import pandas as pd 
import numpy as np
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")
from ServicenowGamification.Components.Data_Sns_Oracle_Loader import IncidentDataLoader
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager


class Gamification: 
    def __init__(self,config:DataGamificationConfig):
        self.config=config
        self.params = Read_Yaml(PARAMS_FILE_PATH)

        config_manager=ConfigurationManager()
        self.loader = IncidentDataLoader(config_manager.get_oracle_connect_config() )

    def calculate_points(self,df):
        df=df
        if df is None:
            df = pd.read_csv(self.config.data_path)
                

        print("=" * 80)
        print("              GAMIFICATION POINT CALCULATION")
        print("=" * 80)

        # ========================================================
        # LOAD DATA
        # ========================================================

        df = pd.read_csv(self.config.data_path)

        df = df.copy()
    
        # ========================================================
        # REQUIRED COLUMNS
            # ========================================================

        required_columns = [

            "number",
            "assigned_to",
            "assignment_group",
            "state",
            "sla_status",
            "fcr",
            "priority",
            "reopen_count",
            "reassignment_count"

        ]
        df["total_incidents"] = (
           df.groupby("assigned_to")["number"]
              .transform("count")
              )
        

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"Required column missing: {column}")

        # ========================================================
        # OPTIONAL CUSTOMER RATING
        # ========================================================

        if "customer_rating" not in df.columns:
            print( "customer_rating column not found."" Defaulting to 0.")
            df["customer_rating"] = 0

        # ========================================================
        # CLEAN NUMERIC COLUMNS
        # ========================================================

        df["fcr"] = pd.to_numeric(df["fcr"],errors="coerce").fillna(0)
        df["reopen_count"] = pd.to_numeric(df["reopen_count"],errors="coerce").fillna(0)
        df["reassignment_count"] = pd.to_numeric(df["reassignment_count"],errors="coerce").fillna(0)

        df["customer_rating"] = pd.to_numeric(df["customer_rating"],errors="coerce").fillna(0)

        # ========================================================
        # INCIDENT LEVEL POINT COLUMNS
        # ========================================================

        incident_closed_points = []
        sla_points = []
        fcr_points = []
        priority_points = []
        rating_points = []
        reopen_penalty_points = []
        reassignment_penalty_points = []
        total_points = []

        # ========================================================
        # INCIDENT LEVEL CALCULATION
        # ========================================================

        for _, row in df.iterrows():

            points = 0

            closed_points = 0
            sla_met_points = 0
            first_call_points = 0
            high_priority_points = 0
            customer_rating_points = 0
            reopen_penalty = 0
            reassignment_penalty = 0

            # ====================================================
            # 1. INCIDENT CLOSED
            # ====================================================

            if (str(row["state"]).strip().lower()== "closed"):

                closed_points = (self.params.gamification.points["incident_closed"])
                points += closed_points

            # ====================================================
            # 2. SLA MET
            # ====================================================

            if (str(row["sla_status"]).strip().lower()== "met"):

                sla_met_points = (self.params.gamification.points["sla_met"])
                points += sla_met_points

            # ====================================================
            # 3. FIRST CALL RESOLUTION
            # ====================================================

            if row["fcr"] == 1:

                first_call_points = (self.params.gamification.points["first_call_resolution"])
                points += first_call_points

            # ====================================================
            # 4. HIGH PRIORITY BONUS
            # ====================================================

            if (str(row["priority"]).strip()== "1 - Critical"):

                high_priority_points = (self.params.gamification.points["high_priority_bonus"])
                points += high_priority_points

            # ====================================================
            # 5. CUSTOMER RATING BONUS
            # ====================================================

            if row["customer_rating"] >= 4.5:
                customer_rating_points = (self.params.gamification.points["customer_rating_bonus"])
                points += customer_rating_points

            # ====================================================
            # 6. REOPEN PENALTY
            # ====================================================

            if row["reopen_count"] > 0:
                reopen_penalty_value = abs(self.params.gamification.points["reopen_penalty"])

                reopen_penalty = (reopen_penalty_value* row["reopen_count"] * -1)
                print('reopen_penalty : ',reopen_penalty)
                points += reopen_penalty

            # ====================================================
            # 7. REASSIGNMENT PENALTY
            # ====================================================

            if row["reassignment_count"] > 0:
                reassignment_penalty_value = abs(self.params.gamification.points["reassignment_penalty"])
                reassignment_penalty = (reassignment_penalty_value* row["reassignment_count"]* -1)
                points += reassignment_penalty

            # ====================================================
            # STORE INCIDENT COMPONENTS
            # ====================================================

            incident_closed_points.append(closed_points)
            sla_points.append(sla_met_points)
            fcr_points.append(first_call_points)
            priority_points.append(high_priority_points)
            rating_points.append(customer_rating_points)
            reopen_penalty_points.append( reopen_penalty)
            reassignment_penalty_points.append(reassignment_penalty)
            total_points.append(points)

        # ========================================================
        # ADD POINT COLUMNS TO INCIDENT DATA
        # ========================================================

        df["incident_closed_points"] = (incident_closed_points)
        df["sla_points"] = (sla_points)
        df["fcr_points"] = (fcr_points)
        df["priority_points"] = (priority_points)
        df["customer_rating_points"] = (rating_points)
        df["reopen_penalty_points"] = (reopen_penalty_points)
        df["reassignment_penalty_points"] = (reassignment_penalty_points)
        df["points"] = (total_points)
        df["average_points"]= df["points"].mean()

        # ========================================================
        # INCIDENT LEVEL TOTAL
        # ========================================================

        print()
        print("=" * 80)
        print("INCIDENT LEVEL POINTS")
        print("=" * 80)

        print(
            df[
                [
                    "number",
                    "assigned_to",
                    "assignment_group",
                    "points"
                ]
            ].to_string(index=False)
        )

        # ========================================================
        # SAVE INCIDENT LEVEL
        # ========================================================

        incident_path = os.path.join(self.config.root_dir,"IncidentPoints.csv")
        if self.params.Oracle['Loader'] is None:
            df.to_csv(incident_path,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(df,'InsGMF')  
        


        # ========================================================
        # AGENT LEVEL
        # ========================================================

        agent_df = df[df["assigned_to"].notna()&
                      ( df["assigned_to"].astype(str).str.strip()!= "")
                      ].copy()

        # ========================================================
        # AGENT AGGREGATION
        # ========================================================

        agent_points = ( agent_df.groupby("assigned_to").agg(
                Total_Incidents=("number",
                    "count"
                ),

                Total_Points=(
                    "points",
                    "sum"
                ),

                Average_Points=(
                    "points",
                    "mean"
                ),

                Closed_Incidents=(
                    "state",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "closed"
                    ).sum()
                ),

                SLA_Met_Count=(
                    "sla_status",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "met"
                    ).sum()
                ),

                FCR_Count=(
                    "fcr",
                    lambda x:
                    (x == 1).sum()
                ),

                Reopen_Count=(
                    "reopen_count",
                    "sum"
                ),

                Reassignment_Count=(
                    "reassignment_count",
                    "sum"
                )
            )
            .reset_index()
        )

        # ========================================================
        # AGENT RANK
        # ========================================================
        agent_points = agent_points.sort_values(
            by="Total_Points",
            ascending=False
        )
        agent_points["Agent_Rank"] = (

            agent_points[
                "Total_Points"
            ]

            .rank(
                method="dense",
                ascending=False
            )

            .astype(int)
        )

        # ========================================================
        # RENAME AGENT
        # ========================================================

        agent_points.rename(
            columns={
                "assigned_to": "Agent"
            },
            inplace=True
        )

        # ========================================================
        # ROUND AGENT VALUES
        # ========================================================

        agent_points[
            "Average_Points"
        ] = (
            agent_points[
                "Average_Points"
            ].round(2)
        )

        # ========================================================
        # SAVE AGENT LEVEL
        # ========================================================

        agent_path = os.path.join(
            self.config.root_dir,
            "AgentPoints.csv"
        )

        if self.params.Oracle['Loader'] is None:
            agent_points.to_csv(agent_path,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(agent_points,'AgentRNK')  

       

        print(
            "Agent Points saved:",
            agent_path
        )

        # ========================================================
        # ASSIGNMENT GROUP LEVEL
        # ========================================================

        group_df = df[
            df["assignment_group"].notna()
            &
            (
                df["assignment_group"]
                .astype(str)
                .str.strip()
                != ""
            )
        ].copy()

        # ========================================================
        # GROUP AGGREGATION
        # ========================================================

        group_points = (

            group_df

            .groupby("assignment_group")

            .agg(

                Total_Incidents=(
                    "number",
                    "count"
                ),

                Total_Points=(
                    "points",
                    "sum"
                ),

                Average_Points=(
                    "points",
                    "mean"
                ),

                Closed_Incidents=(
                    "state",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "closed"
                    ).sum()
                ),

                SLA_Met_Count=(
                    "sla_status",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "met"
                    ).sum()
                ),

                FCR_Count=(
                    "fcr",
                    lambda x:
                    (x == 1).sum()
                ),

                Reopen_Count=(
                    "reopen_count",
                    "sum"
                ),

                Reassignment_Count=(
                    "reassignment_count",
                    "sum"
                )

            )

            .reset_index()
        )

        # ========================================================
        # GROUP RANK
        # ========================================================

        group_points = group_points.sort_values(
            by="Total_Points",
            ascending=False
        )

        group_points["Group_Rank"] = (

            group_points[
                "Total_Points"
            ]

            .rank(
                method="dense",
                ascending=False
            )

            .astype(int)
        )

        # ========================================================
        # RENAME GROUP
        # ========================================================

        group_points.rename(
            columns={
                "assignment_group":
                "Assignment_Group"
            },
            inplace=True
        )

        # ========================================================
        # ROUND GROUP VALUES
        # ========================================================

        group_points[
            "Average_Points"
        ] = (
            group_points[
                "Average_Points"
            ].round(2)
        )

        # ========================================================
        # SAVE GROUP LEVEL
        # ========================================================

        group_path = os.path.join(
            self.config.root_dir,
            "GroupPoints.csv"
        )
        if self.params.Oracle['Loader'] is None:
            group_points.to_csv(group_path,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(group_points,'GPRNK')  

        print(
            "Group Points saved:",
            group_path
        )

        # ========================================================
        # OVERALL LEVEL
        # ========================================================

        total_incidents = (
            df["number"].count()
        )

        total_points = (
            df["points"].sum()
        )

        average_points = (
            df["points"].mean()
        )

        closed_incidents = (

            df["state"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("closed")
            .sum()
        )

        sla_met_count = (

            df["sla_status"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("met")
            .sum()
        )

        fcr_count = (
            df["fcr"].eq(1).sum()
        )

        reopen_count = (
            df["reopen_count"].sum()
        )

        reassignment_count = (
            df["reassignment_count"].sum()
        )

        # ========================================================
        # OVERALL DATAFRAME
        # ========================================================

        overall_points = {

            "Total_Incidents":
                total_incidents,

            "Total_Points":
                total_points,

            "Average_Points_Per_Incident":
                round(
                    average_points,
                    2
                ),

            "Closed_Incidents":
                closed_incidents,

            "SLA_Met_Count":
                sla_met_count,

            "FCR_Count":
                fcr_count,

            "Reopen_Count":
                reopen_count,

            "Reassignment_Count":
                reassignment_count

        }

        overall_points_df = pd.DataFrame(
            [overall_points]
        )

        # ========================================================
        # SAVE OVERALL LEVEL
        # ========================================================

        overall_path = os.path.join(
            self.config.root_dir,
            "OverallGamificationPoints.csv"
        )



        overall_points_df.to_csv(
            overall_path,
            index=False
        )

        # ========================================================
        # PRINT OVERALL
        # ========================================================

        print()
        print("=" * 80)
        print("OVERALL GAMIFICATION POINTS")
        print("=" * 80)

        print(
            overall_points_df.to_string(
                index=False
            )
        )

        print(
            "\nOverall Points saved:",
            overall_path
        )

        # ========================================================
        # FINAL SUMMARY
        # ========================================================

        print()
        print("=" * 80)
        print("GAMIFICATION CALCULATION COMPLETED")
        print("=" * 80)

        print(
            "Incident File :",
            incident_path
        )

        print(
            "Agent File    :",
            agent_path
        )

        print(
            "Group File    :",
            group_path
        )

        print(
            "Overall File  :",
            overall_path
        )

        print("=" * 80)



        # ============================================================
        # AGENT WISE RANKING WITHIN ASSIGNMENT GROUP
        # ============================================================

        agent_group_points = (
            df[
                df["assigned_to"].notna()
                &
                (df["assigned_to"].astype(str).str.strip() != "")
                &
                df["assignment_group"].notna()
                &
                (df["assignment_group"].astype(str).str.strip() != "")
            ]
            .groupby(
                ["assignment_group", "assigned_to"]
            )
            .agg(
                Total_Incidents=("number", "count"),
                Total_Points=("points", "sum"),
                Average_Points=("points", "mean"),

                Closed_Incidents=(
                    "state",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "closed"
                    ).sum()
                ),

                SLA_Met_Count=(
                    "sla_status",
                    lambda x:
                    (
                        x.astype(str)
                        .str.strip()
                        .str.lower()
                        == "met"
                    ).sum()
                ),

                FCR_Count=(
                    "fcr",
                    lambda x: (x == 1).sum()
                ),

                Reopen_Count=(
                    "reopen_count",
                    "sum"
                ),

                Reassignment_Count=(
                    "reassignment_count",
                    "sum"
                )
            )
            .reset_index()
        )


        # ============================================================
        # RANK AGENTS WITHIN EACH GROUP
        # ============================================================

        agent_group_points["Group_Rank"] = (
            agent_group_points
            .groupby("assignment_group")["Total_Points"]
            .rank(
                method="dense",
                ascending=False
            )
            .astype(int)
        )


        # ============================================================
        # SORT
        # ============================================================

        agent_group_points = (
            agent_group_points
            .sort_values(
                by=[
                    "assignment_group",
                    "Group_Rank"
                ],
                ascending=[
                    True,
                    True
                ]
            )
            .reset_index(drop=True)
        )


        # ============================================================
        # ROUND
        # ============================================================

        agent_group_points["Average_Points"] = (
            agent_group_points["Average_Points"]
            .round(2)
        )


        # ============================================================
        # RENAME
        # ============================================================

        agent_group_points.rename(
            columns={
                "assignment_group": "Assignment_Group",
                "assigned_to": "Agent"
            },
            inplace=True
        )


        # ============================================================
        # SAVE
        # ============================================================

        save_path = os.path.join(
            self.config.root_dir,
            "AgentGroupRanking.csv"
        )
        if self.params.Oracle['Loader'] is None:
            agent_group_points.to_csv(save_path,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(agent_group_points,'AgentGpRNK')  
       

        return  df



    ##################################################################
    # Analyst Wise Summary
    ##################################################################

    def analyst_summary(self,df):
            df=df
            summary = (

                df

                .groupby("assigned_to")

                .agg(

                    total_incidents=("number", "count"),

                    total_points=("points", "sum"),

                    sla_met=("sla_status", lambda x: (x == "Met").sum()),

                    average_resolution=("resolution_hours", "mean")

                )

                .reset_index()

            )

            summary["average_resolution"] = summary[
                "average_resolution"
            ].round(2)

            summary = summary.sort_values(

                by="total_points",

                ascending=False

            )

            df = df.merge(
                        summary[
                            [
                                "assigned_to",
                                "average_resolution" 
                            ]
                        ],
                        on="assigned_to",
                        how="left"
                    )
            
            return df,summary
        ##################################################################
    # Save Results
    ##################################################################

    def p_save(self,df):
         
        incident_path =self.config.incident_points
        
        

        summary_path =self.config.analyst_points

        df,df_analyst_summary = self.analyst_summary(df)
       

        if self.params.Oracle['Loader'] is None:
            df_analyst_summary.to_csv(summary_path,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(df_analyst_summary,'AgentPerSMRY')  
            
        df.to_csv(
            incident_path,
            index=False
            )

        print(f"Incident points saved to : {incident_path}")

        print(f"Analyst summary saved to : {summary_path}")
        analyst_path =os.path.join(self.config.root_dir,'P_df_analyst_summary.csv')
        df_analyst_summary.to_csv(
                    analyst_path,
                    index=False
                    )
        return df,df_analyst_summary
           

    # def assign_badges(self,df):
        
    #     print("##################################################################")
    #     print(f" #  Badge Assignment")
    #     print("##################################################################") 
    #     badge_list = []

    #     for _, row in df.iterrows():
    #         points = row["points"]
    #         if points >= self.params.gamification.badges["legend"]["min_points"]:
    #             badge = "Legend"
    #         elif points >= self.params.gamification.badges["platinum"]["min_points"]:
    #             badge = "Platinum"
    #         elif points >= self.params.gamification.badges["gold"]["min_points"]:
    #             badge = "Gold"
    #         elif points >= self.params.gamification.badges["silver"]["min_points"]:
    #             badge = "Silver"
    #         elif points >= self.params.gamification.badges["bronze"]["min_points"]:
    #             badge = "Bronze"
    #         else:
    #             badge = "Rookie"

    #         badge_list.append(badge)

    #     df["badge"] = badge_list

    #     print('badge columns ',df.columns)


        ##################################################################
    # Badge Assignment - Incident + Agent + Group + Overall
    ##################################################################

    def assign_badges(self, df):

        import os
        import pandas as pd

        print("=" * 70)
        print("BADGE ASSIGNMENT")
        print("=" * 70)

        # ==============================================================
        # OUTPUT DIRECTORY
        # ==============================================================

        output_dir = "Artifacts/DataGamification"

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        # ==============================================================
        # BADGE FUNCTION
        # ==============================================================

        def get_badge(points):

            if pd.isna(points):
                points = 0

            points = float(points)

            if points >= self.params.gamification.badges["legend"]["min_points"]:
                return "Legend"

            elif points >= self.params.gamification.badges["platinum"]["min_points"]:
                return "Platinum"

            elif points >= self.params.gamification.badges["gold"]["min_points"]:
                return "Gold"

            elif points >= self.params.gamification.badges["silver"]["min_points"]:
                return "Silver"

            elif points >= self.params.gamification.badges["bronze"]["min_points"]:
                return "Bronze"

            else:
                return "Rookie"

        # ==============================================================
        # 1. INCIDENT LEVEL
        # ==============================================================

        print("\n1. INCIDENT LEVEL")

        df["badge"] = (df["points"].apply(get_badge) )

        incident_file = os.path.join(output_dir,"incident_gamification.csv")

        df.to_csv(incident_file,index=False)


        # ==============================================================
        # 2. AGENT LEVEL
        # ==============================================================

        print("\n2. AGENT LEVEL")

        agent_summary = (df.groupby("assigned_to")
            .agg(
                total_incidents=("number", "count"),
                total_points=("points", "sum"),
                average_points=("points", "mean")
            )
            .reset_index()
        )

        agent_summary["total_points"] = (
            agent_summary["total_points"].round(2)
        )

        agent_summary["average_points"] = (
            agent_summary["average_points"].round(2)
        )

        agent_summary["agent_badge"] = (
            agent_summary["total_points"]
            .apply(get_badge)
        )

        agent_summary = agent_summary.sort_values(
            by="total_points",
            ascending=False
        )

        agent_file = os.path.join(
            output_dir,
            "agent_badge_summary.csv"
        )

        if self.params.Oracle['Loader'] is None:
            agent_summary.to_csv(agent_file,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(agent_summary,'AgentBdgeSMRY') 

        # agent_summary.to_csv(
        #     agent_file,
        #     index=False
        # )


        # ==============================================================
        # 3. GROUP LEVEL
        # ==============================================================

        print("\n3. GROUP LEVEL")

        group_summary = (
            df
            .groupby("assignment_group")
            .agg(
                total_incidents=("number", "count"),
                total_points=("points", "sum"),
                average_points=("points", "mean")
            )
            .reset_index()
        )

        group_summary["total_points"] = (
            group_summary["total_points"].round(2)
        )

        group_summary["average_points"] = (
            group_summary["average_points"].round(2)
        )

        group_summary["group_badge"] = (
            group_summary["total_points"]
            .apply(get_badge)
        )

        group_summary = group_summary.sort_values(
            by="total_points",
            ascending=False
        )

        group_file = os.path.join(
            output_dir,
            "group_badge_summary.csv"
        )

        if self.params.Oracle['Loader'] is None:
            group_summary.to_csv(group_file,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(group_summary,'GPBdgeSMRY') 


        # group_summary.to_csv(
        #     group_file,
        #     index=False
        # )

        print(
            "Group CSV saved:",
            group_file
        )

        # ==============================================================
        # 4. OVERALL LEVEL
        # ==============================================================

        print("\n4. OVERALL LEVEL")

        overall_points = df["points"].sum()

        overall_incidents = df["number"].count()

        overall_average_points = (
            df["points"].mean()
        )

        overall_badge = get_badge(
            overall_points
        )

        overall_summary = pd.DataFrame(
            [
                {
                    "total_incidents":
                        overall_incidents,

                    "total_points":
                        round(
                            overall_points,
                            2
                        ),

                    "average_points":
                        round(
                            overall_average_points,
                            2
                        ),

                    "overall_badge":
                        overall_badge
                }
            ]
        )

        overall_file = os.path.join(
            output_dir,
            "overall_badge_summary.csv"
        )

        overall_summary.to_csv(
            overall_file,
            index=False
        )

        print(
            "Overall CSV saved:",
            overall_file
        )

        # ==============================================================
        # 5. ADD AGENT BADGE TO INCIDENT DATA
        # ==============================================================

        df = df.merge(

            agent_summary[
                [
                    "assigned_to",
                    "agent_badge"
                ]
            ],

            on="assigned_to",

            how="left"
        )

        # ==============================================================
        # 6. ADD GROUP BADGE TO INCIDENT DATA
        # ==============================================================

        df = df.merge(

            group_summary[
                [
                    "assignment_group",
                    "group_badge"
                ]
            ],

            on="assignment_group",

            how="left"
        )

        # ==============================================================
        # 7. ADD OVERALL BADGE
        # ==============================================================

        df["overall_badge"] = overall_badge

        # ==============================================================
        # 8. SAVE FINAL INCIDENT DATA AGAIN
        # ==============================================================

        df.to_csv(
            incident_file,
            index=False
        )
        return df 

    ##################################################################
    # Badge Summary
    ##################################################################

    def badge_summary(self,df):
        df=df

        
        summary = (
            df
            .groupby("badge")

            .size()

            .reset_index(name="employee_count")

            .sort_values(
                by="employee_count",
                ascending=False
            )

        )

        return summary

    ##################################################################
    # Save Results
    ##################################################################

    def b_save(self,df):

        df=df
       

        badge_file = self.config.badgeresults

        summary_file = self.config.badgesummary

        df.to_csv(
            badge_file,
            index=False
        )
        self.badge_summary(df).to_csv(
                            summary_file,
                            index=False
                        )
       

        print(f"Badge results saved to : {badge_file}")
        print(f"Badge summary saved to : {summary_file}")

        return df

    #def calculate_level(self, df):

    def calculate_level(self, df):

        print("=" * 80)
        print("CALCULATING AGENT, GROUP AND OVERALL LEVELS")
        print("=" * 80)
        print('calculate_level columns ',df.columns)

        # ============================================================
        # 1. LEVEL CONFIGURATION
        # ============================================================

        ordered_levels = sorted(self.params.gamification.levels.items(),key=lambda x: x[1]["min_points"])

        print("\nConfigured Levels:")

        for _, level in ordered_levels:
            print(
                f"{level['name']} -> "
                f"{level['min_points']} points"
            )

        # ============================================================
        # HELPER FUNCTION
        # ============================================================

        def get_level(points):

            points = float(points or 0)

            current_level = 1
            current_name = ordered_levels[0][1]["name"]
            current_min = ordered_levels[0][1]["min_points"]

            next_min_points = None

            # --------------------------------------------------------
            # Find current level
            # --------------------------------------------------------

            for index, (_, level) in enumerate(ordered_levels):
                if points >= level["min_points"]:
                    current_level = index + 1
                    current_name = level["name"]
                    current_min = level["min_points"]

                    if index < len(ordered_levels) - 1:
                        next_min_points = (ordered_levels[index + 1][1]["min_points"])
                    else:
                        next_min_points = None

            # --------------------------------------------------------
            # Highest level
            # --------------------------------------------------------

            if next_min_points is None:
                progress = 100
                points_to_next = 0
            else:
                denominator = (next_min_points - current_min)
                if denominator <= 0:
                    progress = 100
                else:
                    progress = ((points - current_min)/ denominator) * 100
                progress = max(0,min(progress, 100))

                points_to_next = max(0,next_min_points - points)

            return {
                "level": current_level,
                "level_name": current_name,
                "points_to_next_level": points_to_next,
                "level_progress": round(progress, 2)
            }

        # ============================================================
        # 2. AGENT LEVEL
        # ============================================================

        print("\nCalculating Agent Level...")
        agent_df = df.copy()

        # Make sure points are numeric

        agent_df["points"] = pd.to_numeric(agent_df["points"], errors="coerce").fillna(0)
        agent_levels = agent_df["points"].apply(get_level)
        agent_df["level"] = agent_levels.apply(lambda x: x["level"])
        agent_df["level_name"] = agent_levels.apply(lambda x: x["level_name"])
        agent_df["points_to_next_level"] = agent_levels.apply(lambda x: x["points_to_next_level"])
        agent_df["level_progress"] = agent_levels.apply(lambda x: x["level_progress"] )

        # ============================================================
        # SAVE AGENT LEVEL
        # ============================================================
        df=agent_df.copy()
        agent_output = os.path.join(self.config.root_dir,"AgentLevel.csv")

        #if self.params.Oracle['Loader'] is None:
        print('agent_df',agent_df.columns)

        agent_df = agent_df[
            [
                "assigned_to",
                "total_incidents",
                "points",
                "average_points",
                "level",
                "level_name",
                "points_to_next_level",
                "level_progress"
            ]
            ]

        agent_df.rename(
                columns={
                    "assigned_to": "Agent"
                },
                inplace=True
            )
        
        if self.params.Oracle['Loader'] is None:
            agent_df.to_csv(agent_output,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(agent_df,'AgentLvlSMRY')  


        # ============================================================
        # 3. GROUP LEVEL
        # ============================================================

        print("\nCalculating Group Level...")

        if "assignment_group" not in df.columns:
            raise ValueError(
                "assignment_group column is missing"
            )

        group_df = (
            df.groupby(
                "assignment_group",
                dropna=False
            )
            .agg(
                total_incidents=(
                    "number",
                    "count"
                ),
                total_points=(
                    "points",
                    "sum"
                ),
                average_points=(
                    "points",
                    "mean"
                )
            )
            .reset_index()
        )

        group_df["total_points"] = pd.to_numeric(
            group_df["total_points"],
            errors="coerce"
        ).fillna(0)

        group_levels = group_df["total_points"].apply(
            get_level
        )

        group_df["level"] = group_levels.apply(
            lambda x: x["level"]
        )

        group_df["level_name"] = group_levels.apply(
            lambda x: x["level_name"]
        )

        group_df["points_to_next_level"] = group_levels.apply(
            lambda x: x["points_to_next_level"]
        )

        group_df["level_progress"] = group_levels.apply(
            lambda x: x["level_progress"]
        )

        # ============================================================
        # SAVE GROUP LEVEL
        # ============================================================

        # group_output = os.path.join(
        #     "Artifacts",
        #     "Gamification",
        #     "GroupLevel.csv"
        # )
        
        group_output = os.path.join(self.config.root_dir,"GroupLevel.csv")

        if self.params.Oracle['Loader'] is None:
            group_df.to_csv(group_output,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(group_df,'GPLvlSMRY')  

        # group_df.to_csv(
        #     group_output,
        #     index=False
        # )


        # ============================================================
        # 4. OVERALL LEVEL
        # ============================================================

        print("\nCalculating Overall Level...")

        total_points = (
            pd.to_numeric(
                df["points"],
                errors="coerce"
            )
            .fillna(0)
            .sum()
        )

        overall_level = get_level(
            total_points
        )

        overall_df = pd.DataFrame(
            [
                {
                    "total_incidents": len(df),
                    "total_points": total_points,
                    "level": overall_level["level"],
                    "level_name": overall_level["level_name"],
                    "points_to_next_level":
                        overall_level[
                            "points_to_next_level"
                        ],
                    "level_progress":
                        overall_level[
                            "level_progress"
                        ]
                }
            ]
        )

        # ============================================================
        # SAVE OVERALL LEVEL
        # ============================================================

        # overall_output = os.path.join(
        #     "Artifacts",
        #     "Gamification",
        #     "OverallLevel.csv"
        # )
        overall_output = os.path.join(self.config.root_dir,"OverallLevel.csv")
        overall_df.to_csv(
            overall_output,
            index=False
        )

        print(
            "Overall level saved:",
            overall_output
        )

        # ============================================================
        # DISPLAY SUMMARY
        # ============================================================

        # print("\n" + "=" * 80)
        # print("LEVEL CALCULATION COMPLETED")
        # print("=" * 80)

        # print("\nAGENT LEVEL")
        # print(
        #     agent_df[
        #         [
        #             "assigned_to",
        #             "points",
        #             "level",
        #             "level_name",
        #             "points_to_next_level",
        #             "level_progress"
        #         ]
        #     ].head()
        # )

        # print("\nGROUP LEVEL")

        # print(
        #     group_df[
        #         [
        #             "assignment_group",
        #             "total_incidents",
        #             "total_points",
        #             "level",
        #             "level_name",
        #             "points_to_next_level",
        #             "level_progress"
        #         ]
        #     ]
        # )

        # print("\nOVERALL LEVEL")

        # print(
        #     overall_df
        # )

        # # ============================================================
        # RETURN ALL THREE
        # ============================================================

        # return (
        #     agent_df,
        #     group_df,
        #     overall_df
        # )
        return df


    

    ####################################################################
    # Level Summary
    ####################################################################

    def level_summary(self,df):
        df=df

        summary = (

            df

            .groupby(["level", "level_name"])

            .size()

            .reset_index(name="employee_count")

            .sort_values(
                by="level",
                ascending=True
            )

        )

        return summary

    ####################################################################
    # Save Results
    ####################################################################

    def l_save(self,df):
        df=df
        print('l svae :',df.columns)
        levelresults =self.config.levelresults
        levelsummary = self.config.levelsummary

        df.to_csv(
            levelresults,
            index=False
        )

        self.level_summary(df).to_csv(
            levelsummary,
            index=False
        )

        print(f"Level results saved to : {levelresults}")
        print(f"Level summary saved to : {levelsummary}")
        print('l svae :',df.columns)
        return df


    ##############################################################
    # Overall Leaderboard
    ##############################################################

    def generate_leaderboard(self,df,o_df):
        df=df   
        df_lead=o_df
        print('l df_lead  c:',df_lead.columns) 
        print("Type of df:", type(df))
        print('##############################################################')
        print('# Overall Leaderboard')
        print('##############################################################')

        df = df.sort_values(

            by=[
                "total_points",
                "total_incidents"
            ],

            ascending=[
                False,
                False
            ]

        ).reset_index(drop=True)

        df["rank"] = df.index + 1
        print('l svae   df  :',df.columns) 
        print('df_lead columns before',df_lead.columns)

        df_lead = df_lead.merge(
            df[
                [
                    "assigned_to",
                    "rank" 
                ]
            ],
            on="assigned_to",
            how="left"
        )
        df_lead = df_lead.rename(columns={"rank": "leaderboard_rank"})
        #lead_board_file=self.config.root_dir/"Leaderboardsummary.csv"
        lead_board_file = os.path.join(self.config.root_dir, "Leaderboardsummary.csv")
        print('df_lead columns',df_lead.columns)
        print("Type of df:", type(df))
        df_lead.to_csv(lead_board_file,index=False)
        return df,df_lead

    ##############################################################
    # Assignment Group Leaderboard
    ##############################################################

    def assignment_group_leaderboard(self, df):

        print("\nGenerating Assignment Group Leaderboard...")

        # Validate input
        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                f"Expected DataFrame, received {type(df)}"
            )

        print("Input shape:", df.shape)

        # Validate required column
        if "assignment_group" not in df.columns:
            raise ValueError(
                "assignment_group column not found in DataFrame"
            )

        # Create group-level summary
        group_df = (
            df.groupby("assignment_group")
            .agg(
                total_incidents=("number", "count"),
                total_points=("points", "sum")
            )
            .reset_index()
        )

        # Calculate group rank
        group_df["group_rank"] = (
            group_df["total_points"]
            .rank(
                method="dense",
                ascending=False
            )
            .astype(int)
        )

        # Sort by rank
        group_df = group_df.sort_values(
            "group_rank"
        )

        print("\nAssignment Group Leaderboard:")
        print(group_df)

        return group_df

    ##############################################################
    # Top N Employees
    ##############################################################

    def top_performers(self,df):
        df=df
        top_n = self.params.gamification.leaderboard["top_n"]

        return df.head(top_n)

    ##############################################################
    # Bottom N Employees
    ##############################################################

    def bottom_performers(self,df):
        df=df

        top_n = self.params.gamification.leaderboard["top_n"]

        return df.tail(top_n)

    ##############################################################
    # Team Summary
    ##############################################################

    def team_summary(self,df):
        df=df
        print('team_summary',df.head(2))
        print('team_summary columns ',df.columns)

        if "assignment_group" not in df.columns:

            return pd.DataFrame()

        summary = (
            df
            .groupby("assignment_group")
            .agg(
                Employees=("assigned_to", "count"),
                Total_Points=("points", "sum"),
                Average_Level=("level", "mean"),
                Average_MTTR=("average_resolution", "mean")
            )
            .reset_index()
        )
        
        summary["Average_Level"] = summary["Average_Level"].round(2)

        summary["Average_MTTR"] = summary["Average_MTTR"].round(2)

        return summary

    ##############################################################
    # Save Results
    ##############################################################

    def lead_save(self, df):
        df=df
        print("Type of df:", type(df))
        leaderboardfile=self.config.leaderboardfile
        topfile=self.config.topfile
        bottomfile=self.config.bottomfile
        teamfile=self.config.teamfile
        groupfile=self.config.groupfile

        print('lead_board_file',df.head(2))
        print('lead_board_file columns ',df.columns)

        df.to_csv(leaderboardfile,index=False)

        self.top_performers(df).to_csv(topfile,index=False)
        self.bottom_performers(df).to_csv(bottomfile,index=False)
        self.team_summary(df).to_csv(teamfile,index=False)
        self.assignment_group_leaderboard(df).to_csv(groupfile,index=False)

        print(f"Leaderboard saved : {leaderboardfile}")
        print(f"Top performers saved : {topfile}")
        print(f"Bottom performers saved : {bottomfile}")
        print(f"Team summary saved : {teamfile}")
        print(f"Assignment Group Leaderboard : {groupfile}")

        return df
    ##############################################################
    # Achievement Calculation
    ##############################################################

    def calculate_achievements(self, df):

        print("calculate_achievements:", df.columns)
        print("##############################################################")
        print("# Achievement Calculation")
        print("##############################################################")

        # Validate required columns
        required_columns = [
            "total_incidents",
            "points",
            "average_resolution",
            "level",
            "leaderboard_rank"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns for achievement calculation: "
                f"{missing_columns}"
            )

        achievement_names = []
        achievement_count = []

        for _, row in df.iterrows():

            badges = []

            ##################################################
            # Incident Master
            ##################################################

            if row["total_incidents"] >= \
                    self.params.gamification.achievements[
                        "incident_master"
                    ]["incidents"]:

                badges.append("Incident Master")

            ##################################################
            # Point Master
            ##################################################

            if row["points"] >= \
                    self.params.gamification.achievements[
                        "point_master"
                    ]["points"]:

                badges.append("Point Master")

            ##################################################
            # SLA Champion
            ##################################################

            if "sla_percentage" in df.columns:

                if row["sla_percentage"] >= \
                        self.params.gamification.achievements[
                            "sla_champion"
                        ]["sla"]:

                    badges.append("SLA Champion")

            ##################################################
            # Speed Star
            ##################################################

            if row["average_resolution"] <= \
                    self.params.gamification.achievements[
                        "speed_star"
                    ]["mttr"]:

                badges.append("Speed Star")

            ##################################################
            # Elite Level
            ##################################################

            if row["level"] >= \
                    self.params.gamification.achievements[
                        "elite_level"
                    ]["level"]:

                badges.append("Elite Level")

            ##################################################
            # Rank Achievement
            ##################################################

            if row["leaderboard_rank"] == \
                    self.params.gamification.achievements[
                        "top_rank"
                    ]["rank"]:

                badges.append("Top Performer")

            ##################################################
            # No Achievement
            ##################################################

            if len(badges) == 0:

                badges.append("No Achievement")

            achievement_names.append(
                ", ".join(badges)
            )

            achievement_count.append(
                len(badges)
            )

        ##################################################
        # Add results to original DataFrame
        ##################################################

        df["achievements"] = achievement_names
        df["achievement_count"] = achievement_count

        return df
    ##############################################################
    # Achievement Summary
    ##############################################################

    def achievement_summary(self,df):
        df=df

        summary = (

            df

            [["assigned_to",
              "achievement_count",
              "achievements"]]

            .sort_values(

                by="achievement_count",
                ascending=False

            )

        )

        return summary

    ##############################################################
    # Save Results
    ##############################################################

    def ach_save(self, df):
        df=df
        achievementfile=self.config.achievementfile
        summaryfile=self.config.summaryfile

        if self.params.Oracle['Loader'] is None:
            df.to_csv(achievementfile,index=False)
        elif self.params.Oracle['Loader']=='Oracle':
            self.loader.run(df,'GMFNL')  
        
        df.to_csv(
            achievementfile,
            index=False
        )

        self.achievement_summary(df).to_csv(
            summaryfile,
            index=False
        )

        print(
            f"Achievement results saved : {achievementfile}"
        )

        print(
            f"Achievement summary saved : {summaryfile}"
        )

        return df

    ##############################################################
    # Generate Monthly Ranking
    ##############################################################

    def generate_monthly_ranking(self,df):
        df=df
        print('##############################################################')
        print('# Generate Monthly Ranking')
        print('##############################################################')

        if "resolved_at" not in df.columns:

            raise Exception(
                "resolved_at column is missing."
            )

        df["resolved_at"] = pd.to_datetime(df["resolved_at"])

        df["month"] = df["resolved_at"].dt.to_period("M").astype(str)

        monthly = (
            df
            .groupby(
                [
                    "month",
                    "assigned_to"
                ]
            )
            .agg(
                total_points=("points", "sum"),
                total_incidents=("number", "count"),
                average_resolution=(
                    "resolution_hours",
                    "mean"
                )
            )
            .reset_index()
        )
        monthly["average_resolution"] = (
            monthly["average_resolution"]
            .round(2)
        )

        monthly = monthly.sort_values(

            by=[
                "month",
                "total_points",
                "total_incidents"
            ],
            ascending=[
                True,
                False,
                False
            ]
        )

        monthly["monthly_rank"] = (
            monthly
            .groupby("month")
            .cumcount()
            + 1
        )

        monthly_df = monthly

        return monthly_df

    ##############################################################
    # Top N Per Month
    ##############################################################

    def m_top_performers(self,df):
        monthly_df=df
        top_n = self.params.gamification.monthly_ranking["top_n"]

        top = (

            monthly_df

            .groupby("month")

            .head(top_n)

        )

        return top

    ##############################################################
    # Monthly Summary
    ##############################################################

    def monthly_summary(self,df):
        monthly_df=df
        summary = (

            monthly_df

            .groupby("month")

            .agg(

                Employees=(

                    "assigned_to",

                    "count"

                ),

                TotalPoints=(

                    "total_points",

                    "sum"

                ),

                Incidents=(

                    "total_incidents",

                    "sum"

                )

            )

            .reset_index()

        )

        return summary

    ##############################################################
    # Save Results
    ##############################################################

    def mon_save(self,df):
        monthly_df=df
        monthlyranking=self.config.monthlyranking
        monthlytopfile =self.config.monthlytopfile
        monthlysummaryfile=self.config.monthlysummaryfile

        monthly_df.to_csv(
            monthlyranking,
            index=False
        )

        self.m_top_performers(monthly_df).to_csv(
            monthlytopfile,
            index=False
        )

        self.monthly_summary(monthly_df).to_csv(
            monthlysummaryfile,
            index=False
        )

        print(
            f"Monthly Ranking saved : {monthlyranking}"
        )

        print(
            f"Top Performers saved : {monthlytopfile}"
        )
        print(
            f"Monthly Summary saved : {monthlysummaryfile}"
        )
    
    