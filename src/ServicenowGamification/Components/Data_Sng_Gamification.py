import os 
import pandas as pd 
import numpy as np
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Config import * 
from ServicenowGamification.Entity.Config_Entity import *
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")


class Gamification: 
    def __init__(self,config:DataGamificationConfig):
        self.config=config
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        
    ##################################################################
    # Calculate Points
    ##################################################################
        

    ##################################################################
       # Calculate Points
       ##################################################################
           
   
    def calculate_points(self,df):
           df=df
           if df is None:
               df = pd.read_csv(self.config.data_path)
                
           #total_points = []

           df["total_incidents"] = (
           df.groupby("assigned_to")["number"]
              .transform("count")
              )

           if "reopen_count" in df.columns:
            df["reopen_count"] = (
                pd.to_numeric(df["reopen_count"], errors="coerce")
                .fillna(0)
                .astype(int)
            )

            if "reassignment_count" in df.columns:
                df["reassignment_count"] = (
                    pd.to_numeric(df["reassignment_count"], errors="coerce")
                    .fillna(0)
                    .astype(int)
                )

            if "customer_rating" in df.columns:
                df["customer_rating"] = (
                    pd.to_numeric(df["customer_rating"], errors="coerce")
                    .fillna(0)
                )

            #print(df[["reopen_count","reassignment_count"]].dtypes)

            total_points = []

   
           for _, row in df.iterrows():
   
               points = 0
   
               ##########################################################
               # Incident Closed
               ##########################################################
   
               if str(row["state"]).lower() == "Closed":
   
                   points += self.params.gamification.points["incident_closed"]
   
               ##########################################################
               # SLA Met
               ##########################################################
   
               if row["sla_status"] == "Met":
   
                   points += self.params.gamification.points["sla_met"]
   
               ##########################################################
               # First Call Resolution
               ##########################################################
   
               if row["fcr"] == 1:
   
                   points += self.params.gamification.points["first_call_resolution"]
   
               ##########################################################
               # High Priority Bonus
               ##########################################################
   
               if str(row["priority"]) == "1 - Critical":
   
                   points += self.params.gamification.points["high_priority_bonus"]
   
               ##########################################################
               # Customer Rating Bonus
               ##########################################################
   
               if "customer_rating" in df.columns:
   
                   if row["customer_rating"] >= 4.5:
   
                       points += self.params.gamification.points["customer_rating_bonus"]
   
               ##########################################################
               # Reopen Penalty
               ##########################################################
   
               if "reopen_count" in df.columns:
   
                   if row["reopen_count"] > 0:
   
                       points += abs(self.params.gamification.points["reopen_penalty"]) * row["reopen_count"] * -1
   
               ##########################################################
               # Reassignment Penalty
               ##########################################################
   
               if "reassignment_count" in df.columns:
   
                   if row["reassignment_count"] > 0:
   
                       points += abs(self.params.gamification.points["reassignment_penalty"]) * row["reassignment_count"] * -1
   
               total_points.append(points)
   
           df["points"] = total_points
   
           return df
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
               df.drop(columns=[
                        "average_resolution",
                        "average_resolution_y",
                        "average_resolution_x"
                        ],
                        errors="ignore",
                        inplace=True
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
   
           df_analyst_summary.to_csv(
   
               summary_path,
   
               index=False
   
           )
           
           df.to_csv(
               incident_path,
               index=False
               )
   
           print(f"Incident points saved to : {incident_path}")
   
           print(f"Analyst summary saved to : {summary_path}")
   
           return df,df_analyst_summary
              
   
    def assign_badges(self,df):
           
           print("##################################################################")
           print(f" #  Badge Assignment")
           print("##################################################################") 
           badge_list = []
   
           for _, row in df.iterrows():
               points = row["points"]
               if points >= self.params.gamification.badges["legend"]["min_points"]:
                   badge = "Legend"
               elif points >= self.params.gamification.badges["platinum"]["min_points"]:
                   badge = "Platinum"
               elif points >= self.params.gamification.badges["gold"]["min_points"]:
                   badge = "Gold"
               elif points >= self.params.gamification.badges["silver"]["min_points"]:
                   badge = "Silver"
               elif points >= self.params.gamification.badges["bronze"]["min_points"]:
                   badge = "Bronze"
               else:
                   badge = "Rookie"
   
               badge_list.append(badge)
   
           df["badge"] = badge_list
   
           print('badge columns ',df.columns)
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
   
    def calculate_level(self, df):
   
           print("##################################################################")
           print("# Calculate Level")
           print("##################################################################")
   
           level_numbers = []
           level_names = []
           next_level_points = []
           progress_percent = []
   
           # Sort levels by minimum points
           ordered_levels = sorted(
               self.params.gamification.levels.items(),
               key=lambda x: x[1]["min_points"]
           )
   
           for _, row in df.iterrows():
   
               points = row["points"]
   
               current_level = 1
               current_name = ordered_levels[0][1]["name"]
               current_min = ordered_levels[0][1]["min_points"]
               next_points = None
   
               # Find current level
               for index, (_, level) in enumerate(ordered_levels):
   
                   if points >= level["min_points"]:
   
                       current_level = index + 1
                       current_name = level["name"]
                       current_min = level["min_points"]
   
                       if index < len(ordered_levels) - 1:
                           next_points = ordered_levels[index + 1][1]["min_points"]
                       else:
                           next_points = None
   
               # Highest level
               if next_points is None:
   
                   progress = 100
                   points_remaining = 0
   
               else:
   
                   denominator = next_points - current_min
   
                   if denominator <= 0:
                       progress = 100
                   else:
                       progress = ((points - current_min) / denominator) * 100
   
                   progress = max(0, min(progress, 100))
                   points_remaining = max(0, next_points - points)
   
               level_numbers.append(current_level)
               level_names.append(current_name)
               next_level_points.append(points_remaining)
               progress_percent.append(round(progress, 2))
   
           df["level"] = level_numbers
           df["level_name"] = level_names
           df["points_to_next_level"] = next_level_points
           df["level_progress"] = progress_percent
           
   
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
   
           df["leaderboard_rank"] = df.index + 1

           # Remove existing leaderboard_rank from df_lead
           df_lead = df_lead.drop(
                columns=["leaderboard_rank"],
                errors="ignore"
            )

            # Take only required columns from leaderboard dataframe
           rank_df = (
                df[
                    [
                        "assigned_to",
                        "leaderboard_rank"
                    ]
                ]
                .drop_duplicates(
                    subset=["assigned_to"]
                )
                )

            # Add leaderboard_rank to full dataframe
           df_lead = df_lead.merge(
                rank_df,
                on="assigned_to",
                how="left")
           #df_lead = df_lead.rename(columns={"rank": "leaderboard_rank"})
           #lead_board_file=self.config.root_dir/"Leaderboardsummary.csv"
           lead_board_file = os.path.join(self.config.root_dir, "Leaderboardsummary.csv")
           print('df_lead columns',df_lead.columns)
           print("Type of df:", type(df))
           df_lead.to_csv(lead_board_file,index=False
                   )
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

           print(df)
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
   
    def monthly_summary(selfdf,df):
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
       
       