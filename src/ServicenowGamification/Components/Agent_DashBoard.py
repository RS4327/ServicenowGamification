from pathlib import Path

import pandas as pd
import numpy as np
from ServicenowGamification.Utils.Common import (
    Read_Yaml,
    create_directories
)


class AgentDashBoard:

    def __init__(self):

        # =========================================================
        # PROJECT ROOT
        # =========================================================

        current_file = Path(__file__).resolve()

        self.project_root = current_file.parents[3]

        # =========================================================
        # PARAMS YAML
        # =========================================================

        self.params_path = (
            self.project_root / "params.yaml"
        )

        if not self.params_path.exists():

            raise FileNotFoundError(
                f"params.yaml not found -> "
                f"{self.params_path}"
            )

        print(
            f"Reading YAML : {self.params_path}"
        )

        self.params = Read_Yaml(
            str(self.params_path)
        )

        # =========================================================
        # DASHBOARD OUTPUT DIRECTORY
        # =========================================================

        self.output_dir = (
            self.project_root
            / "Artifacts"
            / "AgentDashBorad"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"Dashboard directory : {self.output_dir}"
        )

    # ============================================================
    # GET INPUT FILE
    # ============================================================

    def _get_input_file(self):

        input_file = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        if not input_file.exists():

            raise FileNotFoundError(
                "AchievementResults.csv not found -> "
                f"{input_file}"
            )

        return input_file

    # ============================================================
    # READ INPUT
    # ============================================================

    def _read_input(self):

        input_file = self._get_input_file()

        print(
            f"Reading AchievementResults : {input_file}"
        )

        try:

            df = pd.read_csv(
                input_file
            )

        except Exception as e:

            raise RuntimeError(
                f"Unable to read AchievementResults.csv : {e}"
            ) from e

        if df.empty:

            raise ValueError(
                "AchievementResults.csv contains no records"
            )

        print(
            f"Input records : {len(df)}"
        )

        return df

    # ============================================================
    # CLEAN COLUMN NAMES
    # ============================================================

    def _clean_column_names(self, df):

        data = df.copy()

        data.columns = (
            data.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # --------------------------------------------------------
        # Check duplicate columns
        # --------------------------------------------------------

        duplicate_columns = (
            data.columns[
                data.columns.duplicated()
            ]
            .tolist()
        )

        if duplicate_columns:

            raise ValueError(
                "Duplicate columns found in input CSV : "
                f"{duplicate_columns}"
            )

        return data

    # ============================================================
    # VALIDATE COLUMNS
    # ============================================================

    def _validate_columns(self, data):

        required_columns = [
            "assigned_to",
            "assignment_group",
            "points"
        ]

        # --------------------------------------------------------
        # level / agent_level
        # --------------------------------------------------------

        if "agent_level" not in data.columns:

            if "level" in data.columns:

                data.rename(
                    columns={
                        "level": "agent_level"
                    },
                    inplace=True
                )

            else:

                raise ValueError(
                    "Missing column: agent_level "
                    "(or level)"
                )

        # --------------------------------------------------------
        # agent_level_name
        # --------------------------------------------------------

        if "agent_level_name" not in data.columns:

            if "level_name" in data.columns:

                data.rename(
                    columns={
                        "level_name": "agent_level_name"
                    },
                    inplace=True
                )

            else:

                # If not available, create blank column
                data["agent_level_name"] = ""

        # --------------------------------------------------------
        # Validate remaining columns
        # --------------------------------------------------------

        missing_columns = [
            column
            for column in required_columns
            if column not in data.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing required columns : "
                f"{missing_columns}"
            )

        return data

    # ============================================================
    # CLEAN DATA
    # ============================================================

    def _clean_data(self, df):

        data = df.copy()

        # --------------------------------------------------------
        # assigned_to
        # --------------------------------------------------------

        data["assigned_to"] = (
            data["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # --------------------------------------------------------
        # assignment_group
        # --------------------------------------------------------

        data["assignment_group"] = (
            data["assignment_group"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # --------------------------------------------------------
        # agent_level
        # --------------------------------------------------------

        data["agent_level"] = (
            data["agent_level"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # --------------------------------------------------------
        # agent_level_name
        # --------------------------------------------------------

        data["agent_level_name"] = (
            data["agent_level_name"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # --------------------------------------------------------
        # points
        # --------------------------------------------------------

        data["points"] = pd.to_numeric(
            data["points"],
            errors="coerce"
        ).fillna(0)

        # --------------------------------------------------------
        # Remove invalid agents
        # --------------------------------------------------------

        data = data[
            (data["assigned_to"] != "")
            & (
                data["assigned_to"]
                .str.upper()
                != "NAN"
            )
            & (
                data["assigned_to"]
                .str.upper()
                != "NONE"
            )
        ].copy()

        if data.empty:

            raise ValueError(
                "No valid assigned_to records available"
            )

        return data

    # ============================================================
    # GENERATE AGENT HEADER
    # ============================================================

    def generate_agent_header(self):

        print("=" * 70)
        print("AGENT HEADER")
        print("=" * 70)

        # ========================================================
        # READ
        # ========================================================

        df = self._read_input()

        # ========================================================
        # CLEAN COLUMN NAMES
        # ========================================================

        data = self._clean_column_names(
            df
        )

        # ========================================================
        # VALIDATE
        # ========================================================

        data = self._validate_columns(
            data
        )

        # ========================================================
        # CLEAN DATA
        # ========================================================

        data = self._clean_data(
            data
        )

        # ========================================================
        # GROUP BY AGENT HEADER
        # ========================================================

        agent_header = (
            data
            .groupby(
                [
                    "assigned_to",
                    "assignment_group",
                    "agent_level",
                    "agent_level_name"
                ],
                as_index=False
            )
            .agg(
                points=(
                    "points",
                    "sum"
                )
            )
        )

        # ========================================================
        # ROUND POINTS
        # ========================================================

        agent_header["points"] = (
            agent_header["points"]
            .round(2)
        )

        # ========================================================
        # SORT
        # ========================================================

        agent_header = (
            agent_header
            .sort_values(
                by=[
                    "assigned_to",
                    "assignment_group"
                ],
                ascending=[
                    True,
                    True
                ]
            )
            .reset_index(drop=True)
        )

        # ========================================================
        # RENAME
        # ========================================================

        agent_header.rename(
            columns={
                "assigned_to": "ASSIGNED_TO",
                "assignment_group": "ASSIGNMENT_GROUP",
                "agent_level": "AGENT_LEVEL",
                "agent_level_name": "AGENT_LEVEL_NAME",
                "points": "POINTS"
            },
            inplace=True
        )

        # ========================================================
        # OUTPUT FILE
        # ========================================================

        output_file = (
            self.output_dir
            / "Agent_Header_01.csv"
        )

        # ========================================================
        # SAVE
        # ========================================================

        agent_header.to_csv(
            output_file,
            index=False
        )

        # ========================================================
        # LOG
        # ========================================================

        print(
            f"Agent Header records : "
            f"{len(agent_header)}"
        )

        print(
            f"Agent Header saved : "
            f"{output_file}"
        )

        print("=" * 70)
        print(
            "AGENT HEADER GENERATED SUCCESSFULLY"
        )
        print("=" * 70)

        return agent_header

    def read_csv_file(self, file_name):

        file_path = self.output_dir / file_name

        print( f"Reading : {file_path}")

        if not file_path.exists():

            raise FileNotFoundError(
                f"CSV file not found : {file_path}"
            )

        df = pd.read_csv(file_path)

        print(f"Records : {len(df)}")

        return df

    # =============================================================
    # CLEAN COLUMN NAMES
    # =============================================================

    def clean_columns(self, df):

        df = df.copy()

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        return df

    # =============================================================
    # CLEAN AGENT NAME
    # =============================================================

    def clean_agent(self, df, column="agent"):

        if column in df.columns:

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        return df

    # =============================================================
    # GENERATE AGENT PERFORMANCE SUMMARY
    # =============================================================

    def generate_agent_performance_summary(self):

        print("=" * 70)
        print("AGENT PERFORMANCE SUMMARY")
        print("=" * 70)

        # =========================================================
        # 1. INCIDENT GAMIFICATION FINAL
        # =========================================================
 
        incident= (
                    self.project_root
                    / "Artifacts"
                    / "DataGamification"
                    / "AchievementResults.csv"
                )
        incident_df=pd.read_csv(incident)
        # =========================================================
        # VALIDATE INCIDENT COLUMNS
        # =========================================================


        incident_df.rename(columns={"state":"ins_state" },inplace=True)
        required_incident_columns = [
            "assigned_to",
            "ins_state",
            "total_incidents"
        ]

        missing = [
            col
            for col in required_incident_columns
            if col not in incident_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                "Incident_Gamification_Final.csv : "
                f"{missing}"
            )

        # =========================================================
        # CLEAN AGENT
        # =========================================================

        incident_df["assigned_to"] = (
            incident_df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        incident_df["ins_state"] = (
            incident_df["ins_state"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # =========================================================
        # SQL:
        #
        # WITH agent_opened AS (
        #
        # SELECT
        #     assigned_to AS agent_name,
        #     total_incidents,
        #     COUNT(*) opened_count
        #
        # FROM incident_gamification_final
        #
        # WHERE ins_state NOT IN
        # ('Closed', 'Resolved')
        #
        # GROUP BY assigned_to, total_incidents
        #
        # )
        # =========================================================

        opened_df = (
            incident_df[
                ~incident_df["ins_state"].isin(
                    [
                        "CLOSED",
                        "RESOLVED"
                    ]
                )
            ]
            .groupby(
                [
                    "assigned_to",
                    "total_incidents"
                ],
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "assigned_to": "agent_name",
                    "size": "opened_count"
                }
            )
        )

        # =========================================================
        # RENAME TOTAL INCIDENTS
        # =========================================================

        opened_df.rename(columns={"total_incidents":"total_incidents" },inplace=True)

        # =========================================================
        # 2. AGENT LEVEL MTTR
        # =========================================================

        # mttr_df = self.read_csv_file(
        #     "Agent_Level_MTTR.csv"
        # )

        mttr = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelMTTR.csv" )
        mttr_df=pd.read_csv(mttr)
        mttr_df = self.clean_columns( mttr_df)

        # =========================================================
        # EXPECTED:
        #
        # agent
        # mttr_hours
        # =========================================================

        required = [ "agent","resolved_incident_count","closed_incident_count", "mttr_hours"]
        print('mttrcolumns ',mttr_df.columns)

        missing = [
            col
            for col in required
            if col not in mttr_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                f"Agent_Level_MTTR.csv : {missing}"
            )

        mttr_df = self.clean_agent(
            mttr_df
        )

        # =========================================================
        # 3. AGENT LEVEL SLA
        # =========================================================

        # sla_df = self.read_csv_file(
        #     "Agent_Level_SLA.csv"
        # )

        sla = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelSLA.csv" )
        
        sla_df=pd.read_csv(sla)
        sla_df = self.clean_columns(sla_df)

        required = ["agent","sla_compliance"]

        missing = [
            col
            for col in required
            if col not in sla_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                f"Agent_Level_SLA.csv : {missing}"
            )

        sla_df = self.clean_agent( sla_df)

        # =========================================================
        # 4. AGENT FCR
        # =========================================================

        # fcr_df = self.read_csv_file(
        #     "Agent_FCR.csv"
        # )
        fcr = (
                    self.project_root
                    / "Artifacts"
                    / "MetricsCalculation"
                    / "AgentLevelFCR.csv" )


        fcr_df=pd.read_csv(fcr)

        fcr_df = self.clean_columns(fcr_df)

        required = ["agent","fcr_percentage"]

        missing = [
            col
            for col in required
            if col not in fcr_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                f"Agent_FCR.csv : {missing}"
            )

        fcr_df = self.clean_agent(
            fcr_df
        )

        # =========================================================
        # 5. AGENT LEVEL SUMMARY
        # =========================================================

        # level_df = self.read_csv_file(
        #     "Agent_Level_Summary.csv"
        # )

        level  = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AgentLevel.csv" )

        
        level_df=pd.read_csv(level)

        level_df.rename(columns={"level":"agent_level" },inplace=True)
        level_df = self.clean_columns( level_df )

        required = [ "agent", "agent_level" ]

        missing = [
            col
            for col in required
            if col not in level_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                f"Agent_Level_Summary.csv : {missing}"
            )

        level_df = self.clean_agent(
            level_df
        )

        # =========================================================
        # 6. AGENT RANKING
        # =========================================================

        # ranking_df = self.read_csv_file(
        #     "Agent_Ranking.csv"
        # )

        ranking = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AgentPoints.csv" )

        ranking_df=pd.read_csv(ranking)

        ranking_df = self.clean_columns(ranking_df)

        required = [ "agent", "total_points"]

        missing = [
            col
            for col in required
            if col not in ranking_df.columns
        ]

        if missing:

            raise ValueError(
                "Missing columns in "
                f"Agent_Ranking.csv : {missing}"
            )

        ranking_df = self.clean_agent(
            ranking_df
        )

        # =========================================================
        # 7. RENAME JOIN COLUMNS
        # =========================================================

        mttr_df.rename(
            columns={
                "agent": "agent_name"
            },
            inplace=True
        )

        sla_df.rename(
            columns={
                "agent": "agent_name"
            },
            inplace=True
        )

        fcr_df.rename(
            columns={
                "agent": "agent_name"
            },
            inplace=True
        )

        level_df.rename(
            columns={
                "agent": "agent_name"
            },
            inplace=True
        )

        ranking_df.rename(
            columns={
                "agent": "agent_name"
            },
            inplace=True
        )

        # =========================================================
        # 8. REMOVE DUPLICATE AGENTS
        #
        # Important because SQL uses DISTINCT.
        # =========================================================

        mttr_df = mttr_df.drop_duplicates(
            subset=["agent_name"]
        )

        sla_df = sla_df.drop_duplicates(
            subset=["agent_name"]
        )

        fcr_df = fcr_df.drop_duplicates(
            subset=["agent_name"]
        )

        level_df = level_df.drop_duplicates(
            subset=["agent_name"]
        )

        ranking_df = ranking_df.drop_duplicates(
            subset=["agent_name"]
        )

        # =========================================================
        # 9. JOIN MTTR
        # =========================================================

        result = opened_df.merge(
            mttr_df[
                [
                    "agent_name","mttr_hours" ,"resolved_incident_count","closed_incident_count",
                ]
            ],
            on="agent_name",
            how="left"
        )

        # =========================================================
        # 10. JOIN SLA
        # =========================================================

        result = result.merge(
            sla_df[
                [
                    "agent_name",
                    "sla_compliance"
                ]
            ],
            on="agent_name",
            how="left"
        )

        # =========================================================
        # 11. JOIN FCR
        # =========================================================

        result = result.merge(
            fcr_df[
                [
                    "agent_name",
                    "fcr_percentage"
                ]
            ],
            on="agent_name",
            how="left"
        )

        # =========================================================
        # 12. JOIN LEVEL
        # =========================================================

        result = result.merge(
            level_df[
                [
                    "agent_name",
                    "agent_level"
                ]
            ],
            on="agent_name",
            how="left"
        )

        # =========================================================
        # 13. JOIN RANKING
        # =========================================================

        result = result.merge(
            ranking_df[
                [
                    "agent_name",
                    "total_points"
                ]
            ],
            on="agent_name",
            how="left"
        )

        # =========================================================
        # 14. SELECT FINAL COLUMNS
        # =========================================================

        result = result[
            [
                "agent_name",
                "total_incidents",
                "resolved_incident_count",
                "closed_incident_count",
                "opened_count",
                "mttr_hours",
                "sla_compliance",
                "fcr_percentage",
                "total_points",
                "agent_level"
            ]
        ]

        # =========================================================
        # 15. REMOVE DUPLICATES
        #
        # Equivalent to SELECT DISTINCT
        # =========================================================

        result = (
            result
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # =========================================================
        # 16. SAVE CSV
        # =========================================================

        output_file = (
            self.output_dir
            / "Agent_Performance_Summry_02.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

        

        print("=" * 70)
        print(
            "AGENT PERFORMANCE SUMMARY "
            "GENERATED SUCCESSFULLY"
        )
        print("=" * 70)

        #return result

    def generate_agent_sla_performance_summary(self):

        sla = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelSLA.csv" )


        sla_df = pd.read_csv(sla)

        sla_df.columns = (
            sla_df.columns
            .str.strip()
            .str.upper()
        )

        report_df = sla_df[
            [
                "AGENT",
                "TOTAL_RESOLVED_INCIDENTS",
                "SLA_MET",
                "SLA_BREACHED",
                "SLA_MET_PERCENTAGE",
                "SLA_BREACHED_PERCENTAGE",
                "SLA_COMPLIANCE"
            ]
        ].copy()

        output_file = (
            self.output_dir
            / "AGENT_SLA_PERFORMANCE_SUMMRY_03.csv"
        )

        report_df.to_csv(
            output_file,
            index=False
        )

        #return report_df
    
    def generate_agent_fcr_performance_summary(self):

        fcr_file = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelFCR.csv"
        )

        fcr_df = pd.read_csv(fcr_file)

        fcr_df.columns = (
            fcr_df.columns
            .str.strip()
            .str.upper()
        )

        report_df = fcr_df[
            [
                "AGENT",
                "TOTAL_INCIDENTS",
                "FCR_COUNT",
                "NON_FCR_COUNT",
                "FCR_PERCENTAGE",
                "NON_FCR_PERCENTAGE"
            ]
        ].copy()

        output_file = (
            self.output_dir
            / "Agent_FCR_Performance_Summry_04.csv"
        )

        report_df.to_csv(
            output_file,
            index=False
        )

    def generate_agent_incident_by_state(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)
        df.rename(columns={"state":"ins_state" },inplace=True)

        df["assigned_to"] = (
            df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["ins_state"] = (
            df["ins_state"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        result = (
            df.groupby(
                ["assigned_to", "ins_state"],
                as_index=False
            )
            .size()
            .rename(columns={"size": "state_count"})
        )

        result["total_incidents"] = (
            result.groupby("assigned_to")["state_count"]
            .transform("sum")
        )

        result["state_percentage"] = (
            result["state_count"]
            .div(result["total_incidents"])
            .mul(100)
            .round(2)
        )

        result["State(%)"] = (
            result["state_count"].astype(str)
            + "("
            + result["state_percentage"].astype(str)
            + " %)"
        )

        result = result[
            [
                "assigned_to",
                "ins_state",
                "State(%)"
            ]
        ].rename(
            columns={
                "assigned_to": "AGENT",
                "ins_state": "INS_STATE"
            }
        )

        result = result.sort_values(
            ["AGENT", "INS_STATE"]
        ).reset_index(drop=True)

        output_file = (
            self.output_dir
            / "Agent_Incident_By_State_05.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

    def generate_agent_recent_incidents(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)

        # Rename CSV columns
        df.rename(columns={"state": "ins_state"},inplace=True)
        df.rename(columns={"number": "number_id"},inplace=True)
        #df.rename(columns={"number": "number_id"},inplace=True)
        df.rename(columns={"priority": "ins_priority"},inplace=True)
        

        # Clean columns
        df["assigned_to"] = (
            df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # NVL(closed_at, resolved_at)
        df["resolved_at"] = (
            df["closed_at"]
            .where(df["ins_state"]
                   .str.upper().eq("CLOSED") )
                   .fillna(df["resolved_at"])
                   )

        # Select required columns
        result = df[
            [
                "number_id",
                "short_description",
                "ins_state",
                "ins_priority",
                "opened_at",
                "resolved_at"
            ]
        ].rename(
            columns={
                "number_id": "NUMBER_ID",
                "short_description": "Short Description",
                "ins_state": "State",
                "ins_priority": "Priority",
                "opened_at": "Opened At",
                "resolved_at": "Resolved At"
            }
        )

        # Save report
        output_file = (
            self.output_dir
            / "Agent_Recent_Incidents_06.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

    def generate_agent_performance_trend(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)
        df.rename(columns={"state": "ins_state"},inplace=True)
        df.rename(columns={"number": "number_id"},inplace=True)
        #df.rename(columns={"number": "number_id"},inplace=True)
        df.rename(columns={"priority": "ins_priority"},inplace=True)
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Convert date and numeric columns
        df["resolved_at"] = pd.to_datetime(
            df["resolved_at"],
            errors="coerce"
        )

        df["resolution_hours"] = pd.to_numeric(
            df["resolution_hours"],
            errors="coerce"
        )

        # # Selected agent
        # df = df[
        #     df["assigned_to"]
        #     .fillna("")
        #     .astype(str)
        #     .str.strip()
        #     .eq(agent_name)
        # ].copy()

        # Only resolved incidents
        df = df[
            df["resolved_at"].notna()
        ].copy()

        # Week starting Monday
        df["week_start"] = (
            df["resolved_at"]
            .dt.to_period("W-SUN")
            .dt.start_time
        )

        # SLA flag
        df["sla_met_flag"] = (
            df["sla_status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
            .isin([
                "MET",
                "COMPLIANT",
                "PASSED",
                "PASS"
            ])
            .astype(int)
        )

        # FCR flag
        df["fcr_flag"] = (
            df["fcr"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
            .isin([
                "1",
                "Y",
                "YES",
                "TRUE",
                "FCR"
            ])
            .astype(int)
        )

        # Weekly aggregation
        result = (
            df.groupby(
                [
                    "assigned_to",
                    "week_start"
                ],
                as_index=False
            )
            .agg(
                incident_count=(
                    "assigned_to",
                    "size"
                ),
                mttr_hours=(
                    "resolution_hours",
                    "mean"
                ),
                sla_compliance=(
                    "sla_met_flag",
                    "mean"
                ),
                fcr_percentage=(
                    "fcr_flag",
                    "mean"
                )
            )
        )

        # Convert ratios to percentages
        result["sla_compliance"] = (
            result["sla_compliance"] * 100
        ).round(2)

        result["fcr_percentage"] = (
            result["fcr_percentage"] * 100
        ).round(2)

        result["mttr_hours"] = (
            result["mttr_hours"]
            .round(2)
        )

        # Week label: Apr 21, Apr 28, etc.
        result["week_label"] = (
            result["week_start"]
            .dt.strftime("%b %d")
        )

        # Rename columns
        result.rename(
            columns={
                "assigned_to": "AGENT",
                "week_start": "WEEK_START",
                "week_label": "WEEK_LABEL",
                "incident_count": "INCIDENT_COUNT",
                "mttr_hours": "MTTR_HOURS",
                "sla_compliance": "SLA_COMPLIANCE",
                "fcr_percentage": "FCR_PERCENTAGE"
            },
            inplace=True
        )

        # Column order
        result = result[
            [
                "AGENT",
                "WEEK_START",
                "WEEK_LABEL",
                "INCIDENT_COUNT",
                "MTTR_HOURS",
                "SLA_COMPLIANCE",
                "FCR_PERCENTAGE"
            ]
        ]

        # Sort by week
        result.sort_values(
            "WEEK_START",
            inplace=True
        )

        # Save
        output_file = (
            self.output_dir
            / "Agent_Performance_Trend_07.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

        #return result

    def generate_agent_top_category(self):

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
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Clean columns
        df["assigned_to"] = (
            df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df["ins_category"] = (
            df["ins_category"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Remove NULL / blank categories
        df = df[
            (df["ins_category"] != "")
            & (df["ins_category"].str.upper() != "NAN")
        ].copy()

        # Agent + Category count
        result = (
            df.groupby(
                [
                    "assigned_to",
                    "ins_category"
                ],
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "incident_count"
                }
            )
        )

        # Category percentage per agent
        result["category_percentage"] = (
            result["incident_count"]
            / result.groupby("assigned_to")[
                "incident_count"
            ].transform("sum")
            * 100
        ).round(2)

        # Rank categories within each agent
        result["rn"] = (
            result.groupby("assigned_to")[
                "incident_count"
            ]
            .rank(
                method="first",
                ascending=False
            )
        )

        # Top 4 categories
        result = result[
            result["rn"] <= 4
        ].copy()

        # Sort
        result.sort_values(
            by=[
                "assigned_to",
                "incident_count"
            ],
            ascending=[
                True,
                False
            ],
            inplace=True
        )

        # Rename columns
        result.rename(
            columns={
                "assigned_to": "ASSIGNED_TO",
                "ins_category": "CATEGORY",
                "incident_count": "INCIDENT_COUNT",
                "category_percentage": "CATEGORY_PERCENTAGE"
            },
            inplace=True
        )

        # Remove rank
        result.drop(
            columns=["rn"],
            inplace=True
        )

        # Column order
        result = result[
            [
                "ASSIGNED_TO",
                "CATEGORY",
                "INCIDENT_COUNT",
                "CATEGORY_PERCENTAGE"
            ]
        ]

        # Save
        output_file = (
            self.output_dir
            / "Agent_Top_Category_08.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

        #return result

    def generate_agent_goals(self):

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
        # Clean required columns
        for col in ["assigned_to", "sla_status", "fcr", "ins_state"]:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

        goals = []

        for agent, data in df.groupby("assigned_to"):

            # =========================================================
            # 1. SLA GOAL
            # =========================================================

            sla_total = data["sla_status"].isin(
                ["MET", "BREACHED"]
            ).sum()

            sla_met = (
                data["sla_status"] == "MET"
            ).sum()

            if sla_total > 0:
                sla_current = round(
                    (sla_met / sla_total) * 100,
                    2
                )

                sla_progress = round(
                    min(
                        ((sla_current / 90) * 100),
                        100
                    ),
                    2
                )

                sla_remaining = round(
                    max(
                        90 - sla_current,
                        0
                    ),
                    2
                )

            else:
                # Oracle NULLIF returns NULL when denominator = 0
                sla_current = np.nan
                sla_progress = np.nan
                sla_remaining = np.nan

            goals.append({
                "AGENT": agent,
                "GOAL": "Improve SLA Compliance",
                "CURRENT_VALUE": sla_current,
                "TARGET": 90,
                "PROGRESS": sla_progress,
                "REMAINING": sla_remaining,
                "UNIT": "%",
                "DUE_DATE": "31-May-2025",
                "STATUS": (
                    "On Track"
                    if pd.notna(sla_current)
                    and sla_current >= 70
                    else "At Risk"
                )
            })

            # =========================================================
            # 2. FCR GOAL
            # =========================================================

            fcr_total = (
                data["fcr"] != ""
            ).sum()

            fcr_met = data["fcr"].isin(
                [
                    "1",
                    "YES",
                    "Y",
                    "TRUE",
                    "MET"
                ]
            ).sum()

            if fcr_total > 0:
                fcr_current = round(
                    (fcr_met / fcr_total) * 100,
                    2
                )

                fcr_progress = round(
                    min(
                        ((fcr_current / 80) * 100),
                        100
                    ),
                    2
                )

                fcr_remaining = round(
                    max(
                        80 - fcr_current,
                        0
                    ),
                    2
                )

            else:
                fcr_current = np.nan
                fcr_progress = np.nan
                fcr_remaining = np.nan

            goals.append({
                "AGENT": agent,
                "GOAL": "Achieve FCR 80%",
                "CURRENT_VALUE": fcr_current,
                "TARGET": 80,
                "PROGRESS": fcr_progress,
                "REMAINING": fcr_remaining,
                "UNIT": "%",
                "DUE_DATE": "31-May-2025",
                "STATUS": (
                    "On Track"
                    if pd.notna(fcr_current)
                    and fcr_current >= 60
                    else "At Risk"
                )
            })

            # =========================================================
            # 3. RESOLVE 15 INCIDENTS
            # =========================================================

            resolved_count = data["ins_state"].isin(
                [
                    "RESOLVED",
                    "CLOSED"
                ]
            ).sum()

            resolve_progress = min(
                round(
                    (resolved_count / 15) * 100,
                    2
                ),
                100
            )

            resolve_remaining = max(
                15 - resolved_count,
                0
            )

            goals.append({
                "AGENT": agent,
                "GOAL": "Resolve 15 Incidents",
                "CURRENT_VALUE": resolved_count,
                "TARGET": 15,
                "PROGRESS": resolve_progress,
                "REMAINING": resolve_remaining,
                "UNIT": None,
                "DUE_DATE": "31-May-2025",
                "STATUS": (
                    "On Track"
                    if resolved_count >= 15
                    else "At Risk"
                )
            })

        # =========================================================
        # CREATE DATAFRAME
        # =========================================================

        result = pd.DataFrame(
            goals,
            columns=[
                "AGENT",
                "GOAL",
                "CURRENT_VALUE",
                "TARGET",
                "PROGRESS",
                "REMAINING",
                "UNIT",
                "DUE_DATE",
                "STATUS"
            ]
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        output_file = (
            self.project_root
            / "Artifacts"
            / "AgentDashBorad"
            / "Agent_Goals_09.csv"
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        result.to_csv(
            output_file,
            index=False
        )

        #return result
    def generate_agent_performance_target(self):

        # =========================================================
        # INPUT FILES
        # =========================================================

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )
        
        mttr = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelMTTR.csv"
        )

        fcr = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelFCR.csv"
        )

        sla = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelSLA.csv"
        )

        # =========================================================
        # READ CSV FILES
        # =========================================================

        incident_df = pd.read_csv(incident)
        mttr_df = pd.read_csv(mttr)
        fcr_df = pd.read_csv(fcr)
        sla_df = pd.read_csv(sla)


        incident_df.rename(columns={"state": "ins_state"},inplace=True)
        incident_df.rename(columns={"number": "number_id"},inplace=True)
        incident_df.rename(columns={"category": "ins_category"},inplace=True)
        incident_df.rename(columns={"priority": "ins_priority"},inplace=True)

        # =========================================================
        # CLEAN COLUMN NAMES
        # =========================================================

        for df in [
            incident_df,
            mttr_df,
            fcr_df,
            sla_df
        ]:
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )

        # =========================================================
        # CLEAN AGENT NAMES
        # =========================================================

        incident_df["assigned_to"] = (
            incident_df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        mttr_df["agent"] = (
            mttr_df["agent"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        fcr_df["agent"] = (
            fcr_df["agent"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        sla_df["agent"] = (
            sla_df["agent"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # =========================================================
        # NUMERIC COLUMNS
        # =========================================================

        mttr_df["mttr_hours"] = pd.to_numeric(
            mttr_df["mttr_hours"],
            errors="coerce"
        )

        fcr_df["fcr_percentage"] = pd.to_numeric(
            fcr_df["fcr_percentage"],
            errors="coerce"
        )

        fcr_df["fcr_count"] = pd.to_numeric(
            fcr_df["fcr_count"],
            errors="coerce"
        )

        sla_df["sla_compliance"] = pd.to_numeric(
            sla_df["sla_compliance"],
            errors="coerce"
        )

        sla_df["sla_met_percentage"] = pd.to_numeric(
            sla_df["sla_met_percentage"],
            errors="coerce"
        )

        # =========================================================
        # 1. MTTR TARGET
        #
        # Oracle:
        #
        # Critical  = 4 hrs
        # High      = 8 hrs
        # Moderate  = 24 hrs
        # Low       = 48 hrs
        # =========================================================

        priority_counts = (
            incident_df
            .groupby(
                ["assigned_to", "ins_priority"],
                as_index=False
            )
            .size()
            .rename(columns={"size": "cnt"})
        )

        priority_target = {
            "1 - Critical": 4,
            "2 - High": 8,
            "3 - Moderate": 24,
            "4 - Low": 48
        }

        priority_counts["target_hours"] = (
            priority_counts["ins_priority"]
            .map(priority_target)
        )

        priority_counts["target_value"] = (
            priority_counts["cnt"]
            * priority_counts["target_hours"]
        )

        target_df = (
            priority_counts
            .groupby("assigned_to", as_index=False)
            ["target_value"]
            .sum()
            .rename(
                columns={
                    "assigned_to": "agent",
                    "target_value": "target_hrs"
                }
            )
        )

        # =========================================================
        # MTTR SOURCE
        # =========================================================

        mttr_result = mttr_df[
            [
                "agent",
                "mttr_hours"
            ]
        ].copy()

        mttr_result = mttr_result.merge(
            target_df,
            on="agent",
            how="inner"
        )

        mttr_result["STATUS"] = np.where(
            mttr_result["mttr_hours"]
            <= mttr_result["target_hrs"],
            "Met",
            "Not Met"
        )

        mttr_result["METRIC"] = "MTTR(Hours)"

        mttr_result["TARGET_HRS_HRS"] = (
            mttr_result["target_hrs"].astype(str)
            + " hrs"
        )

        mttr_result = mttr_result[
            [
                "METRIC",
                "agent",
                "mttr_hours",
                "TARGET_HRS_HRS",
                "STATUS"
            ]
        ]

        # =========================================================
        # 2. SLA COMPLIANCE
        # =========================================================

        sla_result = sla_df[
            [
                "agent",
                "sla_compliance",
                "sla_met_percentage"
            ]
        ].copy()

        sla_result["METRIC"] = "SLA Compliance(%)"

        sla_result["MTTR_HOURS"] = sla_result[
            "sla_compliance"
        ]

        sla_result["TARGET_HRS_HRS"] = ">=0 %"

        sla_result["STATUS"] = np.where(
            sla_result["sla_met_percentage"] >= 90,
            "Met",
            "Not Met"
        )

        sla_result = sla_result[
            [
                "METRIC",
                "agent",
                "MTTR_HOURS",
                "TARGET_HRS_HRS",
                "STATUS"
            ]
        ]

        # =========================================================
        # 3. FCR %
        # =========================================================

        fcr_percentage = fcr_df[
            [
                "agent",
                "fcr_percentage"
            ]
        ].copy()

        fcr_percentage["METRIC"] = "FCR(%)"

        fcr_percentage["MTTR_HOURS"] = (
            fcr_percentage["fcr_percentage"]
        )

        fcr_percentage["TARGET_HRS_HRS"] = ">=80 %"

        fcr_percentage["STATUS"] = np.where(
            fcr_percentage["fcr_percentage"] >= 80,
            "Met",
            "Not Met"
        )

        fcr_percentage = fcr_percentage[
            [
                "METRIC",
                "agent",
                "MTTR_HOURS",
                "TARGET_HRS_HRS",
                "STATUS"
            ]
        ]

        # =========================================================
        # 4. FCR COUNT
        # =========================================================

        fcr_count = fcr_df[
            [
                "agent",
                "fcr_count"
            ]
        ].copy()

        fcr_count["METRIC"] = "FCR Count"

        fcr_count["MTTR_HOURS"] = (
            fcr_count["fcr_count"]
        )

        fcr_count["TARGET_HRS_HRS"] = ">=5 %"

        fcr_count["STATUS"] = np.where(
            fcr_count["fcr_count"] >= 5,
            "Met",
            "Not Met"
        )

        fcr_count = fcr_count[
            [
                "METRIC",
                "agent",
                "MTTR_HOURS",
                "TARGET_HRS_HRS",
                "STATUS"
            ]
        ]

        # =========================================================
        # 5. RESOLVED INCIDENT
        #
        # Oracle:
        #
        # NVL(CLOSED_INCIDENT_COUNT,
        #     RESOLVED_INCIDENT_COUNT)
        # =========================================================

        resolved = mttr_df[
            [
                "agent",
                "closed_incident_count",
                "resolved_incident_count"
            ]
        ].copy()

        resolved["resolved"] = (
            resolved["closed_incident_count"]
            .fillna(
                resolved["resolved_incident_count"]
            )
        )

        resolved["METRIC"] = "Resolved Incident"

        resolved["MTTR_HOURS"] = resolved["resolved"]

        resolved["TARGET_HRS_HRS"] = ">=10 %"

        resolved["STATUS"] = np.where(
            resolved["resolved"] >= 10,
            "Met",
            "Not Met"
        )

        resolved = resolved[
            [
                "METRIC",
                "agent",
                "MTTR_HOURS",
                "TARGET_HRS_HRS",
                "STATUS"
            ]
        ]

        # =========================================================
        # UNION ALL
        # =========================================================

        result = pd.concat(
            [
                mttr_result,
                sla_result,
                fcr_percentage,
                fcr_count,
                resolved
            ],
            ignore_index=True
        )

        # =========================================================
        # SORT BY AGENT
        # =========================================================

        result = (
            result
            .sort_values("agent")
            .reset_index(drop=True)
        )

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        result.rename(
            columns={
                "agent": "AGENT",
                "mttr_hours": "MTTR_HOURS",
                "TARGET_HRS_HRS": "TARGET_HRS||'HRS'"
            },
            inplace=True
        )

        # =========================================================
        # SAVE
        # =========================================================

        output_file = (
            self.project_root
            / "Artifacts"
            / "AgentDashBorad"
            / "Agent_Performance_Target_10.csv"
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        result.to_csv(
            output_file,
            index=False
        )

    def generate_agent_mttr_performance_summary(self):

        mttr = (
            self.project_root
            / "Artifacts"
            / "MetricsCalculation"
            / "AgentLevelMTTR.csv"
        )

        df = pd.read_csv(mttr)

        # Normalize column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # Map possible column-name variations
        df = df.rename(columns={
            "agent": "agent",
            "mttr_hours": "mttr_hours",
            "resolved_incident_count": "resolved_incident_count",
            "closed_incident_count": "closed_incident_count",
            "total": "total"
        })

        required_columns = [
            "agent",
            "mttr_hours",
            "resolved_incident_count",
            "closed_incident_count",
            "total"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise KeyError(
                f"Missing columns in AgentLevelMTTR.csv: {missing}. "
                f"Available columns: {list(df.columns)}"
            )

        result = df[required_columns].rename(
            columns={
                "agent": "AGENT",
                "mttr_hours": "MTTR_HOURS",
                "resolved_incident_count": "RESOLVED_INCIDENT_COUNT",
                "closed_incident_count": "CLOSED_INCIDENT_COUNT",
                "total": "TOTAL"
            }
        )

        output_file = (
            self.output_dir
            / "Agent_MTTR_Performance_Summry.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )

    def generate_agent_achievements(self):

        incident = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AchievementResults.csv"
        )

        df = pd.read_csv(incident)

        # Rename columns before normalization
        df.rename(
            columns={
                "state": "ins_state",
                "number": "number_id",
                "category": "ins_category",
                "priority": "ins_priority"
            },
            inplace=True
        )

        # Normalize column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # Numeric columns
        numeric_columns = [
            "incident_closed_points",
            "sla_points",
            "fcr_points",
            "priority_points",
            "customer_rating_points",
            "points",
            "leaderboard_rank",
            "agent_level"
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).fillna(0)

        # Clean agent names
        df["assigned_to"] = (
            df["assigned_to"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df = df[df["assigned_to"] != ""].copy()

        # =========================================================
        # XP EARNED
        # =========================================================

        xp_columns = [
            "incident_closed_points",
            "sla_points",
            "fcr_points",
            "priority_points",
            "customer_rating_points"
        ]

        for col in xp_columns:
            if col not in df.columns:
                df[col] = 0

        df["xp_earned"] = df[xp_columns].sum(axis=1)

        # =========================================================
        # AGENT SUMMARY
        # =========================================================

        summary = (
            df.groupby("assigned_to", as_index=False)
            .agg(
                xp_earned=("xp_earned", "sum"),
                total_points=("points", "sum"),
                agent_level=("agent_level", "max"),
                leaderboard_rank=("leaderboard_rank", "min")
            )
        )

        # =========================================================
        # TOTAL AGENTS
        # =========================================================

        agent_count = summary["assigned_to"].nunique()

        # =========================================================
        # RESOLVED DATE
        # =========================================================

        if "resolved_at" in df.columns:

            df["resolved_at"] = pd.to_datetime(
                df["resolved_at"],
                errors="coerce"
            )

            # =====================================================
            # ACTIVE DAYS
            # =====================================================

            active_days = (
                df[df["resolved_at"].notna()]
                [["assigned_to", "resolved_at"]]
                .copy()
            )

            active_days["activity_date"] = (
                active_days["resolved_at"].dt.normalize()
            )

            active_days = (
                active_days[
                    ["assigned_to", "activity_date"]
                ]
                .drop_duplicates()
                .sort_values(
                    ["assigned_to", "activity_date"]
                )
            )

            # =====================================================
            # STREAK
            # =====================================================

            active_days["date_diff"] = (
                active_days
                .groupby("assigned_to")["activity_date"]
                .diff()
                .dt.days
            )

            active_days["streak_group"] = (
                active_days["date_diff"]
                .ne(1)
                .groupby(active_days["assigned_to"])
                .cumsum()
            )

            streaks = (
                active_days
                .groupby(
                    [
                        "assigned_to",
                        "streak_group"
                    ]
                )
                .agg(
                    streak_days=("activity_date", "size"),
                    last_activity_date=(
                        "activity_date",
                        "max"
                    )
                )
                .reset_index()
            )

            # Most recent streak
            current_streak = (
                streaks
                .sort_values(
                    [
                        "assigned_to",
                        "last_activity_date"
                    ]
                )
                .drop_duplicates(
                    "assigned_to",
                    keep="last"
                )
                [
                    [
                        "assigned_to",
                        "streak_days"
                    ]
                ]
            )

        else:

            current_streak = pd.DataFrame(
                columns=[
                    "assigned_to",
                    "streak_days"
                ]
            )

        # =========================================================
        # MERGE STREAK
        # =========================================================

        result = summary.merge(
            current_streak,
            on="assigned_to",
            how="left"
        )

        result["streak_days"] = (
            result["streak_days"]
            .fillna(0)
            .astype(int)
        )

        # =========================================================
        # RANK
        # =========================================================

        result["leaderboard_rank"] = (
            pd.to_numeric(
                result["leaderboard_rank"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

        # IMPORTANT:
        # Use Excel formula so Excel does NOT convert 1 / 15
        # into 15-Jan.
        result["rank"] = (
            '="'
            + result["leaderboard_rank"].astype(str)
            + " / "
            + str(agent_count)
            + '"'
        )

        # =========================================================
        # FINAL OUTPUT
        # =========================================================

        result = result[
            [
                "assigned_to",
                "xp_earned",
                "rank",
                "streak_days",
                "agent_level",
                "total_points"
            ]
        ].rename(
            columns={
                "assigned_to": "AGENT",
                "xp_earned": "XP_EARNED",
                "rank": "RANK",
                "streak_days": "STREAK_DAYS",
                "agent_level": "AGENT_LEVEL",
                "total_points": "POINTS"
            }
        )

        # =========================================================
        # SAVE
        # =========================================================

        output_file = (
            self.output_dir
            / "Agent_Achievements_12.csv"
        )

        result.to_csv(
            output_file,
            index=False
        )    

    def generate_agent_shortage_points(self):

        ranking = (
            self.project_root
            / "Artifacts"
            / "DataGamification"
            / "AgentPoints.csv"
        )

        df = pd.read_csv(ranking)

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
        # HANDLE COLUMN NAME VARIATIONS
        # =========================================================

        df.rename(
            columns={
                "assigned_to": "agent",
                "points": "total_points"
            },
            inplace=True
        )

        # =========================================================
        # VALIDATE REQUIRED COLUMNS
        # =========================================================

        required_columns = [
            "agent",
            "total_points"
        ]

        missing_columns = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                f"Missing columns in AgentPoints.csv: "
                f"{missing_columns}"
            )

        # =========================================================
        # CLEAN AGENT
        # =========================================================

        df["agent"] = (
            df["agent"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        df = df[
            df["agent"] != ""
        ].copy()

        # =========================================================
        # CLEAN POINTS
        # =========================================================

        df["total_points"] = pd.to_numeric(
            df["total_points"],
            errors="coerce"
        ).fillna(0)

        # =========================================================
        # TOTAL POINTS PER AGENT
        # =========================================================

        df = (
            df.groupby(
                "agent",
                as_index=False
            )["total_points"]
            .sum()
        )

        # =========================================================
        # SORT BY POINTS
        # =========================================================

        df = (
            df.sort_values(
                "total_points",
                ascending=False
            )
            .reset_index(drop=True)
        )

        # =========================================================
        # CURRENT RANK
        #
        # Agents with the same points get the same rank.
        # Example:
        #
        # 300 -> 1
        # 300 -> 1
        # 250 -> 2
        # =========================================================

        df["current_rank"] = (
            df["total_points"]
            .rank(
                method="dense",
                ascending=False
            )
            .astype(int)
        )

        # =========================================================
        # TOTAL NUMBER OF AGENTS
        # =========================================================

        total_agents = len(df)

        # =========================================================
        # FIND NEXT HIGHER POINT VALUE
        #
        # Example:
        #
        # 300
        # 250
        # 200
        #
        # Agent with 200 points:
        # next rank = 250
        # shortage = 250 - 200 + 1 = 51
        # =========================================================

        unique_points = (
            df["total_points"]
            .drop_duplicates()
            .sort_values(
                ascending=False
            )
            .reset_index(drop=True)
        )

        next_rank_points_map = {}

        for i in range(1, len(unique_points)):

            current_points = unique_points.iloc[i]

            higher_points = unique_points.iloc[i - 1]

            next_rank_points_map[
                current_points
            ] = higher_points

        # =========================================================
        # NEXT RANK POINTS
        # =========================================================

        df["next_rank_points"] = (
            df["total_points"]
            .map(next_rank_points_map)
        )

        # =========================================================
        # POINTS REQUIRED TO REACH NEXT RANK
        #
        # +1 means the agent must overtake the other agent.
        #
        # If already rank 1 -> 0
        # =========================================================

        df["points_to_next_rank"] = np.where(
            df["current_rank"] == 1,
            0,
            (
                df["next_rank_points"]
                - df["total_points"]
                + 1
            )
        )

        df["points_to_next_rank"] = (
            pd.to_numeric(
                df["points_to_next_rank"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

        # =========================================================
        # FINAL RESULT
        # =========================================================

        result = df[
            [
                "agent",
                "total_points",
                "current_rank",
                "points_to_next_rank"
            ]
        ].copy()

        # =========================================================
        # RENAME COLUMNS
        # =========================================================

        result.rename(
            columns={
                "agent": "AGENT",
                "total_points": "TOTAL_POINTS",
                "current_rank": "CURRENT_RANK",
                "points_to_next_rank": "POINTS_TO_NEXT_RANK"
            },
            inplace=True
        )

        # =========================================================
        # EXCEL-SAFE RANK
        #
        # IMPORTANT:
        #
        # Excel can convert:
        #
        # 1 / 15
        #
        # into:
        #
        # 15-Jul
        #
        # Therefore save it as:
        #
        # ="1 / 15"
        #
        # Excel displays:
        #
        # 1 / 15
        #
        # but keeps it as TEXT.
        # =========================================================

        result["CURRENT_RANK"] = (
            '="'
            + result["CURRENT_RANK"].astype(str)
            + " / "
            + str(total_agents)
            + '"'
        )

        # =========================================================
        # FINAL COLUMN ORDER
        # =========================================================

        result = result[
            [
                "AGENT",
                "TOTAL_POINTS",
                "CURRENT_RANK",
                "POINTS_TO_NEXT_RANK"
            ]
        ]

        # =========================================================
        # OUTPUT PATH
        # =========================================================

        output_file = (
            self.output_dir
            / "Agent_Shortage_Pts_Reache_Next_Rank_13.csv"
        )

        # =========================================================
        # SAVE CSV
        # =========================================================

        result.to_csv(
            output_file,
            index=False
        )


    def generate_live_streak_agent_level(self):

       
        # ============================================================
        # LOAD DATA
        # ============================================================

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
        # ============================================================
        # REQUIRED COLUMNS
        # ============================================================

        required_columns = [
            "assigned_to",
            "opened_at",
            "sla_status",
            "fcr",
            "resolution_hours",
            "reopen_count",
            "customer_rating"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        # ============================================================
        # DATA TYPE CONVERSION
        # ============================================================

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
        )

        df["customer_rating"] = pd.to_numeric(
            df["customer_rating"],
            errors="coerce"
        )

        # ============================================================
        # DATE DEFINITIONS
        #
        # CURRENT  = Last 7 completed days
        # PREVIOUS = 7 days immediately before current period
        #
        # Same as:
        #
        # Current:
        # opened_at >= trunc(sysdate) - 7
        # opened_at <  trunc(sysdate)
        #
        # Previous:
        # opened_at >= trunc(sysdate) - 14
        # opened_at <  trunc(sysdate) - 7
        # ============================================================

        today = pd.Timestamp.now().normalize()

        current_start = today - pd.Timedelta(days=7)
        current_end = today

        previous_start = today - pd.Timedelta(days=14)
        previous_end = today - pd.Timedelta(days=7)

        # ============================================================
        # CURRENT PERIOD
        # ============================================================

        current_df = df[
            (df["opened_at"] >= current_start)
            &
            (df["opened_at"] < current_end)
        ].copy()

        # ============================================================
        # PREVIOUS PERIOD
        # ============================================================

        previous_df = df[
            (df["opened_at"] >= previous_start)
            &
            (df["opened_at"] < previous_end)
        ].copy()

        # ============================================================
        # CURRENT DATA
        # ============================================================

        if not current_df.empty:

            current_df["sla_compliant"] = (
                current_df["sla_status"]
                .astype(str)
                .str.upper()
                .eq("COMPLIANT")
                .astype(int)
            )

            current_df["reopened"] = (
                current_df["reopen_count"]
                .fillna(0)
                .gt(0)
                .astype(int)
            )

            current_data = (
                current_df
                .groupby("assigned_to")
                .agg(
                    current_total_incidents=(
                        "assigned_to",
                        "count"
                    ),

                    current_sla_compliant=(
                        "sla_compliant",
                        "sum"
                    ),

                    current_fcr=(
                        "fcr",
                        "mean"
                    ),

                    current_mttr_hours=(
                        "resolution_hours",
                        "mean"
                    ),

                    current_reopened=(
                        "reopened",
                        "sum"
                    ),

                    current_customer_rating=(
                        "customer_rating",
                        "mean"
                    )
                )
                .reset_index()
            )

            # SLA Compliance %
            current_data["current_sla_compliance"] = (
                current_data["current_sla_compliant"]
                * 100
                / current_data["current_total_incidents"]
            )

            # Reopen Rate %
            current_data["current_reopen_rate"] = (
                current_data["current_reopened"]
                * 100
                / current_data["current_total_incidents"]
            )

            current_data = current_data[
                [
                    "assigned_to",
                    "current_total_incidents",
                    "current_sla_compliance",
                    "current_fcr",
                    "current_mttr_hours",
                    "current_reopen_rate",
                    "current_customer_rating"
                ]
            ]

        else:

            current_data = pd.DataFrame(
                columns=[
                    "assigned_to",
                    "current_total_incidents",
                    "current_sla_compliance",
                    "current_fcr",
                    "current_mttr_hours",
                    "current_reopen_rate",
                    "current_customer_rating"
                ]
            )

        # ============================================================
        # PREVIOUS DATA
        # ============================================================

        if not previous_df.empty:

            previous_df["sla_compliant"] = (
                previous_df["sla_status"]
                .astype(str)
                .str.upper()
                .eq("COMPLIANT")
                .astype(int)
            )

            previous_df["reopened"] = (
                previous_df["reopen_count"]
                .fillna(0)
                .gt(0)
                .astype(int)
            )

            previous_data = (
                previous_df
                .groupby("assigned_to")
                .agg(
                    previous_total_incidents=(
                        "assigned_to",
                        "count"
                    ),

                    previous_sla_compliant=(
                        "sla_compliant",
                        "sum"
                    ),

                    previous_fcr=(
                        "fcr",
                        "mean"
                    ),

                    previous_mttr_hours=(
                        "resolution_hours",
                        "mean"
                    ),

                    previous_reopened=(
                        "reopened",
                        "sum"
                    ),

                    previous_customer_rating=(
                        "customer_rating",
                        "mean"
                    )
                )
                .reset_index()
            )

            # SLA Compliance %
            previous_data["previous_sla_compliance"] = (
                previous_data["previous_sla_compliant"]
                * 100
                / previous_data["previous_total_incidents"]
            )

            # Reopen Rate %
            previous_data["previous_reopen_rate"] = (
                previous_data["previous_reopened"]
                * 100
                / previous_data["previous_total_incidents"]
            )

            previous_data = previous_data[
                [
                    "assigned_to",
                    "previous_total_incidents",
                    "previous_sla_compliance",
                    "previous_fcr",
                    "previous_mttr_hours",
                    "previous_reopen_rate",
                    "previous_customer_rating"
                ]
            ]

        else:

            previous_data = pd.DataFrame(
                columns=[
                    "assigned_to",
                    "previous_total_incidents",
                    "previous_sla_compliance",
                    "previous_fcr",
                    "previous_mttr_hours",
                    "previous_reopen_rate",
                    "previous_customer_rating"
                ]
            )

        # ============================================================
        # ALL AGENTS FROM BOTH PERIODS
        # ============================================================

        all_agents = pd.DataFrame({
            "assigned_to": pd.concat(
                [
                    current_data["assigned_to"],
                    previous_data["assigned_to"]
                ]
            )
            .drop_duplicates()
            .reset_index(drop=True)
        })

        # ============================================================
        # JOIN CURRENT + PREVIOUS
        # ============================================================

        result = all_agents.merge(
            current_data,
            on="assigned_to",
            how="left"
        )

        result = result.merge(
            previous_data,
            on="assigned_to",
            how="left"
        )

        # ============================================================
        # NVL -> FILLNA(0)
        # ============================================================

        numeric_columns = [
            "current_total_incidents",
            "previous_total_incidents",
            "current_sla_compliance",
            "previous_sla_compliance",
            "current_fcr",
            "previous_fcr",
            "current_mttr_hours",
            "previous_mttr_hours",
            "current_reopen_rate",
            "previous_reopen_rate",
            "current_customer_rating",
            "previous_customer_rating"
        ]

        for column in numeric_columns:

            result[column] = (
                pd.to_numeric(
                    result[column],
                    errors="coerce"
                )
                .fillna(0)
            )

        # ============================================================
        # ROUND METRICS
        # ============================================================

        result[
            [
                "current_sla_compliance",
                "previous_sla_compliance",
                "current_fcr",
                "previous_fcr",
                "current_mttr_hours",
                "previous_mttr_hours",
                "current_reopen_rate",
                "previous_reopen_rate",
                "current_customer_rating",
                "previous_customer_rating"
            ]
        ] = result[
            [
                "current_sla_compliance",
                "previous_sla_compliance",
                "current_fcr",
                "previous_fcr",
                "current_mttr_hours",
                "previous_mttr_hours",
                "current_reopen_rate",
                "previous_reopen_rate",
                "current_customer_rating",
                "previous_customer_rating"
            ]
        ].round(2)

        # ============================================================
        # DATE RANGE
        # ============================================================

        result["current_date_range"] = (
            current_start.strftime("%b %d").upper()
            + " - "
            + (current_end - pd.Timedelta(days=1))
            .strftime("%b %d").upper()
        )

        result["previous_date_range"] = (
            previous_start.strftime("%b %d").upper()
            + " - "
            + (previous_end - pd.Timedelta(days=1))
            .strftime("%b %d").upper()
        )

        # ============================================================
        # PERCENTAGE CHANGE
        #
        # Same logic as Oracle:
        #
        # ((CURRENT - PREVIOUS) / PREVIOUS) * 100
        #
        # With + sign when current > previous.
        # ============================================================

        def percentage_change(current, previous):

            if previous == 0:
                return "0.00% from last 7 days"

            change = (
                (current - previous)
                * 100
                / previous
            )

            sign = "+" if current > previous else ""

            return (
                f"{sign}{change:.2f}% "
                f"from last 7 days"
            )

        # ============================================================
        # INCIDENTS % CHANGE
        # ============================================================

        result["incidents_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_total_incidents"],
                row["previous_total_incidents"]
            ),
            axis=1
        )

        # ============================================================
        # SLA COMPLIANCE % CHANGE
        # ============================================================

        result["sla_compliance_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_sla_compliance"],
                row["previous_sla_compliance"]
            ),
            axis=1
        )

        # ============================================================
        # FCR % CHANGE
        # ============================================================

        result["fcr_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_fcr"],
                row["previous_fcr"]
            ),
            axis=1
        )

        # ============================================================
        # MTTR % CHANGE
        # ============================================================

        result["mttr_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_mttr_hours"],
                row["previous_mttr_hours"]
            ),
            axis=1
        )

        # ============================================================
        # REOPEN RATE % CHANGE
        # ============================================================

        result["reopen_rate_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_reopen_rate"],
                row["previous_reopen_rate"]
            ),
            axis=1
        )

        # ============================================================
        # CUSTOMER RATING % CHANGE
        # ============================================================

        result["customer_rating_pct_change"] = result.apply(
            lambda row: percentage_change(
                row["current_customer_rating"],
                row["previous_customer_rating"]
            ),
            axis=1
        )

        # ============================================================
        # FINAL COLUMN ORDER
        # ============================================================

        result = result[
            [
                "assigned_to",

                "current_date_range",
                "previous_date_range",

                "current_total_incidents",
                "previous_total_incidents",
                "incidents_pct_change",

                "current_sla_compliance",
                "previous_sla_compliance",
                "sla_compliance_pct_change",

                "current_fcr",
                "previous_fcr",
                "fcr_pct_change",

                "current_mttr_hours",
                "previous_mttr_hours",
                "mttr_pct_change",

                "current_reopen_rate",
                "previous_reopen_rate",
                "reopen_rate_pct_change",

                "current_customer_rating",
                "previous_customer_rating",
                "customer_rating_pct_change"
            ]
        ]

        # ============================================================
        # SORT BY AGENT
        # ============================================================

        result = (
            result
            .sort_values("assigned_to")
            .reset_index(drop=True)
        )

        # ============================================================
        # SAVE CSV
        # ============================================================

        output_file = (
            self.output_dir
            / "LiveStreakAgentLevel.csv"
            )

        result.to_csv(
            output_file,
                index=False
            )

    

    

    def run(self):

        print("=" * 70)
        print("STARTING AGENT DASHBOARD")
        print("=" * 70)

        try:

            agent_header = (self.generate_agent_header() )
            print("AGENT header generate")
           
            self.generate_agent_performance_summary()
            self.generate_agent_sla_performance_summary()
            self.generate_agent_fcr_performance_summary()
            self.generate_agent_incident_by_state()
            self.generate_agent_recent_incidents()
            self.generate_agent_performance_trend()
            self.generate_agent_top_category()
            self.generate_agent_goals()
            self.generate_agent_performance_target()
            self.generate_agent_mttr_performance_summary()
            self.generate_agent_achievements()
            self.generate_agent_shortage_points()
            self.generate_live_streak_agent_level()

           # return agent_header

        except Exception as e:

            print("=" * 70)
            print(
                "AGENT DASHBOARD FAILED"
            )
            print("=" * 70)

            print(
                f"Error : {e}"
            )

            raise