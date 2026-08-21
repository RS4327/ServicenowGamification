import os
from pathlib import Path

import pandas as pd
import requests

from ServicenowGamification.Config.ConfigurationManager import *
from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sns_Oracle_Loader import IncidentDataLoader


class DataIngestion:

    def __init__(self, config: DataIngestionConfig):

        self.config = config

        # Create artifact directory
        create_directories( [self.config.root_dir])
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        config_manager=ConfigurationManager()
        self.loader = IncidentDataLoader(config_manager.get_oracle_connect_config() )

    # ================================================================
    # LOAD ALL INCIDENTS FROM SERVICENOW
    # ================================================================

    def LoadIncidents(self):

        try:

            # ========================================================
            # CONFIGURATION
            # ========================================================

            INSTANCE = self.config.source_url
            USERNAME = self.config.user_name
            PASSWORD = self.config.password

            url = (
                f"{INSTANCE}"
                "/api/now/table/incident"
            )

            print("\n")
            print("=" * 80)
            print("SERVICENOW INCIDENT DATA INGESTION")
            print("=" * 80)

            print(
                "ServiceNow URL:",
                INSTANCE
            )

            # ========================================================
            # PAGINATION CONFIGURATION
            # ========================================================

            limit = 1000

            offset = 0

            all_incidents = []

            # ========================================================
            # PAGINATION LOOP
            # ========================================================

            while True:

                print("\n" + "-" * 80)

                print(
                    f"Fetching records "
                    f"Offset={offset} "
                    f"Limit={limit}"
                )

                # ====================================================
                # QUERY
                # ====================================================

                params = {

                    # Newest incidents first
                    "sysparm_query":
                        "ORDERBYDESCopened_at",

                    # Number of records per request
                    "sysparm_limit":
                        limit,

                    # Pagination
                    "sysparm_offset":
                        offset,

                    # Return display values for reference fields
                    "sysparm_display_value":
                        "true",

                    # Return only required fields
                    "sysparm_fields":
                        ",".join([
                            "sys_id",
                            "number",
                            "opened_at",
                            "resolved_at",
                            "closed_at",
                            "state",
                            "priority",
                            "assigned_to",
                            "assignment_group",
                            "category",
                            "subcategory",
                            "short_description",
                            "description",
                            "sys_created_on",
                            "sys_updated_on",
                            "reassignment_count",
                            "reopen_count"
                        ])
                }

                # ====================================================
                # SERVICE NOW API CALL
                # ====================================================

                response = requests.get(

                    url,

                    auth=(
                        USERNAME,
                        PASSWORD
                    ),

                    headers={
                        "Accept":
                            "application/json"
                    },

                    params=params,

                    timeout=120
                )

                # ====================================================
                # CHECK RESPONSE
                # ====================================================

                response.raise_for_status()

                # ====================================================
                # READ RESPONSE
                # ====================================================

                response_data = response.json()

                incidents = response_data.get(
                    "result",
                    []
                )

                print(
                    "Records received:",
                    len(incidents)
                )

                # ====================================================
                # NO MORE RECORDS
                # ====================================================

                if not incidents:

                    print(
                        "No more records found."
                    )

                    break

                # ====================================================
                # ADD TO MASTER LIST
                # ====================================================

                all_incidents.extend(
                    incidents
                )

                print(
                    "Total records collected:",
                    len(all_incidents)
                )

                # ====================================================
                # LAST PAGE
                # ====================================================

                if len(incidents) < limit:

                    print(
                        "Last page reached."
                    )

                    break

                # ====================================================
                # NEXT PAGE
                # ====================================================

                offset += limit

            # ========================================================
            # CHECK DATA
            # ========================================================

            if not all_incidents:

                print(
                    "No incidents returned from ServiceNow."
                )

                return pd.DataFrame()

            # ========================================================
            # CONVERT TO DATAFRAME
            # ========================================================

            df = pd.json_normalize(
                all_incidents
            )

            print("\n")
            print("=" * 80)
            print("SERVICENOW DATA RECEIVED")
            print("=" * 80)

            print(
                "Total incidents:",
                len(df)
            )

            print(
                "DataFrame shape:",
                df.shape
            )

            # ========================================================
            # HANDLE REFERENCE DISPLAY VALUES
            # ========================================================

            # ServiceNow can return:
            #
            # assigned_to.display_value
            # assignment_group.display_value
            #
            # We want:
            #
            # assigned_to
            # assignment_group
            #
            # containing the human-readable names.

            reference_columns = [

                "assigned_to",

                "assignment_group"
            ]

            for column in reference_columns:

                display_column = (
                    f"{column}.display_value"
                )

                if display_column in df.columns:

                    print(
                        f"Replacing "
                        f"{column} "
                        f"with "
                        f"{display_column}"
                    )

                    df[column] = (
                        df[display_column]
                    )

                    # Remove .display_value column
                    df.drop(
                        columns=[
                            display_column
                        ],
                        inplace=True
                    )

                elif column not in df.columns:

                    # If ServiceNow didn't return the field,
                    # create an empty column.

                    df[column] = None

            # ========================================================
            # CONVERT DATE COLUMNS
            # ========================================================

            date_columns = [

                "opened_at",

                "resolved_at",

                "closed_at",

                "sys_created_on",

                "sys_updated_on"
            ]

            for column in date_columns:

                if column in df.columns:

                    df[column] = pd.to_datetime(
                        df[column],
                        errors="coerce"
                    )

            # ========================================================
            # SORT NEWEST INCIDENTS FIRST
            # ========================================================

            if "opened_at" in df.columns:

                df = df.sort_values(
                    by="opened_at",
                    ascending=False,
                    na_position="last"
                )

            # ========================================================
            # REMOVE DUPLICATE INCIDENTS
            # ========================================================

            if "sys_id" in df.columns:

                before = len(df)

                df = df.drop_duplicates(
                    subset=["sys_id"],
                    keep="first"
                )

                after = len(df)

                print(
                    "Duplicates removed:",
                    before - after
                )

            elif "number" in df.columns:

                before = len(df)

                df = df.drop_duplicates(
                    subset=["number"],
                    keep="first"
                )

                after = len(df)

                print(
                    "Duplicates removed:",
                    before - after
                )

            # ========================================================
            # DISPLAY LATEST INCIDENTS
            # ========================================================

            print("\n")
            print("=" * 80)
            print("LATEST 20 INCIDENTS")
            print("=" * 80)

            display_columns = [

                "number",

                "opened_at",

                "state",

                "priority",

                "assigned_to",

                "assignment_group"
            ]

            available_columns = [

                column

                for column in display_columns

                if column in df.columns
            ]

            print(
                df[
                    available_columns
                ].head(20).to_string(
                    index=False
                )
            )

            # ========================================================
            # DISPLAY REFERENCE FIELD COUNTS
            # ========================================================

            if "assigned_to" in df.columns:

                assigned_count = (
                    df["assigned_to"]
                    .notna()
                    .sum()
                )

                print(
                    "\nAssigned incidents:",
                    assigned_count
                )

            if "assignment_group" in df.columns:

                group_count = (
                    df["assignment_group"]
                    .notna()
                    .sum()
                )

                print(
                    "Assignment group populated:",
                    group_count
                )

            # ========================================================
            # SAVE CSV
            # ========================================================

            local_path = (self.config.local_data_file)

            self.loader.check_connection()

            if self.params.Oracle["Loader"] is None: 
                df.to_csv(local_path,index=False)
            else : 
                df.to_csv(local_path, index=False)
                #self.loader.run(df,'SAIncidents')

            print("\n")
            print("=" * 80)
            print("DATA SAVED SUCCESSFULLY")
            print("=" * 80)

            print(
                "CSV path:",
                local_path
            )

            print(
                "Total incidents:",
                len(df)
            )

            print(
                "Final DataFrame shape:",
                df.shape
            )

            print("=" * 80)

            return df

        # ============================================================
        # EXCEPTION HANDLING
        # ============================================================

        except requests.exceptions.Timeout as e:

            print(
                "ServiceNow request timed out."
            )

            print(e)

            raise

        except requests.exceptions.HTTPError as e:

            print(
                "ServiceNow HTTP error."
            )

            print(e)

            if e.response is not None:

                print(
                    "Status code:",
                    e.response.status_code
                )

                print(
                    "Response:",
                    e.response.text[:1000]
                )

            raise

        except requests.exceptions.RequestException as e:

            print(
                "ServiceNow connection failed."
            )

            print(e)

            raise

        except Exception as e:

            print(
                "ServiceNow Data Ingestion Failed."
            )

            print(
                "Error:",
                str(e)
            )

            raise