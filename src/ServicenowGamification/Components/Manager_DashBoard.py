from pathlib import Path

import pandas as pd
import numpy as np
from ServicenowGamification.Utils.Common import (
    Read_Yaml,
    create_directories
)
import csv
import os 

class ManagerDashBoard:

    def __init__(self):

        # =========================================================
        # PROJECT ROOT
        # =========================================================

        current_file = Path(__file__).resolve()

        self.project_root = current_file.parents[3]
        # =========================================================
        # PARAMS YAML
        # =========================================================

        self.params_path = (self.project_root / "params.yaml")

        if not self.params_path.exists():

            raise FileNotFoundError(
                f"params.yaml not found -> "
                f"{self.params_path}"
            )

        self.params = Read_Yaml(str(self.params_path))

        # =========================================================
        # DASHBOARD OUTPUT DIRECTORY
        # =========================================================

        self.output_dir = (
            self.project_root
            / "Artifacts"
            / "ManagerDashBorad"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def generate_live_streak_overall_level(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.rename(columns={"state": "ins_state"},inplace=True)
        df.rename(columns={"number": "number_id"},inplace=True)
        df.rename(columns={"category": "ins_category"},inplace=True)
        df.rename(columns={"priority": "ins_priority"},inplace=True)

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "opened_at",
            "sla_status",
            "fcr",
            "resolution_hours",
            "reopen_count",
            "customer_rating"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                f"Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT DATA TYPES
        # =========================================================

        df["opened_at"] = pd.to_datetime(
            df["opened_at"],
            errors="coerce"
        )

        df["fcr"] = pd.to_numeric(
            df["fcr"],
            errors="coerce"
        )

        df["resolution_hours"] = pd.to_numeric(
            df["resolution_hours"],
            errors="coerce"
        )

        df["reopen_count"] = pd.to_numeric(
            df["reopen_count"],
            errors="coerce"
        ).fillna(0)

        df["customer_rating"] = pd.to_numeric(
            df["customer_rating"],
            errors="coerce"
        )

        # =========================================================
        # CURRENT DATE
        #
        # Same as TRUNC(SYSDATE)
        # =========================================================

        today = pd.Timestamp.today().normalize()

        # =========================================================
        # CURRENT PERIOD
        #
        # Last 7 completed days
        #
        # Example:
        # Today = AUG 22
        # Current = AUG 15 - AUG 21
        # =========================================================

        current_start_date = (
            today - pd.Timedelta(days=7)
        )

        current_end_date = today

        current_df = df[
            (df["opened_at"] >= current_start_date) &
            (df["opened_at"] < current_end_date)
        ].copy()

        # =========================================================
        # PREVIOUS PERIOD
        #
        # Previous 7 completed days
        #
        # Example:
        # AUG 08 - AUG 14
        # =========================================================

        previous_start_date = (
            today - pd.Timedelta(days=14)
        )

        previous_end_date = (
            today - pd.Timedelta(days=7)
        )

        previous_df = df[
            (df["opened_at"] >= previous_start_date) &
            (df["opened_at"] < previous_end_date)
        ].copy()

        # =========================================================
        # CURRENT TOTAL INCIDENTS
        # =========================================================

        current_total_incidents = len(
            current_df
        )

        # =========================================================
        # PREVIOUS TOTAL INCIDENTS
        # =========================================================

        previous_total_incidents = len(
            previous_df
        )

        # =========================================================
        # CURRENT SLA COMPLIANCE
        # =========================================================

        if current_total_incidents == 0:

            current_sla_compliance = 0

        else:

            current_sla_compliance = round(
                (
                    current_df["sla_status"]
                    .astype(str)
                    .str.upper()
                    .eq("COMPLIANT")
                    .sum()
                    * 100
                    / current_total_incidents
                ),
                2
            )

        # =========================================================
        # PREVIOUS SLA COMPLIANCE
        # =========================================================

        if previous_total_incidents == 0:

            previous_sla_compliance = 0

        else:

            previous_sla_compliance = round(
                (
                    previous_df["sla_status"]
                    .astype(str)
                    .str.upper()
                    .eq("COMPLIANT")
                    .sum()
                    * 100
                    / previous_total_incidents
                ),
                2
            )

        # =========================================================
        # CURRENT FCR
        # =========================================================

        current_fcr = round(
            current_df["fcr"].mean(),
            2
        )

        if pd.isna(current_fcr):
            current_fcr = 0

        # =========================================================
        # PREVIOUS FCR
        # =========================================================

        previous_fcr = round(
            previous_df["fcr"].mean(),
            2
        )

        if pd.isna(previous_fcr):
            previous_fcr = 0

        # =========================================================
        # CURRENT MTTR
        #
        # SQL uses RESOLUTION_HOURS
        # =========================================================

        current_mttr_hours = round(
            current_df["resolution_hours"].mean(),
            2
        )

        if pd.isna(current_mttr_hours):
            current_mttr_hours = 0

        # =========================================================
        # PREVIOUS MTTR
        # =========================================================

        previous_mttr_hours = round(
            previous_df["resolution_hours"].mean(),
            2
        )

        if pd.isna(previous_mttr_hours):
            previous_mttr_hours = 0

        # =========================================================
        # CURRENT REOPEN RATE
        # =========================================================

        if current_total_incidents == 0:

            current_reopen_rate = 0

        else:

            current_reopen_rate = round(
                (
                    (
                        current_df["reopen_count"] > 0
                    ).sum()
                    * 100
                    / current_total_incidents
                ),
                2
            )

        # =========================================================
        # PREVIOUS REOPEN RATE
        # =========================================================

        if previous_total_incidents == 0:

            previous_reopen_rate = 0

        else:

            previous_reopen_rate = round(
                (
                    (
                        previous_df["reopen_count"] > 0
                    ).sum()
                    * 100
                    / previous_total_incidents
                ),
                2
            )

        # =========================================================
        # CURRENT CUSTOMER RATING
        # =========================================================

        current_customer_rating = round(
            current_df["customer_rating"].mean(),
            2
        )

        if pd.isna(current_customer_rating):
            current_customer_rating = 0

        # =========================================================
        # PREVIOUS CUSTOMER RATING
        # =========================================================

        previous_customer_rating = round(
            previous_df["customer_rating"].mean(),
            2
        )

        if pd.isna(previous_customer_rating):
            previous_customer_rating = 0

        # =========================================================
        # PERCENTAGE CHANGE FUNCTION
        # =========================================================

        def calculate_percentage_change(
            current_value,
            previous_value
        ):

            if previous_value == 0:

                if current_value == 0:
                    return "0.00% from last 7 days"

                return "+100.00% from last 7 days"

            percentage = round(
                (
                    (current_value - previous_value)
                    * 100
                    / previous_value
                ),
                2
            )

            sign = ""

            if current_value > previous_value:
                sign = "+"

            return (
                f"{sign}{percentage:.2f}% "
                f"from last 7 days"
            )

        # =========================================================
        # DATE RANGE
        # =========================================================

        current_date_range = (
            "vs "
            + current_start_date.strftime(
                "%b %d"
            ).upper()
            + " - "
            + (
                today - pd.Timedelta(days=1)
            ).strftime(
                "%b %d"
            ).upper()
        )

        previous_date_range = (
            "vs "
            + previous_start_date.strftime(
                "%b %d"
            ).upper()
            + " - "
            + (
                previous_end_date
                - pd.Timedelta(days=1)
            ).strftime(
                "%b %d"
            ).upper()
        )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        result = pd.DataFrame([{

            "CURRENT_DATE_RANGE":
                current_date_range,

            "PREVIOUS_DATE_RANGE":
                previous_date_range,

            # -----------------------------------------------------
            # TOTAL INCIDENTS
            # -----------------------------------------------------

            "CURRENT_TOTAL_INCIDENTS":
                current_total_incidents,

            "PREVIOUS_TOTAL_INCIDENTS":
                previous_total_incidents,

            "INCIDENTS_PCT_CHANGE":
                calculate_percentage_change(
                    current_total_incidents,
                    previous_total_incidents
                ),

            # -----------------------------------------------------
            # SLA COMPLIANCE
            # -----------------------------------------------------

            "CURRENT_SLA_COMPLIANCE":
                current_sla_compliance,

            "PREVIOUS_SLA_COMPLIANCE":
                previous_sla_compliance,

            "SLA_COMPLIANCE_PCT_CHANGE":
                calculate_percentage_change(
                    current_sla_compliance,
                    previous_sla_compliance
                ),

            # -----------------------------------------------------
            # FCR
            # -----------------------------------------------------

            "CURRENT_FCR":
                current_fcr,

            "PREVIOUS_FCR":
                previous_fcr,

            "FCR_PCT_CHANGE":
                calculate_percentage_change(
                    current_fcr,
                    previous_fcr
                ),

            # -----------------------------------------------------
            # MTTR
            # -----------------------------------------------------

            "CURRENT_MTTR_HOURS":
                current_mttr_hours,

            "PREVIOUS_MTTR_HOURS":
                previous_mttr_hours,

            "MTTR_PCT_CHANGE":
                calculate_percentage_change(
                    current_mttr_hours,
                    previous_mttr_hours
                ),

            # -----------------------------------------------------
            # REOPEN RATE
            # -----------------------------------------------------

            "CURRENT_REOPEN_RATE":
                current_reopen_rate,

            "PREVIOUS_REOPEN_RATE":
                previous_reopen_rate,

            "REOPEN_RATE_PCT_CHANGE":
                calculate_percentage_change(
                    current_reopen_rate,
                    previous_reopen_rate
                ),

            # -----------------------------------------------------
            # CUSTOMER RATING
            # -----------------------------------------------------

            "CURRENT_CUSTOMER_RATING":
                current_customer_rating,

            "PREVIOUS_CUSTOMER_RATING":
                previous_customer_rating,

            "CUSTOMER_RATING_PCT_CHANGE":
                calculate_percentage_change(
                    current_customer_rating,
                    previous_customer_rating
                )
        }])

        # =========================================================
        # OUTPUT PATH
        # =========================================================

        output_file = (
            self.output_dir
            / "Live_Streak_Overall_Level.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def generate_manager_incidents_over_time(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)
        df.rename(columns={"state": "ins_state"},inplace=True)
        df.rename(columns={"number": "number_id"},inplace=True)
        df.rename(columns={"category": "ins_category"},inplace=True)
        df.rename(columns={"priority": "ins_priority"},inplace=True)
        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "opened_at",
            "number_id"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                f"Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT opened_at TO DATETIME
        # =========================================================

        df["opened_at"] = pd.to_datetime(
            df["opened_at"],
            errors="coerce"
        )

        # =========================================================
        # REMOVE NULL opened_at
        #
        # Equivalent to:
        # WHERE opened_at IS NOT NULL
        # =========================================================

        df = df[
            df["opened_at"].notna()
        ].copy()

        # =========================================================
        # INCIDENT DATE
        #
        # Equivalent to:
        # TRUNC(opened_at)
        # =========================================================

        df["incident_date"] = (
            df["opened_at"]
            .dt.normalize()
        )

        # =========================================================
        # INCIDENT COUNT
        #
        # Equivalent to:
        # COUNT(number_id)
        # GROUP BY TRUNC(opened_at)
        # =========================================================

        result = (
            df.groupby(
                "incident_date",
                as_index=False
            )["number_id"]
            .count()
            .rename(
                columns={
                    "number_id": "incident_count"
                }
            )
        )

        # =========================================================
        # ORDER BY incident_date
        # =========================================================

        result = (
            result
            .sort_values(
                "incident_date"
            )
            .reset_index(drop=True)
        )

        # =========================================================
        # OUTPUT PATH
        # =========================================================

        output_file = (
            self.output_dir
            / "Manager_Incidents_Over_Time_02.csv"
        )

        # =========================================================
        # SAVE RESULT
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def generate_manager_sla_trend_overall(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)

        df.rename(columns={"number": "number_id"},inplace=True)
        df.rename(columns={"category": "ins_category"},inplace=True)
        df.rename(columns={"priority": "ins_priority"},inplace=True)

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "resolved_at",
            "sla_status"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                f"Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT RESOLVED_AT TO DATETIME
        # =========================================================

        df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")

        # =========================================================
        # REMOVE NULL RESOLVED_AT
        # Oracle:
        # WHERE resolved_at IS NOT NULL
        # =========================================================

        df = df[df["resolved_at"].notna()].copy()

        # =========================================================
        # CREATE WEEK START
        #
        # Oracle:
        # TRUNC(resolved_at, 'IW')
        #
        # 'IW' = Monday as the beginning of the week
        # =========================================================

        df["week_start"] = (
            df["resolved_at"]
            - pd.to_timedelta(
                df["resolved_at"].dt.weekday,
                unit="D"
            )
        ).dt.normalize()

        # =========================================================
        # CREATE WEEK LABEL
        #
        # Oracle:
        # TO_CHAR(TRUNC(resolved_at, 'IW'), 'Mon DD')
        # =========================================================

        df["week_label"] = (
            df["week_start"]
            .dt.strftime("%b %d")
            .str.title()
        )

        # =========================================================
        # NORMALIZE SLA STATUS
        # =========================================================

        df["sla_status_clean"] = (
            df["sla_status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # =========================================================
        # SLA COMPLIANCE FLAG
        #
        # Oracle:
        # MET
        # COMPLIANT
        # PASSED
        # PASS
        # =========================================================

        compliant_status = [
            "MET",
            "COMPLIANT",
            "PASSED",
            "PASS"
        ]

        df["sla_compliant"] = (
            df["sla_status_clean"]
            .isin(compliant_status)
            .astype(int)
        )

        # =========================================================
        # GROUP BY WEEK
        # =========================================================

        result = (
            df.groupby(
                [
                    "week_start",
                    "week_label"
                ],
                as_index=False
            )
            .agg(
                incident_count=(
                    "sla_status",
                    "size"
                ),
                sla_compliance=(
                    "sla_compliant",
                    "mean"
                )
            )
        )

        # =========================================================
        # CONVERT SLA COMPLIANCE TO PERCENTAGE
        #
        # Oracle:
        # 100 * SUM(compliant) / COUNT(*)
        # =========================================================

        result["sla_compliance"] = (
            result["sla_compliance"] * 100
        ).round(2)

        # =========================================================
        # SORT BY WEEK
        #
        # Oracle:
        # ORDER BY week_start
        # =========================================================

        result = (
            result
            .sort_values(
                "week_start"
            )
            .reset_index(drop=True)
        )

        # =========================================================
        # FINAL COLUMN ORDER
        # =========================================================

        result = result[
            [
                "week_start",
                "week_label",
                "incident_count",
                "sla_compliance"
            ]
        ]

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "Manager_SLA_Trend_Overall_04.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def generate_manager_incident_by_state(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMN
        # =========================================================

        required_columns = [
            "ins_state"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                f"Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CLEAN STATE
        # =========================================================

        df["ins_state"] = (
            df["ins_state"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # STATE COUNT
        # =========================================================

        state_summary = (
            df.groupby(
                "ins_state",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "state_count"
                }
            )
        )

        # =========================================================
        # TOTAL INCIDENTS
        # =========================================================

        total_incidents = state_summary["state_count"].sum()

        # =========================================================
        # STATE PERCENTAGE
        # =========================================================

        if total_incidents == 0:

            state_summary["state_percentage"] = 0.00

        else:

            state_summary["state_percentage"] = (
                state_summary["state_count"]
                * 100
                / total_incidents
            ).round(2)

        # =========================================================
        # CREATE STATE(%)
        #
        # Example:
        # Open     25(41.67 %)
        # Resolved 20(33.33 %)
        # Closed   15(25.00 %)
        # =========================================================

        state_summary["State(%)"] = (
            state_summary["state_count"]
            .astype(str)
            + "("
            + state_summary["state_percentage"]
            .map(lambda x: f"{x:.2f}")
            + " %)"
        )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        result = state_summary[
            [
                "ins_state",
                "State(%)"
            ]
        ].copy()

        # =========================================================
        # RENAME FOR OUTPUT
        # =========================================================

        result.rename(
            columns={
                "ins_state": "INS_STATE"
            },
            inplace=True
        )

        # =========================================================
        # SORT BY STATE
        # =========================================================

        result.sort_values(
            by="INS_STATE",
            inplace=True
        )

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "Manager_INCIDENT_BY_STATE_03.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def insert_agent_level_fcr_data(self):

        # =========================================================
        # INPUT FILES
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        fcr = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelFCR.csv"
        )

        # =========================================================
        # READ INPUT FILES
        # =========================================================

        try:
            incident_df = pd.read_csv(
                incident,
                encoding="utf-8"
            )

            fcr_df = pd.read_csv(
                fcr,
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            incident_df = pd.read_csv(
                incident,
                encoding="latin1"
            )

            fcr_df = pd.read_csv(
                fcr,
                encoding="latin1"
            )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        incident_df.columns = (
            incident_df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        fcr_df.columns = (
            fcr_df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME INCIDENT COLUMNS
        # =========================================================

        incident_df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE INCIDENT COLUMNS
        # =========================================================

        required_incident_columns = [
            "assigned_to",
            "opened_at",
            "fcr",
            "number_id"
        ]

        missing_incident_columns = [
            col
            for col in required_incident_columns
            if col not in incident_df.columns
        ]

        if missing_incident_columns:
            raise KeyError(
                "Missing columns in AchievementResults.csv: "
                f"{missing_incident_columns}"
            )

        # =========================================================
        # VALIDATE FCR COLUMNS
        # =========================================================

        required_fcr_columns = [
            "agent",
            "total_incidents",
            "fcr_percentage"
        ]

        missing_fcr_columns = [
            col
            for col in required_fcr_columns
            if col not in fcr_df.columns
        ]

        if missing_fcr_columns:
            raise KeyError(
                "Missing columns in AgentLevelFCR.csv: "
                f"{missing_fcr_columns}"
            )

        # =========================================================
        # CLEAN INCIDENT DATA
        # =========================================================

        incident_df["assigned_to"] = (
            incident_df["assigned_to"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        incident_df["opened_at"] = pd.to_datetime(
            incident_df["opened_at"],
            errors="coerce"
        )

        incident_df["fcr"] = pd.to_numeric(
            incident_df["fcr"],
            errors="coerce"
        )

        incident_df = incident_df[
            incident_df["assigned_to"].ne("Unknown")
            & incident_df["opened_at"].notna()
        ].copy()

        # =========================================================
        # CURRENT MONTH
        # =========================================================

        today = pd.Timestamp.today()

        current_month_start = pd.Timestamp(
            year=today.year,
            month=today.month,
            day=1
        )

        next_month_start = (
            current_month_start
            + pd.offsets.MonthBegin(1)
        )

        current_month_df = incident_df[
            (incident_df["opened_at"] >= current_month_start)
            &
            (incident_df["opened_at"] < next_month_start)
        ].copy()

        # =========================================================
        # CURRENT MONTH FCR
        # =========================================================

        if current_month_df.empty:

            current_month_fcr = pd.DataFrame(
                columns=[
                    "agent_key",
                    "current_fcr"
                ]
            )

        else:

            current_month_fcr = (
                current_month_df
                .groupby("assigned_to")
                .agg(
                    total_incidents=(
                        "number_id",
                        "count"
                    ),
                    fcr_count=(
                        "fcr",
                        lambda x: (x == 1).sum()
                    )
                )
                .reset_index()
            )

            current_month_fcr["current_fcr"] = (
                current_month_fcr["fcr_count"]
                * 100
                / current_month_fcr[
                    "total_incidents"
                ].replace(0, np.nan)
            ).round(2)

            current_month_fcr["agent_key"] = (
                current_month_fcr["assigned_to"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            current_month_fcr = current_month_fcr[
                [
                    "agent_key",
                    "current_fcr"
                ]
            ]

        # =========================================================
        # PREVIOUS MONTH
        # =========================================================

        previous_month_start = (
            current_month_start
            - pd.offsets.MonthBegin(1)
        )

        previous_month_df = incident_df[
            (incident_df["opened_at"] >= previous_month_start)
            &
            (incident_df["opened_at"] < current_month_start)
        ].copy()

        # =========================================================
        # PREVIOUS MONTH FCR
        # =========================================================

        if previous_month_df.empty:

            previous_month_fcr = pd.DataFrame(
                columns=[
                    "agent_key",
                    "previous_fcr"
                ]
            )

        else:

            previous_month_fcr = (
                previous_month_df
                .groupby("assigned_to")
                .agg(
                    total_incidents=(
                        "number_id",
                        "count"
                    ),
                    fcr_count=(
                        "fcr",
                        lambda x: (x == 1).sum()
                    )
                )
                .reset_index()
            )

            previous_month_fcr["previous_fcr"] = (
                previous_month_fcr["fcr_count"]
                * 100
                / previous_month_fcr[
                    "total_incidents"
                ].replace(0, np.nan)
            ).round(2)

            previous_month_fcr["agent_key"] = (
                previous_month_fcr["assigned_to"]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            previous_month_fcr = previous_month_fcr[
                [
                    "agent_key",
                    "previous_fcr"
                ]
            ]

        # =========================================================
        # NORMALIZE FCR AGENT
        # =========================================================

        fcr_df["agent"] = (
            fcr_df["agent"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        fcr_df["agent_key"] = (
            fcr_df["agent"]
            .str.upper()
        )

        # =========================================================
        # LEFT JOIN CURRENT MONTH
        # =========================================================

        result = fcr_df[
            [
                "agent",
                "total_incidents",
                "fcr_percentage",
                "agent_key"
            ]
        ].copy()

        result = result.merge(
            current_month_fcr,
            on="agent_key",
            how="left"
        )

        # =========================================================
        # LEFT JOIN PREVIOUS MONTH
        # =========================================================

        result = result.merge(
            previous_month_fcr,
            on="agent_key",
            how="left"
        )

        # =========================================================
        # CALCULATE FCR TREND
        # =========================================================

        def calculate_trend(row):

            current = row["current_fcr"]
            previous = row["previous_fcr"]

            if pd.isna(current) or pd.isna(previous):
                return "0%"

            difference = round(
                current - previous,
                2
            )

            if difference > 0:
                return f"▲ {difference:.2f}%"

            if difference < 0:
                return f"▼ {abs(difference):.2f}%"

            return "0%"

            if difference < 0:
                return f"▼ {abs(difference):.2f}%"

            return "— 0%"

        result["trend"] = result.apply(
            calculate_trend,
            axis=1
        )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        result = result[
            [
                "agent",
                "fcr_percentage",
                "total_incidents",
                "trend"
            ]
        ].copy()

        # =========================================================
        # RENAME OUTPUT COLUMNS
        # =========================================================

        result.rename(
            columns={
                "fcr_percentage": "FCR (%)",
                "total_incidents": "incidents"
            },
            inplace=True
        )

        # =========================================================
        # CLEAN FCR PERCENTAGE
        # =========================================================

        result["FCR (%)"] = (
            result["FCR (%)"]
            .astype(str)
            .str.replace(
                "%",
                "",
                regex=False
            )
        )

        result["FCR (%)"] = pd.to_numeric(
            result["FCR (%)"],
            errors="coerce"
        ).round(2)

        result["incidents"] = pd.to_numeric(
            result["incidents"],
            errors="coerce"
        )

        # =========================================================
        # SORT BY FCR DESCENDING
        # =========================================================

        result.sort_values(
            by="FCR (%)",
            ascending=False,
            inplace=True
        )

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # TOP 5 AGENTS
        # =========================================================

        result = result.head(5)

        # =========================================================
        # OUTPUT DIRECTORY
        # =========================================================

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "MANAGER_AGENTS_BY_FCR_TRENDS_05.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False,
            encoding="utf-8"
        )

        # =========================================================
        # VALIDATE OUTPUT
        # =========================================================

        if not output_file.exists():
            raise FileNotFoundError(
                f"Output file was not generated: "
                f"{output_file}"
            )


    def generate_manager_avg_by_priority(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        # =========================================================
        # READ INPUT FILE
        # =========================================================

        df = pd.read_csv(
            incident,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "ins_priority",
            "opened_at",
            "resolved_at"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT DATE COLUMNS
        # =========================================================

        df["opened_at"] = pd.to_datetime(
            df["opened_at"],
            errors="coerce"
        )

        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce"
        )

        # =========================================================
        # REMOVE INVALID RECORDS
        # =========================================================

        df = df[
            df["opened_at"].notna()
            & df["resolved_at"].notna()
        ].copy()

        # =========================================================
        # CALCULATE MTTR HOURS
        # =========================================================

        df["mttr_hours"] = (
            df["resolved_at"]
            - df["opened_at"]
        ).dt.total_seconds() / 3600

        # =========================================================
        # REMOVE INVALID MTTR VALUES
        # =========================================================

        df = df[
            df["mttr_hours"].notna()
            & (df["mttr_hours"] >= 0)
        ].copy()

        # =========================================================
        # AVERAGE MTTR BY PRIORITY
        # =========================================================

        result = (
            df.groupby(
                "ins_priority",
                as_index=False
            )
            .agg(
                avg_mttr_hours=(
                    "mttr_hours",
                    "mean"
                )
            )
        )

        # =========================================================
        # ROUND MTTR
        # =========================================================

        result["avg_mttr_hours"] = (
            result["avg_mttr_hours"]
            .round(2)
        )

        # =========================================================
        # RENAME OUTPUT COLUMNS
        # =========================================================

        result.rename(
            columns={
                "ins_priority": "INS_PRIORITY",
                "avg_mttr_hours": "AVG_MTTR_HOURS"
            },
            inplace=True
        )

        # =========================================================
        # SORT BY PRIORITY
        # =========================================================

        result.sort_values(
            by="INS_PRIORITY",
            inplace=True
        )

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (self.output_dir/ "MANAGER_AVG_BY_PRIORITY_06.csv" )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def generate_manager_sla_by_priority(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        # =========================================================
        # READ INPUT FILE
        # =========================================================

        df = pd.read_csv(
            incident,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "ins_priority",
            "opened_at",
            "resolved_at"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT DATE COLUMNS
        # =========================================================

        df["opened_at"] = pd.to_datetime(
            df["opened_at"],
            errors="coerce"
        )

        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce"
        )

        # =========================================================
        # CLEAN PRIORITY
        # =========================================================

        df["ins_priority"] = (
            df["ins_priority"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # REMOVE INVALID RECORDS
        # =========================================================

        df = df[
            df["opened_at"].notna()
            & df["resolved_at"].notna()
        ].copy()

        # =========================================================
        # EXTRACT PRIORITY NUMBER
        # Example:
        # 1 - Critical  -> 1
        # 2 - High      -> 2
        # 3 - Moderate  -> 3
        # 4 - Low       -> 4
        # 5 - Planned   -> 5
        # =========================================================

        df["priority_number"] = pd.to_numeric(
            df["ins_priority"]
            .str.extract(r"^(\d+)")[0],
            errors="coerce"
        )

        # =========================================================
        # CALCULATE RESOLUTION HOURS
        # =========================================================

        df["resolution_hours"] = (
            df["resolved_at"]
            - df["opened_at"]
        ).dt.total_seconds() / 3600

        # =========================================================
        # SLA TARGET HOURS
        # =========================================================

        sla_targets = {
            1: 4,
            2: 8,
            3: 24,
            4: 48,
            5: 48
        }

        df["sla_target_hours"] = (
            df["priority_number"]
            .map(sla_targets)
        )

        # =========================================================
        # SLA COMPLIANCE
        # =========================================================

        df["sla_compliant"] = (
            df["resolution_hours"]
            <= df["sla_target_hours"]
        )

        # =========================================================
        # GROUP BY PRIORITY
        # =========================================================

        result = (
            df.groupby(
                [
                    "ins_priority",
                    "priority_number"
                ],
                as_index=False
            )
            .agg(
                total_incidents=(
                    "ins_priority",
                    "size"
                ),
                sla_compliant_incidents=(
                    "sla_compliant",
                    "sum"
                )
            )
        )

        # =========================================================
        # SLA COMPLIANCE PERCENTAGE
        # =========================================================

        result["sla_compliance_percentage"] = (
            result["sla_compliant_incidents"]
            * 100
            / result["total_incidents"]
        ).round(2)

        # =========================================================
        # ADD % SYMBOL
        # =========================================================

        result["sla_compliance_percentage"] = (
            result["sla_compliance_percentage"]
            .map(
                lambda x: f"{x:.2f}%"
            )
        )

        # =========================================================
        # FINAL COLUMNS
        # =========================================================

        result = result[
            [
                "ins_priority",
                "total_incidents",
                "sla_compliant_incidents",
                "sla_compliance_percentage"
            ]
        ].copy()

        # =========================================================
        # RENAME OUTPUT COLUMNS
        # =========================================================

        result.rename(
            columns={
                "ins_priority": "INS_PRIORITY",
                "total_incidents": "TOTAL_INCIDENTS",
                "sla_compliant_incidents":
                    "SLA_COMPLIANT_INCIDENTS",
                "sla_compliance_percentage":
                    "SLA_COMPLIANCE_PERCENTAGE"
            },
            inplace=True
        )

        # =========================================================
        # SORT BY PRIORITY
        # =========================================================

        result["priority_number"] = pd.to_numeric(
            result["INS_PRIORITY"]
            .str.extract(r"^(\d+)")[0],
            errors="coerce"
        )

        result.sort_values(
            by="priority_number",
            inplace=True
        )

        result.drop(
            columns=["priority_number"],
            inplace=True
        )

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "MANAGER_SLA_BY_PRIORITY_08.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )            

    def generate_manager_recent_alert(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        # =========================================================
        # READ INPUT FILE
        # =========================================================

        df = pd.read_csv(
            incident,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "number_id",
            "ins_priority",
            "reopen_count",
            "opened_at",
            "resolved_at"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in AchievementResults.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CONVERT DATE COLUMNS
        # =========================================================

        df["opened_at"] = pd.to_datetime(
            df["opened_at"],
            errors="coerce"
        )

        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce"
        )

        # =========================================================
        # CLEAN PRIORITY
        # =========================================================

        df["ins_priority"] = (
            df["ins_priority"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # CLEAN REOPEN COUNT
        # =========================================================

        df["reopen_count"] = pd.to_numeric(
            df["reopen_count"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # REMOVE INVALID RECORDS
        # Open incidents are retained
        # =========================================================

        df = df[
            df["opened_at"].notna()
        ].copy()

        # =========================================================
        # EXTRACT PRIORITY NUMBER
        # =========================================================

        df["priority_number"] = pd.to_numeric(
            df["ins_priority"]
            .str.extract(r"^(\d+)")[0],
            errors="coerce"
        )

        # =========================================================
        # SLA TARGET HOURS
        # =========================================================

        sla_targets = {
            1: 4,
            2: 8,
            3: 24,
            4: 48,
            5: 48
        }

        df["sla_threshold_hours"] = (
            df["priority_number"]
            .map(sla_targets)
        )

        # =========================================================
        # CALCULATE DURATION HOURS
        # Resolved = resolved_at - opened_at
        # Open = current time - opened_at
        # =========================================================

        current_time = pd.Timestamp.now()

        df["duration_hours"] = (
            df["resolved_at"]
            .fillna(current_time)
            - df["opened_at"]
        ).dt.total_seconds() / 3600

        # =========================================================
        # RESOLVED / OPEN FLAGS
        # =========================================================

        df["resolved_flag"] = (
            df["resolved_at"].notna()
        ).astype(int)

        df["open_flag"] = (
            df["resolved_at"].isna()
        ).astype(int)

        # =========================================================
        # REOPEN FLAG
        # =========================================================

        df["reopened_flag"] = (
            df["reopen_count"] > 0
        ).astype(int)

        # =========================================================
        # INCIDENT DATE
        # =========================================================

        df["incident_date"] = (
            df["opened_at"]
            .dt.normalize()
        )

        # =========================================================
        # SLA BREACH FLAG
        # =========================================================

        df["sla_breached_flag"] = (
            df["duration_hours"]
            > df["sla_threshold_hours"]
        ).astype(int)

        # =========================================================
        # P1/P2 AGING FLAG
        # =========================================================

        df["aging_flag"] = (
            df["priority_number"].isin([1, 2])
            & (df["open_flag"] == 1)
            & (
                df["duration_hours"]
                > df["sla_threshold_hours"]
            )
        ).astype(int)

        # =========================================================
        # CONFIGURATION
        # =========================================================

        sla_target_percentage = 90
        reopen_rate_threshold = 14
        volume_increase_threshold = 20
        resolution_drop_threshold = 20
        high_duration_multiplier = 2
        p1p2_volume_threshold = 3

        # =========================================================
        # DAILY PRIORITY METRICS
        # =========================================================

        priority_groups = []

        for (
            incident_date,
            ins_priority,
            priority_number,
            sla_threshold_hours
        ), group in df.groupby(
            [
                "incident_date",
                "ins_priority",
                "priority_number",
                "sla_threshold_hours"
            ],
            dropna=False
        ):

            resolved_incidents = (
                group["resolved_flag"].sum()
            )

            total_incidents = len(group)

            sla_breached_incidents = (
                group["sla_breached_flag"].sum()
            )

            sla_compliance = (
                (
                    resolved_incidents
                    - group.loc[
                        group["resolved_flag"] == 1,
                        "sla_breached_flag"
                    ].sum()
                )
                * 100
                / resolved_incidents
                if resolved_incidents > 0
                else np.nan
            )

            priority_groups.append(
                {
                    "incident_date": incident_date,
                    "ins_priority": ins_priority,
                    "priority_number": priority_number,
                    "sla_threshold_hours":
                        sla_threshold_hours,
                    "total_incidents":
                        total_incidents,
                    "resolved_incidents":
                        resolved_incidents,
                    "open_incidents":
                        group["open_flag"].sum(),
                    "reopened_incidents":
                        group["reopened_flag"].sum(),
                    "sla_breached_incidents":
                        sla_breached_incidents,
                    "aging_incidents":
                        group["aging_flag"].sum(),
                    "avg_mttr_hours":
                        group.loc[
                            group["resolved_flag"] == 1,
                            "duration_hours"
                        ].mean(),
                    "max_duration_hours":
                        group["duration_hours"].max(),
                    "avg_duration_hours":
                        group["duration_hours"].mean(),
                    "sla_compliance_percentage":
                        sla_compliance,
                    "reopen_rate":
                        group["reopened_flag"].sum()
                        * 100
                        / total_incidents
                        if total_incidents > 0
                        else 0
                }
            )

        daily_priority_metrics = pd.DataFrame(
            priority_groups
        )

        if not daily_priority_metrics.empty:

            daily_priority_metrics[
                "avg_mttr_hours"
            ] = daily_priority_metrics[
                "avg_mttr_hours"
            ].round(2)

            daily_priority_metrics[
                "max_duration_hours"
            ] = daily_priority_metrics[
                "max_duration_hours"
            ].round(2)

            daily_priority_metrics[
                "avg_duration_hours"
            ] = daily_priority_metrics[
                "avg_duration_hours"
            ].round(2)

            daily_priority_metrics[
                "sla_compliance_percentage"
            ] = daily_priority_metrics[
                "sla_compliance_percentage"
            ].round(2)

            daily_priority_metrics[
                "reopen_rate"
            ] = daily_priority_metrics[
                "reopen_rate"
            ].round(2)

        # =========================================================
        # DAILY OVERALL METRICS
        # =========================================================

        daily_overall_metrics = (
            df.groupby(
                "incident_date",
                as_index=False
            )
            .agg(
                total_incidents=(
                    "number_id",
                    "size"
                ),
                resolved_incidents=(
                    "resolved_flag",
                    "sum"
                ),
                open_incidents=(
                    "open_flag",
                    "sum"
                ),
                reopened_incidents=(
                    "reopened_flag",
                    "sum"
                ),
                sla_breached_incidents=(
                    "sla_breached_flag",
                    "sum"
                )
            )
        )

        # =========================================================
        # P1/P2 DAILY METRICS
        # =========================================================

        p1p2_df = df[
            df["priority_number"].isin([1, 2])
        ].copy()

        p1p2_metrics = (
            p1p2_df.groupby(
                "incident_date",
                as_index=False
            )
            .agg(
                p1p2_incidents=(
                    "number_id",
                    "size"
                )
            )
        )

        open_p1p2_metrics = (
            p1p2_df[
                p1p2_df["open_flag"] == 1
            ]
            .groupby(
                "incident_date",
                as_index=False
            )
            .agg(
                open_p1p2_incidents=(
                    "number_id",
                    "size"
                )
            )
        )

        daily_overall_metrics = (
            daily_overall_metrics
            .merge(
                p1p2_metrics,
                on="incident_date",
                how="left"
            )
            .merge(
                open_p1p2_metrics,
                on="incident_date",
                how="left"
            )
        )

        daily_overall_metrics[
            "p1p2_incidents"
        ] = daily_overall_metrics[
            "p1p2_incidents"
        ].fillna(0)

        daily_overall_metrics[
            "open_p1p2_incidents"
        ] = daily_overall_metrics[
            "open_p1p2_incidents"
        ].fillna(0)

        # =========================================================
        # PREVIOUS DAY COMPARISON
        # =========================================================

        daily_comparison = (
            daily_overall_metrics.copy()
        )

        previous_metrics = (
            daily_overall_metrics[
                [
                    "incident_date",
                    "total_incidents",
                    "resolved_incidents"
                ]
            ]
            .copy()
        )

        previous_metrics["incident_date"] = (
            previous_metrics["incident_date"]
            + pd.Timedelta(days=1)
        )

        previous_metrics.rename(
            columns={
                "total_incidents":
                    "previous_total_incidents",
                "resolved_incidents":
                    "previous_resolved_incidents"
            },
            inplace=True
        )

        daily_comparison = (
            daily_comparison
            .merge(
                previous_metrics,
                on="incident_date",
                how="left"
            )
        )

        # =========================================================
        # ALERT LIST
        # =========================================================

        alerts = []

        # =========================================================
        # INCIDENT DETAILS FUNCTION
        # =========================================================

        def get_incident_details(
            incident_date,
            condition=None,
            sort_by="duration_hours",
            ascending=False
        ):

            temp = df[
                df["incident_date"] == incident_date
            ].copy()

            if condition is not None:
                temp = temp[
                    condition(temp)
                ]

            if temp.empty:
                return None

            temp = temp.sort_values(
                by=sort_by,
                ascending=ascending
            )

            incident_numbers = (
                temp["number_id"]
                .astype(str)
                .tolist()
            )

            if len(incident_numbers) > 20:
                return (
                    ", ".join(
                        incident_numbers[:20]
                    )
                    + f", ... ({len(incident_numbers) - 20} more)"
                )

            return ", ".join(
                incident_numbers
            )

        # =========================================================
        # PRIORITY ALERTS
        # =========================================================

        for _, row in daily_priority_metrics.iterrows():

            # =====================================================
            # 1. HIGH MTTR
            # =====================================================

            if (
                pd.notna(row["avg_mttr_hours"])
                and row["avg_mttr_hours"]
                > row["sla_threshold_hours"]
            ):

                alerts.append(
                    {
                        "alert_type": "HIGH",
                        "alert_title":
                            f"High MTTR for "
                            f"{row['ins_priority']} incidents",
                        "alert_message":
                            f"Average MTTR is "
                            f"{row['avg_mttr_hours']:.2f} hours; "
                            f"target is "
                            f"{row['sla_threshold_hours']:.2f} hours",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    (
                                        x["ins_priority"]
                                        == row["ins_priority"]
                                    )
                                    & (
                                        x["resolved_flag"] == 1
                                    )
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration":
                            row["avg_mttr_hours"],
                        "priority":
                            row["priority_number"],
                        "metric_value":
                            row["avg_mttr_hours"],
                        "threshold_value":
                            row["sla_threshold_hours"]
                    }
                )

            # =====================================================
            # 2. LOW SLA COMPLIANCE
            # =====================================================

            if (
                pd.notna(
                    row["sla_compliance_percentage"]
                )
                and row["sla_compliance_percentage"]
                < sla_target_percentage
            ):

                alerts.append(
                    {
                        "alert_type": "WARNING",
                        "alert_title":
                            f"Low SLA Compliance for "
                            f"{row['ins_priority']}",
                        "alert_message":
                            f"SLA compliance is "
                            f"{row['sla_compliance_percentage']:.2f}%; "
                            f"target is "
                            f"{sla_target_percentage}%",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    (
                                        x["ins_priority"]
                                        == row["ins_priority"]
                                    )
                                    & (
                                        x["sla_breached_flag"] == 1
                                    )
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration":
                            row["max_duration_hours"],
                        "priority":
                            row["priority_number"],
                        "metric_value":
                            row["sla_compliance_percentage"],
                        "threshold_value":
                            sla_target_percentage
                    }
                )

            # =====================================================
            # 3. HIGH REOPEN RATE
            # =====================================================

            if (
                pd.notna(row["reopen_rate"])
                and row["reopen_rate"]
                > reopen_rate_threshold
            ):

                alerts.append(
                    {
                        "alert_type": "MEDIUM",
                        "alert_title":
                            f"High Reopen Rate for "
                            f"{row['ins_priority']}",
                        "alert_message":
                            f"Reopen rate is "
                            f"{row['reopen_rate']:.2f}%; "
                            f"threshold is "
                            f"{reopen_rate_threshold}%",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    (
                                        x["ins_priority"]
                                        == row["ins_priority"]
                                    )
                                    & (
                                        x["reopened_flag"] == 1
                                    )
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration":
                            row["max_duration_hours"],
                        "priority":
                            row["priority_number"],
                        "metric_value":
                            row["reopen_rate"],
                        "threshold_value":
                            reopen_rate_threshold
                    }
                )

            # =====================================================
            # 4. P1/P2 AGING INCIDENTS
            # =====================================================

            if (
                row["aging_incidents"] > 0
                and row["priority_number"] in [1, 2]
            ):

                alerts.append(
                    {
                        "alert_type": "HIGH",
                        "alert_title":
                            "P1/P2 Aging Incidents",
                        "alert_message":
                            f"{int(row['aging_incidents'])} "
                            f"P1/P2 incidents are beyond SLA",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    x["priority_number"].isin(
                                        [1, 2]
                                    )
                                    & (
                                        x["aging_flag"] == 1
                                    )
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration":
                            row["max_duration_hours"],
                        "priority":
                            row["priority_number"],
                        "metric_value":
                            row["aging_incidents"],
                        "threshold_value": 0
                    }
                )

            # =====================================================
            # 5. HIGH INDIVIDUAL INCIDENT DURATION
            # =====================================================

            duration_limit = (
                row["sla_threshold_hours"]
                * high_duration_multiplier
            )

            if (
                pd.notna(row["max_duration_hours"])
                and row["max_duration_hours"]
                > duration_limit
            ):

                alerts.append(
                    {
                        "alert_type": "HIGH",
                        "alert_title":
                            "High Incident Duration",
                        "alert_message":
                            f"Maximum duration is "
                            f"{row['max_duration_hours']:.2f} hours; "
                            f"limit is "
                            f"{duration_limit:.2f} hours",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    (
                                        x["ins_priority"]
                                        == row["ins_priority"]
                                    )
                                    & (
                                        x["duration_hours"]
                                        > duration_limit
                                    )
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration":
                            row["max_duration_hours"],
                        "priority":
                            row["priority_number"],
                        "metric_value":
                            row["max_duration_hours"],
                        "threshold_value":
                            duration_limit
                    }
                )

        # =========================================================
        # OVERALL DAILY ALERTS
        # =========================================================

        for _, row in daily_comparison.iterrows():

            previous_total = (
                row["previous_total_incidents"]
            )

            previous_resolved = (
                row["previous_resolved_incidents"]
            )

            # =====================================================
            # 6. INCIDENT VOLUME INCREASE
            # =====================================================

            if (
                pd.notna(previous_total)
                and previous_total > 0
            ):

                volume_increase = (
                    (
                        row["total_incidents"]
                        - previous_total
                    )
                    * 100
                    / previous_total
                )

                if (
                    volume_increase
                    >= volume_increase_threshold
                ):

                    alerts.append(
                        {
                            "alert_type": "WARNING",
                            "alert_title":
                                "Incident Volume Increased",
                            "alert_message":
                                f"Today: "
                                f"{int(row['total_incidents'])}; "
                                f"previous day: "
                                f"{int(previous_total)}; "
                                f"increase: "
                                f"{volume_increase:.2f}%",
                            "incident_details":
                                get_incident_details(
                                    row["incident_date"],
                                    sort_by="opened_at",
                                    ascending=True
                                ),
                            "incident_date":
                                row["incident_date"],
                            "duration": None,
                            "priority": None,
                            "metric_value":
                                round(
                                    volume_increase,
                                    2
                                ),
                            "threshold_value":
                                volume_increase_threshold
                        }
                    )

            # =====================================================
            # 7. RESOLUTION VOLUME DECREASE
            # =====================================================

            if (
                pd.notna(previous_resolved)
                and previous_resolved > 0
            ):

                resolution_decrease = (
                    (
                        previous_resolved
                        - row["resolved_incidents"]
                    )
                    * 100
                    / previous_resolved
                )

                if (
                    resolution_decrease
                    >= resolution_drop_threshold
                ):

                    alerts.append(
                        {
                            "alert_type": "WARNING",
                            "alert_title":
                                "Resolution Volume Decreased",
                            "alert_message":
                                f"Resolved today: "
                                f"{int(row['resolved_incidents'])}; "
                                f"previous day: "
                                f"{int(previous_resolved)}; "
                                f"decrease: "
                                f"{resolution_decrease:.2f}%",
                            "incident_details":
                                get_incident_details(
                                    row["incident_date"],
                                    lambda x:
                                        x["resolved_flag"] == 0
                                ),
                            "incident_date":
                                row["incident_date"],
                            "duration": None,
                            "priority": None,
                            "metric_value":
                                round(
                                    resolution_decrease,
                                    2
                                ),
                            "threshold_value":
                                resolution_drop_threshold
                        }
                    )

            # =====================================================
            # 8. HIGH P1/P2 VOLUME
            # =====================================================

            if (
                row["p1p2_incidents"]
                >= p1p2_volume_threshold
            ):

                alerts.append(
                    {
                        "alert_type": "HIGH",
                        "alert_title":
                            "High P1/P2 Incident Volume",
                        "alert_message":
                            f"P1/P2 incidents today: "
                            f"{int(row['p1p2_incidents'])}",
                        "incident_details":
                            get_incident_details(
                                row["incident_date"],
                                lambda x:
                                    x["priority_number"].isin(
                                        [1, 2]
                                    ),
                                sort_by="duration_hours",
                                ascending=False
                            ),
                        "incident_date":
                            row["incident_date"],
                        "duration": None,
                        "priority": None,
                        "metric_value":
                            row["p1p2_incidents"],
                        "threshold_value":
                            p1p2_volume_threshold
                    }
                )

        # =========================================================
        # CREATE RESULT DATAFRAME
        # =========================================================

        result = pd.DataFrame(
            alerts
        )

        # =========================================================
        # EMPTY RESULT HANDLING
        # =========================================================

        if result.empty:

            result = pd.DataFrame(
                columns=[
                    "alert_type",
                    "alert_title",
                    "alert_message",
                    "incident_details",
                    "incident_date",
                    "duration",
                    "priority",
                    "metric_value",
                    "threshold_value"
                ]
            )

        else:

            # =====================================================
            # RECENT 7 DAYS
            # =====================================================

            recent_date = (
                pd.Timestamp.now().normalize()
                - pd.Timedelta(days=7)
            )

            result = result[
                result["incident_date"]
                >= recent_date
            ].copy()

            # =====================================================
            # ALERT PRIORITY
            # =====================================================

            alert_order = {
                "HIGH": 1,
                "WARNING": 2,
                "MEDIUM": 3,
                "INFO": 4
            }

            result["alert_order"] = (
                result["alert_type"]
                .map(alert_order)
                .fillna(5)
            )

            # =====================================================
            # SORT RESULT
            # =====================================================

            result.sort_values(
                by=[
                    "incident_date",
                    "alert_order",
                    "duration"
                ],
                ascending=[
                    False,
                    True,
                    False
                ],
                na_position="last",
                inplace=True
            )

            result.drop(
                columns=["alert_order"],
                inplace=True
            )

            result.reset_index(
                drop=True,
                inplace=True
            )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "Manager_recent_alert_09.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    


    def generate_gamification_challenges_csv(self):
        output_dir = r"C:\Users\RSR\PYTHON\ServicenowGamification\Artifacts\ManagerDashBorad"
        file_name = "GAMIFICATION_CHALLENGES.csv"

        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, file_name)

        headers = [
            "CHALLENGE_ID",
            "CHALLENGE_NAME",
            "CHALLENGE_DESCRIPTION",
            "CHALLENGE_TYPE",
            "TARGET_VALUE",
            "CURRENT_VALUE",
            "START_DATE",
            "END_DATE",
            "STATUS",
            "POINTS_REWARD",
            "BADGE_REWARD"
        ]

        challenges = [
            [
                1,
                "SLA Champion",
                "Maintain SLA compliance for assigned incidents",
                "SLA",
                95,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                500,
                "SLA_CHAMPION"
            ],
            [
                2,
                "First Contact Hero",
                "Achieve a high First Contact Resolution rate",
                "FCR",
                90,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                500,
                "FCR_HERO"
            ],
            [
                3,
                "Fast Resolver",
                "Resolve incidents within the target resolution time",
                "RESOLUTION_TIME",
                90,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                400,
                "FAST_RESOLVER"
            ],
            [
                4,
                "Customer Favorite",
                "Maintain an excellent customer rating",
                "CUSTOMER_RATING",
                4.5,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                500,
                "CUSTOMER_FAVORITE"
            ],
            [
                5,
                "Zero Reopen",
                "Minimize incidents that are reopened",
                "REOPEN",
                0,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                300,
                "ZERO_REOPEN"
            ],
            [
                6,
                "Team Player",
                "Minimize unnecessary incident reassignments",
                "REASSIGNMENT",
                2,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                300,
                "TEAM_PLAYER"
            ],
            [
                7,
                "Priority Master",
                "Successfully resolve high-priority incidents",
                "PRIORITY",
                20,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                500,
                "PRIORITY_MASTER"
            ],
            [
                8,
                "Points Hunter",
                "Earn the required number of gamification points",
                "POINTS",
                1000,
                0,
                "24-Aug-26",
                "23-Sep-26",
                "ACTIVE",
                750,
                "POINTS_HUNTER"
            ]
        ]

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(challenges)

        print(f"CSV created successfully:")
        print(file_path)


    def generate_manager_gamification_summary(self):

        # =========================================================
        # INPUT FILE - INCIDENT DATA
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        # =========================================================
        # INPUT FILE - GAMIFICATION CHALLENGES
        # =========================================================

        challenges = (
            self.project_root
            / "Artifacts"
            / "ManagerDashBorad"
            / "GAMIFICATION_CHALLENGES.csv"
        )

        # =========================================================
        # READ INCIDENT DATA
        # =========================================================

        df = pd.read_csv(
            incident,
            encoding="utf-8"
        )

        # =========================================================
        # READ CHALLENGES DATA
        # =========================================================

        challenge_df = pd.read_csv(
            challenges,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE INCIDENT COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # NORMALIZE CHALLENGE COLUMN NAMES
        # =========================================================

        challenge_df.columns = (
            challenge_df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # RENAME INCIDENT COLUMNS
        # =========================================================

        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE INCIDENT COLUMNS
        # =========================================================

        required_incident_columns = [
            "assigned_to",
            "points",
            "agent_badge"
        ]

        missing_incident_columns = [
            col
            for col in required_incident_columns
            if col not in df.columns
        ]

        if missing_incident_columns:
            raise KeyError(
                "Missing columns in AchievementResults.csv: "
                f"{missing_incident_columns}"
            )

        # =========================================================
        # VALIDATE CHALLENGE COLUMNS
        # =========================================================

        required_challenge_columns = [
            "status",
            "start_date",
            "end_date"
        ]

        missing_challenge_columns = [
            col
            for col in required_challenge_columns
            if col not in challenge_df.columns
        ]

        if missing_challenge_columns:
            raise KeyError(
                "Missing columns in GAMIFICATION_CHALLENGES.csv: "
                f"{missing_challenge_columns}"
            )

        # =========================================================
        # CLEAN ASSIGNED TO
        # =========================================================

        df["assigned_to"] = (
            df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # CLEAN AGENT BADGE
        # =========================================================

        df["agent_badge"] = (
            df["agent_badge"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # CONVERT POINTS
        # =========================================================

        df["points"] = pd.to_numeric(
            df["points"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # TOTAL AGENTS
        #
        # SQL:
        # COUNT(DISTINCT ASSIGNED_TO)
        # WHERE ASSIGNED_TO IS NOT NULL
        # =========================================================

        total_agents = (
            df.loc[
                df["assigned_to"] != "",
                "assigned_to"
            ]
            .nunique()
        )

        # =========================================================
        # TOTAL POINTS
        #
        # SQL:
        # NVL(SUM(POINTS), 0)
        # =========================================================

        total_points = df["points"].sum()

        # =========================================================
        # BADGES AWARDED
        #
        # SQL:
        # COUNT(*)
        # FROM (
        #   SELECT DISTINCT ASSIGNED_TO, AGENT_BADGE
        #   ...
        # )
        # =========================================================

        badge_data = df[
            (df["assigned_to"] != "")
            & (df["agent_badge"] != "")
        ][
            [
                "assigned_to",
                "agent_badge"
            ]
        ].drop_duplicates()

        badges_awarded = len(
            badge_data
        )

        # =========================================================
        # CONVERT CHALLENGE DATES
        # =========================================================

        challenge_df["start_date"] = pd.to_datetime(
            challenge_df["start_date"],
            errors="coerce"
        )

        challenge_df["end_date"] = pd.to_datetime(
            challenge_df["end_date"],
            errors="coerce"
        )

        # =========================================================
        # CLEAN CHALLENGE STATUS
        # =========================================================

        challenge_df["status"] = (
            challenge_df["status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # =========================================================
        # ACTIVE CHALLENGES
        #
        # SQL:
        # STATUS = 'ACTIVE'
        # AND SYSDATE >= START_DATE
        # AND SYSDATE < END_DATE
        # =========================================================

        current_time = pd.Timestamp.now()

        active_challenges = challenge_df[
            (challenge_df["status"] == "ACTIVE")
            & (
                current_time
                >= challenge_df["start_date"]
            )
            & (
                current_time
                < challenge_df["end_date"]
            )
        ]

        active_challenge_count = len(
            active_challenges
        )

        # =========================================================
        # CREATE SUMMARY RESULT
        # =========================================================

        result = pd.DataFrame(
            {
                "FEATURES": [
                    "Total Agents",
                    "Total Points",
                    "Badges Awarded",
                    "Active Challenges"
                ],
                "COUNTS": [
                    total_agents,
                    total_points,
                    badges_awarded,
                    active_challenge_count
                ]
            }
        )

        # =========================================================
        # CONVERT COUNTS TO INTEGER
        # =========================================================

        result["COUNTS"] = pd.to_numeric(
            result["COUNTS"],
            errors="coerce"
        ).fillna(0)

        result["COUNTS"] = (
            result["COUNTS"]
            .astype(int)
        )

        # =========================================================
        # RESET INDEX
        # =========================================================

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "MANAGER_GAMIFICATION_SUMMARY_10.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )


    def generate_manager_top_badges_earned(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        group_badge_summary = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "group_badge_summary.csv"
        )

        # =========================================================
        # READ INPUT FILE
        # =========================================================

        df = pd.read_csv(
            group_badge_summary,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "badges",
            "badge_count"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in group_badge_summary.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CLEAN BADGES
        # =========================================================

        df["badges"] = (
            df["badges"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # CONVERT BADGE COUNT
        # =========================================================

        df["badge_count"] = pd.to_numeric(
            df["badge_count"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # REMOVE NULL / EMPTY BADGES
        # =========================================================

        df = df[
            df["badges"] != ""
        ].copy()

        # =========================================================
        # GROUP BY BADGES
        # =========================================================

        result = (
            df.groupby(
                "badges",
                as_index=False
            )
            .agg(
                badge_count=(
                    "badge_count",
                    "sum"
                )
            )
        )

        # =========================================================
        # CREATE TOTAL AGENTS COLUMN
        # =========================================================

        result["total_agents"] = (
            "Awarded to "
            + result["badge_count"]
            .astype(int)
            .astype(str)
            + " Agents"
        )

        # =========================================================
        # FINAL COLUMNS
        # =========================================================

        result = result[
            [
                "badges",
                "total_agents"
            ]
        ].copy()

        # =========================================================
        # RENAME OUTPUT COLUMNS
        # =========================================================

        result.rename(
            columns={
                "badges": "BADGES",
                "total_agents": "TOTAL_AGENTS"
            },
            inplace=True
        )

        # =========================================================
        # SORT BY BADGE COUNT DESCENDING
        # =========================================================

        result["badge_count_sort"] = (
            result["TOTAL_AGENTS"]
            .str.extract(r"(\d+)")
            .astype(int)
        )

        result.sort_values(
            by="badge_count_sort",
            ascending=False,
            inplace=True
        )

        result.drop(
            columns=["badge_count_sort"],
            inplace=True
        )

        # =========================================================
        # RESET INDEX
        # =========================================================

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "Manger_TOP_Badges_eardned_11.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )

    def generate_manager_performance_distribution(self):

        # =========================================================
        # INPUT FILE
        # =========================================================

        group_badge_summary = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "group_badge_summary.csv"
        )

        # =========================================================
        # READ INPUT FILE
        # =========================================================

        df = pd.read_csv(
            group_badge_summary,
            encoding="utf-8"
        )

        # =========================================================
        # NORMALIZE COLUMN NAMES
        # =========================================================

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "assignment_group",
            "sla_percentage",
            "fcr_percentage",
            "average_points"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Missing columns in group_badge_summary.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # BASE DATA
        # COALESCE NULL VALUES TO ZERO
        # =========================================================

        df["sla_percentage"] = pd.to_numeric(
            df["sla_percentage"],
            errors="coerce"
        ).fillna(0)

        df["fcr_percentage"] = pd.to_numeric(
            df["fcr_percentage"],
            errors="coerce"
        ).fillna(0)

        df["average_points"] = pd.to_numeric(
            df["average_points"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # CLEAN ASSIGNMENT GROUP
        # =========================================================

        df["assignment_group"] = (
            df["assignment_group"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # MAXIMUM AVERAGE POINTS
        # =========================================================

        max_average_points = (
            df["average_points"].max()
        )

        # =========================================================
        # PERFORMANCE SCORE
        #
        # SLA             = 40%
        # FCR             = 30%
        # Average Points  = 30%
        # =========================================================

        if max_average_points > 0:

            df["performance_score"] = (
                df["sla_percentage"] * 0.40
                + df["fcr_percentage"] * 0.30
                + (
                    df["average_points"]
                    / max_average_points
                    * 100
                ) * 0.30
            )

        else:

            df["performance_score"] = (
                df["sla_percentage"] * 0.40
                + df["fcr_percentage"] * 0.30
            )

        # =========================================================
        # PERFORMANCE CATEGORY
        # =========================================================

        df["performance_category"] = np.select(
            [
                df["performance_score"] >= 70,
                df["performance_score"] >= 40
            ],
            [
                "High Performer",
                "Average Performer"
            ],
            default="Low Performer"
        )

        # =========================================================
        # PERFORMANCE DISTRIBUTION
        # =========================================================

        result = (
            df.groupby(
                "performance_category",
                as_index=False
            )
            .agg(
                group_count=(
                    "assignment_group",
                    "count"
                )
            )
        )

        # =========================================================
        # CALCULATE PERCENTAGE
        # =========================================================

        total_groups = (
            result["group_count"].sum()
        )

        result["percentage"] = (
            result["group_count"]
            * 100
            / total_groups
        ).round(2)

        # =========================================================
        # FINAL COLUMNS
        # =========================================================

        result = result[
            [
                "performance_category",
                "group_count",
                "percentage"
            ]
        ].copy()

        # =========================================================
        # RENAME OUTPUT COLUMNS
        # =========================================================

        result.rename(
            columns={
                "performance_category":
                    "PERFORMANCE_CATEGORY",
                "group_count":
                    "GROUP_COUNT",
                "percentage":
                    "PERCENTAGE"
            },
            inplace=True
        )

        # =========================================================
        # SORT PERFORMANCE CATEGORY
        # =========================================================

        category_order = {
            "High Performer": 1,
            "Average Performer": 2,
            "Low Performer": 3
        }

        result["category_order"] = (
            result["PERFORMANCE_CATEGORY"]
            .map(category_order)
        )

        result.sort_values(
            by="category_order",
            inplace=True
        )

        result.drop(
            columns=["category_order"],
            inplace=True
        )

        # =========================================================
        # RESET INDEX
        # =========================================================

        result.reset_index(
            drop=True,
            inplace=True
        )

        # =========================================================
        # OUTPUT FILE
        # =========================================================

        output_file = (
            self.output_dir
            / "Manager_performanace_distribution_12.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )


        





    def run(self):

        try:

            self.generate_live_streak_overall_level()
            self.generate_manager_incidents_over_time()
            self.generate_manager_sla_trend_overall()
            self.generate_manager_incident_by_state()
            self.insert_agent_level_fcr_data()
            self.generate_manager_avg_by_priority()
            self.generate_manager_sla_by_priority()
            self.generate_manager_recent_alert()
            self.generate_gamification_challenges_csv()
            self.generate_manager_gamification_summary()
            self.generate_manager_top_badges_earned()
            self.generate_manager_performance_distribution()


           # return agent_header

        except Exception as e:

            raise
