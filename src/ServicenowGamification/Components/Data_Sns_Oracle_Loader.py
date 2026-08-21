from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 
import oracledb
import numpy as np
import pandas as pd
import yaml
import os


import pandas as pd
import oracledb


class IncidentDataLoader:

    # ================================================================
    # INITIALIZATION
    # ================================================================

    def __init__(self, config:OracleConnectConfig):

        self.config = config
        self.params = Read_Yaml(PARAMS_FILE_PATH)
    # ================================================================
    # STEP 1 - CONNECT TO ORACLE
    # ================================================================

    def connect_oracle(self):

        try:

            print("=" * 70)
            print("CONNECTING TO ORACLE")
            print("=" * 70)

            connection = oracledb.connect(

                user=self.config.username,

                password=self.config.password,

                host=self.config.host,

                port=self.config.port,

                service_name=self.config.service_name

            )

            print("Oracle connection successful")

            print("Host:",self.config.host)

            print("Service:",self.config.service_name)

            return connection

        except oracledb.DatabaseError as e:

            print(f"Oracle connection failed: {e}")

            return None

        except Exception as e:

            print(f"Unexpected Oracle connection error: {e}")

            return None


       


    def update_loader_in_params(self, loader_value):

        params_file = "params.yaml"

        try:

            # Read params.yaml
            with open(params_file, "r") as file:
                params = yaml.safe_load(file)

            # Update Oracle -> Loader
            params["Oracle"]["Loader"] = loader_value

            # Write back to params.yaml
            with open(params_file, "w") as file:
                yaml.safe_dump(
                    params,
                    file,
                    sort_keys=False
                )

            print("=" * 70)
            print("PARAMS.YAML UPDATED SUCCESSFULLY")
            print("=" * 70)

            print(
                "Oracle : Loader :",
                loader_value
            )

        except Exception as e:

            print("Failed to update params.yaml")
            print("Error:", e)

            raise

    def configure_loader(self):

        print("=" * 70)
        print("CHECKING ORACLE CONNECTIVITY")
        print("=" * 70)

        connection = self.connect_oracle()

        if connection is not None:

            print("Oracle connection is available")

            # Update Params.yaml
            self.update_loader_in_params("Oracle")

            print("Loader configuration: Oracle")

            connection.close()

            return "Oracle"

        else:

            print("Oracle connection is unavailable")

            # Update Params.yaml
            self.update_loader_in_params(None)

            print("Loader configuration: None")

            return None


    # ================================================================
    # STEP 2 - PREPARE DATA
    # ================================================================

    def prepare_data(self, df):

        try:

            print("=" * 70)
            print("PREPARING DATA")
            print("=" * 70)

            # --------------------------------------------------------
            # Check DataFrame
            # --------------------------------------------------------

            if df is None:

                raise ValueError(
                    "Input DataFrame is None"
                )

            if not isinstance(df, pd.DataFrame):

                raise TypeError(
                    "Input must be a pandas DataFrame"
                )

            print(
                "Input DataFrame shape:",
                df.shape
            )

            # --------------------------------------------------------
            # Clean column names
            # --------------------------------------------------------

            df.columns = (
                df.columns
                .str.strip()
            )

            print("\nColumns received:")

            for column in df.columns:

                print(
                    " -",
                    column
                )

            # ========================================================
            # DATE COLUMNS
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
            # NUMERIC COLUMNS
            # ========================================================

            numeric_columns = [

                "reassignment_count",

                "reopen_count"

            ]

            for column in numeric_columns:

                if column in df.columns:

                    print(
                        f"\nConverting numeric column: {column}"
                    )

                    df[column] = pd.to_numeric(

                        df[column],

                        errors="coerce"

                    )

            # ========================================================
            # CONVERT NaN / NaT TO NONE
            # ========================================================

            # Pandas:
            #
            # NaN -> None
            # NaT -> None
            #
            # Python None is inserted into Oracle as NULL.

            df = df.astype(object)

            df = df.where(

                pd.notna(df),

                None

            )

            print(
                "\nNaN / NaT values converted to None"
            )

            # ========================================================
            # SHOW NULL COUNTS
            # ========================================================

            print("\nNULL values:")

            for column in df.columns:

                null_count = sum(

                    value is None

                    for value in df[column]

                )

                if null_count > 0:

                    print(

                        f"{column}: "
                        f"{null_count}"

                    )

            print(
                "\nData preparation completed"
            )

            return df

        except Exception as e:

            print(
                "Data preparation failed"
            )

            print(
                "Error:",
                e
            )

            raise

    # ================================================================
    # STEP 3 - TRUNCATE TABLE
    # ================================================================

    def truncate_table(self, connection):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("TRUNCATING INCIDENTS TABLE")
            print("=" * 70)

            cursor.execute(
                "TRUNCATE TABLE INCIDENTS"
            )

            print(
                "INCIDENTS table truncated successfully"
            )

        except Exception as e:

            print(
                "TRUNCATE failed:",
                e
            )

            raise

        finally:

            cursor.close()

    # ================================================================
    # STEP 4 - INSERT DATA
    # ================================================================

    def insert_data(self,connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING DATA INTO ORACLE")
            print("=" * 70)

            sql = """
                INSERT INTO INCIDENTS
                (
                    INCIDENT_NO,
                    OPENED_AT,
                    RESOLVED_AT,
                    CLOSED_AT,
                    INS_PRIORITY,
                    INS_STATE,
                    ASSIGNED_TO,
                    ASSIGNMENT_GROUP,
                    INS_CATEGORY,
                    SUBCATEGORY,
                    SHORT_DESCRIPTION,
                    INS_DESCRIPTION,
                    SYS_CREATED_ON,
                    SYS_UPDATED_ON,
                    REASSIGNMENT_COUNT,
                    REOPEN_COUNT
                )

                VALUES
                (
                    :1,

                    :2,

                    :3,

                    :4,

                    :5,

                    :6,

                    :7,

                    :8,

                    :9,

                    :10,

                    :11,

                    :12,

                    :13,

                    :14,

                    :15,

                    :16

                )

            """

            # ========================================================
            # CREATE RECORD LIST
            # ========================================================

            records = []

            for index, row in df.iterrows():

                try:

                    record = (

                        # ------------------------------------------------
                        # INCIDENT_NO
                        # CSV: number
                        # ------------------------------------------------

                        row.get("number"),

                        # ------------------------------------------------
                        # OPENED_AT
                        # CSV: opened_at
                        # ------------------------------------------------

                        row.get("opened_at"),

                        # ------------------------------------------------
                        # RESOLVED_AT
                        # CSV: resolved_at
                        # ------------------------------------------------

                        row.get("resolved_at"),

                        # ------------------------------------------------
                        # CLOSED_AT
                        # CSV: closed_at
                        # ------------------------------------------------

                        row.get("closed_at"),

                        # ------------------------------------------------
                        # INS_PRIORITY
                        # CSV: priority
                        # ------------------------------------------------

                        row.get("priority"),

                        # ------------------------------------------------
                        # INS_STATE
                        # CSV: state
                        # ------------------------------------------------

                        row.get("state"),

                        # ------------------------------------------------
                        # ASSIGNED_TO
                        # CSV: assigned_to
                        # ------------------------------------------------

                        row.get("assigned_to"),

                        # ------------------------------------------------
                        # ASSIGNMENT_GROUP
                        # CSV: assignment_group
                        # ------------------------------------------------

                        row.get("assignment_group"),

                        # ------------------------------------------------
                        # INS_CATEGORY
                        # CSV: category
                        # ------------------------------------------------

                        row.get("category"),

                        # ------------------------------------------------
                        # SUBCATEGORY
                        # CSV: subcategory
                        # ------------------------------------------------

                        row.get("subcategory"),

                        # ------------------------------------------------
                        # SHORT_DESCRIPTION
                        # CSV: short_description
                        # ------------------------------------------------

                        row.get("short_description"),

                        # ------------------------------------------------
                        # INS_DESCRIPTION
                        # CSV: description
                        # ------------------------------------------------

                        row.get("description"),

                        # ------------------------------------------------
                        # SYS_CREATED_ON
                        # CSV: sys_created_on
                        # ------------------------------------------------

                        row.get("sys_created_on"),

                        # ------------------------------------------------
                        # SYS_UPDATED_ON
                        # CSV: sys_updated_on
                        # ------------------------------------------------

                        row.get("sys_updated_on"),

                        # ------------------------------------------------
                        # REASSIGNMENT_COUNT
                        # CSV: reassignment_count
                        # ------------------------------------------------

                        row.get("reassignment_count"),

                        # ------------------------------------------------
                        # REOPEN_COUNT
                        # CSV: reopen_count
                        # ------------------------------------------------

                        row.get("reopen_count")

                    )

                    records.append(record)

                except Exception as e:

                    print(
                        f"Error preparing row {index}:",
                        e
                    )

                    raise

            # ========================================================
            # SHOW RECORD COUNT
            # ========================================================

            print(
                "Total records prepared:",
                len(records)
            )

            # ========================================================
            # INSERT
            # ========================================================

            if len(records) == 0:

                print(
                    "No records found. Nothing to insert."
                )

                return

            cursor.executemany(

                sql,

                records

            )

            # ========================================================
            # COMMIT
            # ========================================================

            connection.commit()

            print("=" * 70)
            print("DATA INSERTED SUCCESSFULLY")
            print("=" * 70)

            print(
                "Records inserted:",
                cursor.rowcount
            )

        except Exception as e:

            # ========================================================
            # ROLLBACK
            # ========================================================

            connection.rollback()

            print("=" * 70)
            print("INSERT FAILED")
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                e
            )

            raise

        finally:

            cursor.close()


    def insert_servicenow_incidents(self, connection, df):

        cursor = None

        try:

            print("=" * 70)
            print("INSERTING SERVICENOW INCIDENTS INTO ORACLE")
            print("=" * 70)

            print("Total records:", len(df))

            print("DataFrame columns:")
            print(df.columns.tolist())

            # ============================================================
            # CLEAN NUMBER COLUMNS
            # ============================================================

            def clean_number(value):

                if value is None:
                    return None

                if pd.isna(value):
                    return None

                try:

                    value = str(value).strip()

                    if value == "":
                        return None

                    if value.lower() in [
                        "none",
                        "null",
                        "nan",
                        "n/a",
                        "na"
                    ]:
                        return None

                    return int(float(value))

                except (ValueError, TypeError):

                    print(
                        f"Invalid NUMBER value found: {value}"
                    )

                    return None

            # ============================================================
            # CLEAN REOPEN_COUNT
            # ============================================================

            df["reopen_count"] = df["reopen_count"].apply(
                clean_number
            )

            # ============================================================
            # CLEAN REASSIGNMENT_COUNT
            # ============================================================

            df["reassignment_count"] = df[
                "reassignment_count"
            ].apply(
                clean_number
            )

            # ============================================================
            # CONVERT NaN / NaT TO None
            # ============================================================

            df = df.where(
                pd.notnull(df),
                None
            )

            # ============================================================
            # ORACLE INSERT SQL
            # ============================================================

            insert_sql = """
                INSERT INTO SERVICENOW_INCIDENTS
                (
                    SHORT_DESCRIPTION,
                    CLOSED_AT,
                    INS_DESCRIPTION,
                    SYS_UPDATED_ON,
                    REOPEN_COUNT,
                    INS_PRIORITY,
                    SYS_ID,
                    INS_NUMBER,
                    OPENED_AT,
                    RESOLVED_AT,
                    SYS_CREATED_ON,
                    INS_STATE,
                    REASSIGNMENT_COUNT,
                    INS_CATEGORY,
                    SUBCATEGORY,
                    ASSIGNMENT_GROUP_LINK,
                    ASSIGNED_TO_LINK,
                    ASSIGNMENT_GROUP,
                    ASSIGNED_TO
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10,
                    :11,
                    :12,
                    :13,
                    :14,
                    :15,
                    :16,
                    :17,
                    :18,
                    :19
                )
            """

            # ============================================================
            # PREPARE RECORDS
            # ============================================================

            records = []

            for _, row in df.iterrows():

                record = (

                    row.get("short_description"),

                    row.get("closed_at"),

                    row.get("description"),

                    row.get("sys_updated_on"),

                    row.get("reopen_count"),

                    row.get("priority"),

                    row.get("sys_id"),

                    row.get("number"),

                    row.get("opened_at"),

                    row.get("resolved_at"),

                    row.get("sys_created_on"),

                    row.get("state"),

                    row.get("reassignment_count"),

                    row.get("category"),

                    row.get("subcategory"),

                    row.get("assignment_group.link"),

                    row.get("assigned_to.link"),

                    row.get("assignment_group"),

                    row.get("assigned_to")
                )

                records.append(record)

            print(
                "Records prepared:",
                len(records)
            )

            # ============================================================
            # INSERT
            # ============================================================

            cursor = connection.cursor()

            if records:

                cursor.executemany(
                    insert_sql,
                    records
                )

                connection.commit()

                print("=" * 70)
                print(
                    "SUCCESSFULLY INSERTED:",
                    len(records),
                    "RECORDS"
                )
                print("=" * 70)

            else:

                print("No records to insert.")

        except Exception as e:

            print("=" * 70)
            print("ORACLE INSERT FAILED")
            print("=" * 70)

            print("Error:", e)

            connection.rollback()

            raise

        finally:

            if cursor is not None:
                cursor.close()
    



    def insert_agent_mttr_data(self,connection,df):

        cursor = connection.cursor()
        try:
            print("=" * 70)
            print("INSERTING AGENT LEVEL MTTR DATA INTO ORACLE")
            print("=" * 70)
            
            cursor.execute(
                            "TRUNCATE TABLE AGENT_LEVEL_MTTR"
                        )
            # ========================================================
            # ORACLE INSERT QUERY
            # ========================================================
            sql = """
                INSERT INTO AGENT_LEVEL_MTTR
                (
                    AGENT,
                    MTTR_HOURS,
                    RESOLVED_INCIDENT_COUNT,
                    CLOSED_INCIDENT_COUNT,
                    TOTAL
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5
                )

            """

            # ========================================================
            # CREATE RECORD LIST
            # ========================================================
            records = []
            for index, row in df.iterrows():
                try:
                    record = (
                        row.get("Agent"),
                        row.get("MTTR_hours"),
                        row.get("Resolved_Incident_Count"),
                        row.get("Closed_Incident_Count"),
                        row.get("Total")
                        )
                    records.append(record)

                except Exception as e:
                    print(f"Error preparing row {index}:", e)
                    raise

            # ========================================================
            # SHOW RECORD COUNT
            # ========================================================

            print("Total records prepared:", len(records))

            # ========================================================
            # INSERT
            # ========================================================

            if len(records) == 0:
                print("No records found. Nothing to insert.")
                return
            cursor.executemany(
                sql,
                records
                )

            # ========================================================
            # COMMIT
            # ========================================================
            connection.commit()

            print("=" * 70)
            print("AGENT LEVEL MTTR DATA INSERTED SUCCESSFULLY")
            print("=" * 70)

            print("Records inserted:",cursor.rowcount)
        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT LEVEL MTTR INSERT FAILED")
            print("=" * 70)
            print("Error type:",type(e).__name__)
            print("Error:",e)

            raise

        finally:
            cursor.close()

    def insert_agent_art_data(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT LEVEL ART DATA INTO ORACLE")
            print("=" * 70)

            # ------------------------------------------------------------
            # CHECK DATAFRAME
            # ------------------------------------------------------------

            print("DataFrame columns:")
            print(df.columns.tolist())

            print("\nDataFrame shape:")
            print(df.shape)

            # ------------------------------------------------------------
            # RENAME COLUMNS IF REQUIRED
            # ------------------------------------------------------------

            df = df.rename(
                columns={
                    "Assignment_Group": "ASSIGNMENT_GROUP",
                    "Agent": "AGENT",
                    "Average_Resolution_Time": "AVERAGE_RESOLUTION_TIME",
                    "Resolved_Incident_Count": "RESOLVED_INCIDENT_COUNT"
                }
            )

            required_columns = [
                "ASSIGNMENT_GROUP",
                "AGENT",
                "AVERAGE_RESOLUTION_TIME",
                "RESOLVED_INCIDENT_COUNT"
            ]

            missing_columns = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing_columns:
                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            # ------------------------------------------------------------
            # REMOVE NaN
            # ------------------------------------------------------------

            df = df.where(
                pd.notnull(df),
                None
            )

            # ------------------------------------------------------------
            # DELETE OLD DATA
            # ------------------------------------------------------------

            cursor.execute(
                "DELETE FROM AGENT_ART"
            )

            # ------------------------------------------------------------
            # INSERT SQL
            # ------------------------------------------------------------

            sql = """
                INSERT INTO AGENT_ART
                (
                    ASSIGNMENT_GROUP,
                    AGENT,
                    AVERAGE_RESOLUTION_TIME,
                    RESOLVED_INCIDENT_COUNT
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4
                )
            """

            # ------------------------------------------------------------
            # CREATE RECORDS
            # ------------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (
                    row["ASSIGNMENT_GROUP"],
                    row["AGENT"],
                    row["AVERAGE_RESOLUTION_TIME"],
                    row["RESOLVED_INCIDENT_COUNT"]
                )

                records.append(record)

            print(
                "Total records prepared:",
                len(records)
            )

            # ------------------------------------------------------------
            # SHOW SAMPLE
            # ------------------------------------------------------------

            if records:

                print(
                    "\nFirst record:"
                )

                print(records[0])

            # ------------------------------------------------------------
            # INSERT
            # ------------------------------------------------------------

            if not records:

                print(
                    "No records found. Nothing to insert."
                )

                return

            cursor.executemany(
                sql,
                records
            )

            # ------------------------------------------------------------
            # COMMIT
            # ------------------------------------------------------------

            connection.commit()

            print("=" * 70)
            print("AGENT LEVEL ART DATA INSERTED SUCCESSFULLY")
            print("=" * 70)

            print(
                "Records inserted:",
                cursor.rowcount
            )

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT LEVEL ART INSERT FAILED")
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                e
            )

            raise

        finally:

            cursor.close()

    def insert_agent_group_art_data(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING ASSIGNMENT GROUP ART DATA")
            print("=" * 70)

            print("Input shape:", df.shape)

            print("Input columns:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "Assignment_Group":
                        "ASSIGNMENT_GROUP",

                    "Average_Resolution_Time":
                        "AVERAGE_RESOLUTION_TIME",

                    "Resolved_Incident_Count":
                        "RESOLVED_INCIDENT_COUNT"
                }
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------

            required_columns = [
                "ASSIGNMENT_GROUP",
                "AVERAGE_RESOLUTION_TIME",
                "RESOLVED_INCIDENT_COUNT"
            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------

            print("\nDeleting old ASSIGNMENT_GROUP_ART data...")

            cursor.execute(
                "DELETE FROM ASSIGNMENT_GROUP_ART"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO ASSIGNMENT_GROUP_ART
                (
                    ASSIGNMENT_GROUP,
                    AVERAGE_RESOLUTION_TIME,
                    RESOLVED_INCIDENT_COUNT
                )
                VALUES
                (
                    :1,
                    :2,
                    :3
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (

                    row["ASSIGNMENT_GROUP"],

                    row["AVERAGE_RESOLUTION_TIME"],

                    row["RESOLVED_INCIDENT_COUNT"]

                )

                records.append(record)

            print(
                "\nTotal records prepared:",
                len(records)
            )

            if len(records) > 0:

                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            print("\nExecuting INSERT...")

            cursor.executemany(
                sql,
                records
            )

            print(
                "Oracle executemany completed"
            )

            print(
                "Rows inserted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM ASSIGNMENT_GROUP_ART
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print(
                "ASSIGNMENT GROUP ART INSERT SUCCESSFUL"
            )
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "ASSIGNMENT GROUP ART INSERT FAILED"
            )
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()


    def insert_overall_sla_data(self, connection, df):

        cursor = connection.cursor()

        try:
            print("=" * 70)
            print("INSERTING OVERALL SLA DATA")
            print("=" * 70)

            print("Input shape:", df.shape)

            print("Input columns:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "SLA_Met_Count":
                        "SLA_MET_COUNT",

                    "SLA_Breached_Count":
                        "SLA_BREACHED_COUNT",

                    "Total_Resolved":
                        "TOTAL_RESOLVED",

                    "SLA_Met_Percentage":
                        "SLA_MET_PERCENTAGE",

                    "SLA_Breached_Percentage":
                        "SLA_BREACHED_PERCENTAGE",

                    "SLA_Compliance":
                        "SLA_COMPLIANCE"
                }
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------

            required_columns = [

                "SLA_MET_COUNT",
                "SLA_BREACHED_COUNT",
                "TOTAL_RESOLVED",
                "SLA_MET_PERCENTAGE",
                "SLA_BREACHED_PERCENTAGE",
                "SLA_COMPLIANCE"

            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------

            print("\nDeleting old OVERALL_SLA data...")

            cursor.execute(
                "DELETE FROM OVERALL_SLA"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO OVERALL_SLA
                (
                    SLA_MET_COUNT,
                    SLA_BREACHED_COUNT,
                    TOTAL_RESOLVED,
                    SLA_MET_PERCENTAGE,
                    SLA_BREACHED_PERCENTAGE,
                    SLA_COMPLIANCE
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (

                    row["SLA_MET_COUNT"],

                    row["SLA_BREACHED_COUNT"],

                    row["TOTAL_RESOLVED"],

                    row["SLA_MET_PERCENTAGE"],

                    row["SLA_BREACHED_PERCENTAGE"],

                    row["SLA_COMPLIANCE"]

                )

                records.append(record)

            print(
                "\nTotal records prepared:",
                len(records)
            )

            if len(records) > 0:

                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            if len(records) > 0:

                print("\nExecuting INSERT...")

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Oracle executemany completed"
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records found. Nothing to insert."
                )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM OVERALL_SLA
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print(
                "OVERALL SLA INSERT SUCCESSFUL"
            )
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "OVERALL SLA INSERT FAILED"
            )
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()

    def insert_agent_level_sla_data(self, connection, df):

            cursor = connection.cursor()

            try:

                print("=" * 70)
                print("INSERTING AGENT LEVEL SLA DATA")
                print("=" * 70)

                print("Input shape:", df.shape)

                print("Input columns:")
                print(df.columns.tolist())

                # ---------------------------------------------------------
                # RENAME COLUMNS
                # ---------------------------------------------------------

                df = df.rename(
                    columns={
                        "Agent":
                            "AGENT",

                        "Total_Resolved_Incidents":
                            "TOTAL_RESOLVED_INCIDENTS",

                        "SLA_Met":
                            "SLA_MET",

                        "SLA_Breached":
                            "SLA_BREACHED",

                        "SLA_Met_Percentage":
                            "SLA_MET_PERCENTAGE",

                        "SLA_Breached_Percentage":
                            "SLA_BREACHED_PERCENTAGE",

                        "SLA_Compliance":
                            "SLA_COMPLIANCE"
                    }
                )

                print("\nColumns after rename:")
                print(df.columns.tolist())

                # ---------------------------------------------------------
                # VALIDATE
                # ---------------------------------------------------------

                required_columns = [

                    "AGENT",
                    "TOTAL_RESOLVED_INCIDENTS",
                    "SLA_MET",
                    "SLA_BREACHED",
                    "SLA_MET_PERCENTAGE",
                    "SLA_BREACHED_PERCENTAGE",
                    "SLA_COMPLIANCE"

                ]

                for column in required_columns:

                    if column not in df.columns:

                        raise ValueError(
                            f"Missing column: {column}"
                        )

                # ---------------------------------------------------------
                # NaN -> None
                # ---------------------------------------------------------

                df = df.where(
                    pd.notna(df),
                    None
                )

                # ---------------------------------------------------------
                # DELETE OLD DATA
                # ---------------------------------------------------------

                print(
                    "\nDeleting old AGENT_LEVEL_SLA data..."
                )

                cursor.execute(
                    "DELETE FROM AGENT_LEVEL_SLA"
                )

                print(
                    "Old rows deleted:",
                    cursor.rowcount
                )

                # ---------------------------------------------------------
                # INSERT SQL
                # ---------------------------------------------------------

                sql = """
                    INSERT INTO AGENT_LEVEL_SLA
                    (
                        AGENT,
                        TOTAL_RESOLVED_INCIDENTS,
                        SLA_MET,
                        SLA_BREACHED,
                        SLA_MET_PERCENTAGE,
                        SLA_BREACHED_PERCENTAGE,
                        SLA_COMPLIANCE
                    )
                    VALUES
                    (
                        :1,
                        :2,
                        :3,
                        :4,
                        :5,
                        :6,
                        :7
                    )
                """

                # ---------------------------------------------------------
                # CREATE RECORDS
                # ---------------------------------------------------------

                records = []

                for index, row in df.iterrows():

                    record = (

                        row["AGENT"],
                        row["TOTAL_RESOLVED_INCIDENTS"],
                        row["SLA_MET"],
                        row["SLA_BREACHED"],
                        row["SLA_MET_PERCENTAGE"],
                        row["SLA_BREACHED_PERCENTAGE"],
                        row["SLA_COMPLIANCE"]
                    )

                    records.append(record)

                print(
                    "\nTotal records prepared:",
                    len(records)
                )

                if len(records) > 0:

                    print(
                        "First record:",
                        records[0]
                    )

                # ---------------------------------------------------------
                # INSERT
                # ---------------------------------------------------------

                if len(records) > 0:

                    print("\nExecuting INSERT...")

                    cursor.executemany(
                        sql,
                        records
                    )

                    print(
                        "Oracle executemany completed"
                    )

                    print(
                        "Rows inserted:",
                        cursor.rowcount
                    )

                else:

                    print(
                        "No records found. Nothing to insert."
                    )

                # ---------------------------------------------------------
                # COMMIT
                # ---------------------------------------------------------

                connection.commit()

                print(
                    "Oracle COMMIT completed"
                )

                # ---------------------------------------------------------
                # VERIFY
                # ---------------------------------------------------------

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM AGENT_LEVEL_SLA
                    """
                )

                count = cursor.fetchone()[0]

                print(
                    "Rows currently in Oracle:",
                    count
                )

                print("=" * 70)
                print(
                    "AGENT LEVEL SLA INSERT SUCCESSFUL"
                )
                print("=" * 70)

            except Exception as e:

                connection.rollback()

                print("=" * 70)
                print(
                    "AGENT LEVEL SLA INSERT FAILED"
                )
                print("=" * 70)

                print(
                    "Error type:",
                    type(e).__name__
                )

                print(
                    "Error:",
                    str(e)
                )

                raise

            finally:

                cursor.close()

    def insert_overall_fcr_data(self, connection, df):

        cursor = connection.cursor()
        try:
            print("=" * 70)
            print("INSERTING OVERALL FCR DATA")
            print("=" * 70)
            print("Input shape:", df.shape)
            print("Input columns:")
            print(df.columns.tolist())
            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------
            df = df.rename(
            columns={
                "Total_Incidents":
                    "TOTAL_INCIDENTS",

                "FCR_Count":
                    "FCR_COUNT",

                "Non_FCR_Count":
                    "NON_FCR_COUNT",

                "FCR_Percentage":
                    "FCR_PERCENTAGE",

                "Non_FCR_Percentage":
                    "NON_FCR_PERCENTAGE"
            }
            )
            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------
            required_columns = [
                "TOTAL_INCIDENTS",
                "FCR_COUNT",
                "NON_FCR_COUNT",
                "FCR_PERCENTAGE",
                "NON_FCR_PERCENTAGE"
            ]
            for column in required_columns:
                if column not in df.columns:
                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )
            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------
            print(
                "\nDeleting old OVERALL_FCR data..."
            )
            cursor.execute(
                "DELETE FROM OVERALL_FCR"
            )
            print(
                "Old rows deleted:",
                cursor.rowcount
            )
            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------
            sql = """
                INSERT INTO OVERALL_FCR
                (
                    TOTAL_INCIDENTS,
                    FCR_COUNT,
                    NON_FCR_COUNT,
                    FCR_PERCENTAGE,
                    NON_FCR_PERCENTAGE
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------
            print(f" sl script {sql}")
            records = []

            for index, row in df.iterrows():

                record = (
                    row["TOTAL_INCIDENTS"],
                    row["FCR_COUNT"],
                    row["NON_FCR_COUNT"],
                    row["FCR_PERCENTAGE"],
                    row["NON_FCR_PERCENTAGE"]
                )
                records.append(record)
            print(
                "\nTotal records prepared:",
                len(records)
            )
            if len(records) > 0:
                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            if len(records) > 0:
                print("\nExecuting INSERT...")
                cursor.executemany(
                    sql,
                    records
                )
                print(
                    "Oracle executemany completed"
                )
                print(
                    "Rows inserted:",
                    cursor.rowcount
                )
            else:
                print(
                    "No records found. Nothing to insert."
                )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()
            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM OVERALL_FCR
                """
            )

            count = cursor.fetchone()[0]

            print( "Rows currently in Oracle:",count )

            print("=" * 70)

            print(
                "OVERALL FCR INSERT SUCCESSFUL"
            )

            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "OVERALL FCR INSERT FAILED"
            )
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()


    def insert_agent_level_fcr_data(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT LEVEL FCR DATA")
            print("=" * 70)

            print("Input shape:", df.shape)

            print("Input columns:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------

            df = df.rename(
                columns={

                    "Agent":
                        "AGENT",

                    "Total_Incidents":
                        "TOTAL_INCIDENTS",

                    "FCR_Count":
                        "FCR_COUNT",

                    "Non_FCR_Count":
                        "NON_FCR_COUNT",

                    "FCR_Percentage":
                        "FCR_PERCENTAGE",

                    "Non_FCR_Percentage":
                        "NON_FCR_PERCENTAGE"

                }
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------

            required_columns = [

                "AGENT",
                "TOTAL_INCIDENTS",
                "FCR_COUNT",
                "NON_FCR_COUNT",
                "FCR_PERCENTAGE",
                "NON_FCR_PERCENTAGE"

            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------

            print(
                "\nDeleting old AGENT_FCR data..."
            )

            cursor.execute(
                "DELETE FROM AGENT_FCR"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO AGENT_FCR
                (
                    AGENT,
                    TOTAL_INCIDENTS,
                    FCR_COUNT,
                    NON_FCR_COUNT,
                    FCR_PERCENTAGE,
                    NON_FCR_PERCENTAGE
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (

                    row["AGENT"],
                    row["TOTAL_INCIDENTS"],
                    row["FCR_COUNT"],
                    row["NON_FCR_COUNT"],
                    row["FCR_PERCENTAGE"],
                    row["NON_FCR_PERCENTAGE"]

                )

                records.append(record)

            print(
                "\nTotal records prepared:",
                len(records)
            )

            if len(records) > 0:

                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            if len(records) > 0:

                print("\nExecuting INSERT...")

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Oracle executemany completed"
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records found. Nothing to insert."
                )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM AGENT_FCR
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)

            print(
                "AGENT LEVEL FCR INSERT SUCCESSFUL"
            )

            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)

            print(
                "AGENT LEVEL FCR INSERT FAILED"
            )

            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()    
    

    def insert_overall_performance_metrics(self,connection,df):

        cursor = connection.cursor()
        try:

            print("=" * 70)
            print("INSERTING OVERALL PERFORMANCE METRICS")
            print("=" * 70)

            print("Input shape:", df.shape)

            print("Input columns:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------

            df = df.rename(
                columns={

                    "Total Incidents":
                        "TOTAL_INCIDENTS",

                    "Resolved Incidents":
                        "RESOLVED_INCIDENTS",

                    "Closed Incidents":
                        "CLOSED_INCIDENTS",

                    "Open Incidents":
                        "OPEN_INCIDENTS",

                    "MTTR(Hours)":
                        "MTTR_HOURS",

                    "SLA_Met_Count":
                        "SLA_MET_COUNT",

                    "SLA_Breached_Count":
                        "SLA_BREACHED_COUNT",

                    "SLA Compliance(%)":
                        "SLA_COMPLIANCE",

                    "FCR_Count":
                        "FCR_COUNT",

                    "FCR(%)":
                        "FCR"
                }
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------

            required_columns = [

                "TOTAL_INCIDENTS",
                "RESOLVED_INCIDENTS",
                "CLOSED_INCIDENTS",
                "OPEN_INCIDENTS",
                "MTTR_HOURS",
                "SLA_MET_COUNT",
                "SLA_BREACHED_COUNT",
                "SLA_COMPLIANCE",
                "FCR_COUNT",
                "FCR"

            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------

            print(
                "\nDeleting old OVERALL_PERFORMANCE_METRICS data..."
            )

            cursor.execute(
                "DELETE FROM OVERALL_PERFORMANCE_METRICS"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO OVERALL_PERFORMANCE_METRICS
                (
                    TOTAL_INCIDENTS,
                    RESOLVED_INCIDENTS,
                    CLOSED_INCIDENTS,
                    OPEN_INCIDENTS,
                    MTTR_HOURS,
                    SLA_MET_COUNT,
                    SLA_BREACHED_COUNT,
                    SLA_COMPLIANCE,
                    FCR_COUNT,
                    FCR
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (

                    row["TOTAL_INCIDENTS"],
                    row["RESOLVED_INCIDENTS"],
                    row["CLOSED_INCIDENTS"],
                    row["OPEN_INCIDENTS"],
                    row["MTTR_HOURS"],
                    row["SLA_MET_COUNT"],
                    row["SLA_BREACHED_COUNT"],
                    row["SLA_COMPLIANCE"],
                    row["FCR_COUNT"],
                    row["FCR"]

                )

                records.append(record)

            print(
                "\nTotal records prepared:",
                len(records)
            )

            if len(records) > 0:

                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            if len(records) > 0:

                print("\nExecuting INSERT...")

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Oracle executemany completed"
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records found. Nothing to insert."
                )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM OVERALL_PERFORMANCE_METRICS
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)

            print(
                "OVERALL PERFORMANCE METRICS INSERT SUCCESSFUL"
            )

            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)

            print(
                "OVERALL PERFORMANCE METRICS INSERT FAILED"
            )

            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()


    def insert_agent_performance_metrics(self,connection,df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT PERFORMANCE METRICS")
            print("=" * 70)

            print("Input shape:", df.shape)

            print("Input columns:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # RENAME COLUMNS
            # ---------------------------------------------------------

            df = df.rename(
                columns={

                    "Agent":
                        "AGENT",

                    "Total_Incidents":
                        "TOTAL_INCIDENTS",

                    "Resolved_Incidents":
                        "RESOLVED_INCIDENTS",

                    "Closed_Incidents":
                        "CLOSED_INCIDENTS",

                    "Open_Incidents":
                        "OPEN_INCIDENTS",

                    "MTTR_Hours":
                        "MTTR_HOURS",

                    "SLA_Met_Count":
                        "SLA_MET_COUNT",

                    "SLA_Breached_Count":
                        "SLA_BREACHED_COUNT",

                    "SLA_Compliance":
                        "SLA_COMPLIANCE",

                    "FCR_Count":
                        "FCR_COUNT",

                    "FCR":
                        "FCR"
                }
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ---------------------------------------------------------
            # VALIDATE
            # ---------------------------------------------------------

            required_columns = [

                "AGENT",
                "TOTAL_INCIDENTS",
                "RESOLVED_INCIDENTS",
                "CLOSED_INCIDENTS",
                "OPEN_INCIDENTS",
                "MTTR_HOURS",
                "SLA_MET_COUNT",
                "SLA_BREACHED_COUNT",
                "SLA_COMPLIANCE",
                "FCR_COUNT",
                "FCR"

            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # DELETE OLD DATA
            # ---------------------------------------------------------

            print(
                "\nDeleting old AGENT_PERFORMANCE_METRICS data..."
            )

            cursor.execute(
                "DELETE FROM AGENT_PERFORMANCE_METRICS"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # INSERT SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO AGENT_PERFORMANCE_METRICS
                (
                    AGENT,
                    TOTAL_INCIDENTS,
                    RESOLVED_INCIDENTS,
                    CLOSED_INCIDENTS,
                    OPEN_INCIDENTS,
                    MTTR_HOURS,
                    SLA_MET_COUNT,
                    SLA_BREACHED_COUNT,
                    SLA_COMPLIANCE,
                    FCR_COUNT,
                    FCR
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10,
                    :11
                )
            """

            # ---------------------------------------------------------
            # CREATE RECORDS
            # ---------------------------------------------------------

            records = []

            for index, row in df.iterrows():

                record = (

                    row["AGENT"],
                    row["TOTAL_INCIDENTS"],
                    row["RESOLVED_INCIDENTS"],
                    row["CLOSED_INCIDENTS"],
                    row["OPEN_INCIDENTS"],
                    row["MTTR_HOURS"],
                    row["SLA_MET_COUNT"],
                    row["SLA_BREACHED_COUNT"],
                    row["SLA_COMPLIANCE"],
                    row["FCR_COUNT"],
                    row["FCR"]

                )

                records.append(record)

            print(
                "\nTotal records prepared:",
                len(records)
            )

            if len(records) > 0:

                print(
                    "First record:",
                    records[0]
                )

            # ---------------------------------------------------------
            # INSERT
            # ---------------------------------------------------------

            if len(records) > 0:

                print("\nExecuting INSERT...")

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Oracle executemany completed"
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records found. Nothing to insert."
                )

            # ---------------------------------------------------------
            # COMMIT
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ---------------------------------------------------------
            # VERIFY
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM AGENT_PERFORMANCE_METRICS
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)

            print(
                "AGENT PERFORMANCE METRICS INSERT SUCCESSFUL"
            )

            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)

            print(
                "AGENT PERFORMANCE METRICS INSERT FAILED"
            )

            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()

    def insert_incident_gamification(self, connection, df):

        import pandas as pd
        import datetime

        cursor = connection.cursor()

        try:

            print("=" * 80)
            print("        INSERTING INCIDENT_GAMIFICATION")
            print("=" * 80)

            print("Input shape:", df.shape)

            # ============================================================
            # 1. RENAME DATAFRAME COLUMNS
            # ============================================================

            column_mapping = {

                "number":
                    "NUMBER_ID",

                "opened_at":
                    "OPENED_AT",

                "resolved_at":
                    "RESOLVED_AT",

                "closed_at":
                    "CLOSED_AT",

                "priority":
                    "PRIORITY",

                "state":
                    "STATE",

                "assigned_to":
                    "ASSIGNED_TO",

                "assignment_group":
                    "ASSIGNMENT_GROUP",

                "category":
                    "CATEGORY",

                "subcategory":
                    "SUBCATEGORY",

                "short_description":
                    "SHORT_DESCRIPTION",

                "description":
                    "DESCRIPTION",

                "sys_created_on":
                    "SYS_CREATED_ON",

                "sys_updated_on":
                    "SYS_UPDATED_ON",

                "reopen_count":
                    "REOPEN_COUNT",

                "reassignment_count":
                    "REASSIGNMENT_COUNT",

                "resolution_time":
                    "RESOLUTION_TIME",

                "resolution_hours":
                    "RESOLUTION_HOURS",

                "sla_status":
                    "SLA_STATUS",

                "fcr":
                    "FCR",

                "customer_rating":
                    "CUSTOMER_RATING",

                "incident_closed_points":
                    "INCIDENT_CLOSED_POINTS",

                "sla_points":
                    "SLA_POINTS",

                "fcr_points":
                    "FCR_POINTS",

                "priority_points":
                    "PRIORITY_POINTS",

                "customer_rating_points":
                    "CUSTOMER_RATING_POINTS",

                "reopen_penalty_points":
                    "REOPEN_PENALTY_POINTS",

                "reassignment_penalty_points":
                    "REASSIGNMENT_PENALTY_POINTS",

                "points":
                    "POINTS"
            }

            df = df.rename(
                columns=column_mapping
            )

            print("\nColumns after rename:")
            print(df.columns.tolist())

            # ============================================================
            # 2. REQUIRED ORACLE COLUMNS
            # ============================================================

            columns = [

                "NUMBER_ID",
                "OPENED_AT",
                "RESOLVED_AT",
                "CLOSED_AT",

                "PRIORITY",
                "STATE",

                "ASSIGNED_TO",
                "ASSIGNMENT_GROUP",

                "CATEGORY",
                "SUBCATEGORY",

                "SHORT_DESCRIPTION",
                "DESCRIPTION",

                "SYS_CREATED_ON",
                "SYS_UPDATED_ON",

                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",

                "RESOLUTION_TIME",
                "RESOLUTION_HOURS",

                "SLA_STATUS",
                "FCR",

                "CUSTOMER_RATING",

                "INCIDENT_CLOSED_POINTS",
                "SLA_POINTS",
                "FCR_POINTS",
                "PRIORITY_POINTS",
                "CUSTOMER_RATING_POINTS",
                "REOPEN_PENALTY_POINTS",
                "REASSIGNMENT_PENALTY_POINTS",

                "POINTS"
            ]

            # ============================================================
            # 3. CHECK MISSING COLUMNS
            # ============================================================

            missing_columns = [
                col
                for col in columns
                if col not in df.columns
            ]

            if missing_columns:

                raise ValueError(
                    "Missing columns: "
                    + str(missing_columns)
                )

            # ============================================================
            # 4. SELECT ONLY REQUIRED COLUMNS
            # ============================================================

            df = df[columns].copy()

            # ============================================================
            # 5. TIMESTAMP CONVERSION
            # ============================================================

            timestamp_columns = [

                "OPENED_AT",
                "RESOLVED_AT",
                "CLOSED_AT",
                "SYS_CREATED_ON",
                "SYS_UPDATED_ON"
            ]

            for col in timestamp_columns:

                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

                df[col] = df[col].apply(

                    lambda x:
                        x.to_pydatetime()
                        if pd.notna(x)
                        else None

                )

            # ============================================================
            # 6. RESOLUTION TIME
            # Oracle column is VARCHAR2
            # ============================================================

            df["RESOLUTION_TIME"] = df[
                "RESOLUTION_TIME"
            ].apply(

                lambda x:
                    str(x)
                    if pd.notna(x)
                    else None

            )

            # ============================================================
            # 7. NUMERIC COLUMNS
            # ============================================================

            numeric_columns = [

                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",

                "RESOLUTION_HOURS",

                "FCR",

                "CUSTOMER_RATING",

                "INCIDENT_CLOSED_POINTS",
                "SLA_POINTS",
                "FCR_POINTS",
                "PRIORITY_POINTS",
                "CUSTOMER_RATING_POINTS",
                "REOPEN_PENALTY_POINTS",
                "REASSIGNMENT_PENALTY_POINTS",

                "POINTS"
            ]

            for col in numeric_columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            # ============================================================
            # 8. CONVERT NUMPY VALUES TO PYTHON VALUES
            # ============================================================

            for col in numeric_columns:

                df[col] = df[col].apply(

                    lambda x:
                        None
                        if pd.isna(x)
                        else x.item()
                        if hasattr(x, "item")
                        else x

                )

            # ============================================================
            # 9. STRING COLUMNS
            # ============================================================

            string_columns = [

                "NUMBER_ID",
                "PRIORITY",
                "STATE",
                "ASSIGNED_TO",
                "ASSIGNMENT_GROUP",
                "CATEGORY",
                "SUBCATEGORY",
                "SHORT_DESCRIPTION",
                "DESCRIPTION",
                "SLA_STATUS"
            ]

            for col in string_columns:

                df[col] = df[col].apply(

                    lambda x:
                        str(x)
                        if pd.notna(x)
                        else None

                )

            # ============================================================
            # 10. FINAL NaN / NaT -> None
            # ============================================================

            df = df.astype(object)

            df = df.where(
                pd.notna(df),
                None
            )

            # ============================================================
            # 11. DEBUG DATA TYPES
            # ============================================================

            print("\nFinal Data Types")
            print("-" * 80)

            for col in columns:

                sample = df[col].dropna()

                if len(sample) > 0:

                    value = sample.iloc[0]

                    print(
                        f"{col:35} "
                        f"{type(value).__name__:20} "
                        f"{str(value)[:50]}"
                    )

                else:

                    print(
                        f"{col:35} EMPTY"
                    )

            # ============================================================
            # 12. DELETE OLD DATA
            # ============================================================

            print("\nDeleting old INCIDENT_GAMIFICATION data...")

            cursor.execute(
                """
                DELETE FROM INCIDENT_GAMIFICATION
                """
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ============================================================
            # 13. INSERT SQL
            # ============================================================

            sql = """

                INSERT INTO INCIDENT_GAMIFICATION
                (

                    NUMBER_ID,
                    OPENED_AT,
                    RESOLVED_AT,
                    CLOSED_AT,

                    PRIORITY,
                    STATE,

                    ASSIGNED_TO,
                    ASSIGNMENT_GROUP,

                    CATEGORY,
                    SUBCATEGORY,

                    SHORT_DESCRIPTION,
                    DESCRIPTION,

                    SYS_CREATED_ON,
                    SYS_UPDATED_ON,

                    REOPEN_COUNT,
                    REASSIGNMENT_COUNT,

                    RESOLUTION_TIME,
                    RESOLUTION_HOURS,

                    SLA_STATUS,
                    FCR,

                    CUSTOMER_RATING,

                    INCIDENT_CLOSED_POINTS,
                    SLA_POINTS,
                    FCR_POINTS,
                    PRIORITY_POINTS,
                    CUSTOMER_RATING_POINTS,
                    REOPEN_PENALTY_POINTS,
                    REASSIGNMENT_PENALTY_POINTS,

                    POINTS

                )

                VALUES
                (

                    :1,
                    :2,
                    :3,
                    :4,

                    :5,
                    :6,

                    :7,
                    :8,

                    :9,
                    :10,

                    :11,
                    :12,

                    :13,
                    :14,

                    :15,
                    :16,

                    :17,
                    :18,

                    :19,
                    :20,

                    :21,

                    :22,
                    :23,
                    :24,
                    :25,
                    :26,
                    :27,
                    :28,

                    :29

                )

            """

            # ============================================================
            # 14. CREATE RECORDS
            # ============================================================

            records = list(

                df.itertuples(
                    index=False,
                    name=None
                )

            )

            print(
                "\nTotal records prepared:",
                len(records)
            )

            # ============================================================
            # 15. SHOW FIRST RECORD
            # ============================================================

            if records:

                print("\nFirst record:")
                print(records[0])

                print(
                    "\nFirst record length:",
                    len(records[0])
                )

            # ============================================================
            # 16. INSERT
            # ============================================================

            if records:

                print(
                    "\nExecuting Oracle executemany..."
                )

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Oracle executemany completed"
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records found."
                )

            # ============================================================
            # 17. COMMIT
            # ============================================================

            connection.commit()

            print(
                "\nOracle COMMIT completed"
            )

            # ============================================================
            # 18. VERIFY
            # ============================================================

            cursor.execute(

                """
                SELECT COUNT(*)
                FROM INCIDENT_GAMIFICATION
                """

            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            # ============================================================
            # 19. SUCCESS
            # ============================================================

            print("=" * 80)
            print(
                "INCIDENT_GAMIFICATION INSERT SUCCESSFUL"
            )
            print("=" * 80)

        except Exception as e:

            # ============================================================
            # ROLLBACK
            # ============================================================

            connection.rollback()

            print("=" * 80)
            print(
                "INCIDENT_GAMIFICATION INSERT FAILED"
            )
            print("=" * 80)

            print(
                "Error Type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()

       

    def insert_agent_group_ranking(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT GROUP RANKING")
            print("=" * 70)

            # ============================================================
            # RENAME COLUMNS
            # ============================================================

            df = df.rename(columns={

                "Assignment_Group":
                    "ASSIGNMENT_GROUP",

                "Agent":
                    "AGENT",

                "Total_Incidents":
                    "TOTAL_INCIDENTS",

                "Total_Points":
                    "TOTAL_POINTS",

                "Average_Points":
                    "AVERAGE_POINTS",

                "Closed_Incidents":
                    "CLOSED_INCIDENTS",

                "SLA_Met_Count":
                    "SLA_MET_COUNT",

                "FCR_Count":
                    "FCR_COUNT",

                "Reopen_Count":
                    "REOPEN_COUNT",

                "Reassignment_Count":
                    "REASSIGNMENT_COUNT",

                "Group_Rank":
                    "GROUP_RANK"
            })

            # ============================================================
            # REQUIRED COLUMNS
            # ============================================================

            columns = [

                "ASSIGNMENT_GROUP",
                "AGENT",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "CLOSED_INCIDENTS",
                "SLA_MET_COUNT",
                "FCR_COUNT",
                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",
                "GROUP_RANK"
            ]

            # ============================================================
            # VALIDATE
            # ============================================================

            missing_columns = [
                col
                for col in columns
                if col not in df.columns
            ]

            if missing_columns:

                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            # ============================================================
            # SELECT REQUIRED COLUMNS
            # ============================================================

            df = df[columns].copy()

            # ============================================================
            # NaN -> NULL
            # ============================================================

            df = df.where(
                pd.notna(df),
                None
            )

            # ============================================================
            # DELETE OLD DATA
            # ============================================================

            cursor.execute(
                "DELETE FROM AGENT_GROUP_RANKING"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ============================================================
            # INSERT SQL
            # ============================================================

            sql = """
                INSERT INTO AGENT_GROUP_RANKING
                (
                    ASSIGNMENT_GROUP,
                    AGENT,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    CLOSED_INCIDENTS,
                    SLA_MET_COUNT,
                    FCR_COUNT,
                    REOPEN_COUNT,
                    REASSIGNMENT_COUNT,
                    GROUP_RANK
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10,
                    :11
                )
            """

            # ============================================================
            # CREATE RECORDS
            # ============================================================

            records = list(
                df.itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Records prepared:",
                len(records)
            )

            # ============================================================
            # INSERT
            # ============================================================

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records to insert."
                )

            # ============================================================
            # COMMIT
            # ============================================================

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ============================================================
            # VERIFY
            # ============================================================

            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM AGENT_GROUP_RANKING
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print(
                "AGENT GROUP RANKING INSERT SUCCESSFUL"
            )
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "AGENT GROUP RANKING INSERT FAILED"
            )
            print(
                "Error type:",
                type(e).__name__
            )
            print(
                "Error:",
                str(e)
            )
            print("=" * 70)

            raise

        finally:

            cursor.close()

    def insert_group_ranking(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING GROUP RANKING")
            print("=" * 70)

            # ============================================================
            # RENAME COLUMNS
            # ============================================================

            df = df.rename(columns={

                "Assignment_Group":
                    "ASSIGNMENT_GROUP",

                "Total_Incidents":
                    "TOTAL_INCIDENTS",

                "Total_Points":
                    "TOTAL_POINTS",

                "Average_Points":
                    "AVERAGE_POINTS",

                "Closed_Incidents":
                    "CLOSED_INCIDENTS",

                "SLA_Met_Count":
                    "SLA_MET_COUNT",

                "FCR_Count":
                    "FCR_COUNT",

                "Reopen_Count":
                    "REOPEN_COUNT",

                "Reassignment_Count":
                    "REASSIGNMENT_COUNT",

                "Group_Rank":
                    "GROUP_RANK"
            })

            # ============================================================
            # REQUIRED COLUMNS
            # ============================================================

            columns = [

                "ASSIGNMENT_GROUP",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "CLOSED_INCIDENTS",
                "SLA_MET_COUNT",
                "FCR_COUNT",
                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",
                "GROUP_RANK"
            ]

            # ============================================================
            # VALIDATE COLUMNS
            # ============================================================

            missing_columns = [
                col
                for col in columns
                if col not in df.columns
            ]

            if missing_columns:

                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            # ============================================================
            # SELECT REQUIRED COLUMNS
            # ============================================================

            df = df[columns].copy()

            # ============================================================
            # NaN -> NULL
            # ============================================================

            df = df.where(
                pd.notna(df),
                None
            )

            # ============================================================
            # DELETE OLD DATA
            # ============================================================

            cursor.execute(
                "DELETE FROM GROUP_RANKING"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ============================================================
            # INSERT SQL
            # ============================================================

            sql = """
                INSERT INTO GROUP_RANKING
                (
                    ASSIGNMENT_GROUP,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    CLOSED_INCIDENTS,
                    SLA_MET_COUNT,
                    FCR_COUNT,
                    REOPEN_COUNT,
                    REASSIGNMENT_COUNT,
                    GROUP_RANK
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10
                )
            """

            # ============================================================
            # CREATE RECORDS
            # ============================================================

            records = list(
                df.itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Records prepared:",
                len(records)
            )

            # ============================================================
            # INSERT
            # ============================================================

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records to insert."
                )

            # ============================================================
            # COMMIT
            # ============================================================

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ============================================================
            # VERIFY
            # ============================================================

            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM GROUP_RANKING
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print(
                "GROUP RANKING INSERT SUCCESSFUL"
            )
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "GROUP RANKING INSERT FAILED"
            )
            print(
                "Error type:",
                type(e).__name__
            )
            print(
                "Error:",
                str(e)
            )
            print("=" * 70)

            raise

        finally:

            cursor.close()

    def insert_agent_ranking(self, connection, df):

        cursor = connection.cursor()

        try:
            print("=" * 70)
            print("INSERTING AGENT RANKING")
            print("=" * 70)
            # ============================================================
            # RENAME COLUMNS
            # ============================================================
            df = df.rename(columns={
                "Agent":
                    "AGENT",

                "Total_Incidents":
                    "TOTAL_INCIDENTS",

                "Total_Points":
                    "TOTAL_POINTS",

                "Average_Points":
                    "AVERAGE_POINTS",

                "Closed_Incidents":
                    "CLOSED_INCIDENTS",

                "SLA_Met_Count":
                    "SLA_MET_COUNT",

                "FCR_Count":
                    "FCR_COUNT",

                "Reopen_Count":
                    "REOPEN_COUNT",

                "Reassignment_Count":
                    "REASSIGNMENT_COUNT",

                "Agent_Rank":
                    "AGENT_RANK"
            })

            # ============================================================
            # REQUIRED COLUMNS
            # ============================================================

            columns = [

                "AGENT",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "CLOSED_INCIDENTS",
                "SLA_MET_COUNT",
                "FCR_COUNT",
                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",
                "AGENT_RANK"
            ]

            # ============================================================
            # VALIDATE COLUMNS
            # ============================================================

            missing_columns = [
                col
                for col in columns
                if col not in df.columns
            ]

            if missing_columns:

                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            # ============================================================
            # SELECT REQUIRED COLUMNS
            # ============================================================

            df = df[columns].copy()

            # ============================================================
            # NaN -> NULL
            # ============================================================

            df = df.where(
                pd.notna(df),
                None
            )

            # ============================================================
            # DELETE OLD DATA
            # ============================================================

            cursor.execute(
                "DELETE FROM AGENT_RANKING"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ============================================================
            # INSERT SQL
            # ============================================================

            sql = """
                INSERT INTO AGENT_RANKING
                (
                    AGENT,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    CLOSED_INCIDENTS,
                    SLA_MET_COUNT,
                    FCR_COUNT,
                    REOPEN_COUNT,
                    REASSIGNMENT_COUNT,
                    AGENT_RANK
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10
                )
            """

            # ============================================================
            # CREATE RECORDS
            # ============================================================

            records = list(
                df.itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Records prepared:",
                len(records)
            )

            # ============================================================
            # INSERT
            # ============================================================

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records to insert."
                )

            # ============================================================
            # COMMIT
            # ============================================================

            connection.commit()

            print(
                "Oracle COMMIT completed"
            )

            # ============================================================
            # VERIFY
            # ============================================================

            cursor.execute(
                """
                    SELECT COUNT(*)
                    FROM AGENT_RANKING
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print(
                "AGENT RANKING INSERT SUCCESSFUL"
            )
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "AGENT RANKING INSERT FAILED"
            )
            print(
                "Error type:",
                type(e).__name__
            )
            print(
                "Error:",
                str(e)
            )
            print("=" * 70)

            raise

        finally:

            cursor.close()


    def insert_agent_performance_summary(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT PERFORMANCE SUMMARY")
            print("=" * 70)

            # ---------------------------------------------------------
            # Rename columns
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "assigned_to": "ASSIGNED_TO",
                    "total_incidents": "TOTAL_INCIDENTS",
                    "total_points": "TOTAL_POINTS",
                    "sla_met": "SLA_MET",
                    "average_resolution": "AVERAGE_RESOLUTION"
                }
            )

            # ---------------------------------------------------------
            # Validate columns
            # ---------------------------------------------------------

            required_columns = [
                "ASSIGNED_TO",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "SLA_MET",
                "AVERAGE_RESOLUTION"
            ]

            for column in required_columns:
                if column not in df.columns:
                    raise ValueError(f"Missing column: {column}")

            # ---------------------------------------------------------
            # Convert NaN -> None
            # ---------------------------------------------------------

            df = df.where(pd.notna(df), None)

            # ---------------------------------------------------------
            # Delete old data
            # ---------------------------------------------------------

            cursor.execute(
                "DELETE FROM AGENT_PERFORMANCE_SUMMARY"
            )

            print("Old rows deleted:", cursor.rowcount)

            # ---------------------------------------------------------
            # SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO AGENT_PERFORMANCE_SUMMARY
                (
                    ASSIGNED_TO,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    SLA_MET,
                    AVERAGE_RESOLUTION
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5
                )
            """

            # ---------------------------------------------------------
            # Prepare records
            # ---------------------------------------------------------

            records = list(
                df[
                    [
                        "ASSIGNED_TO",
                        "TOTAL_INCIDENTS",
                        "TOTAL_POINTS",
                        "SLA_MET",
                        "AVERAGE_RESOLUTION"
                    ]
                ].itertuples(index=False, name=None)
            )

            print("Total records:", len(records))

            # ---------------------------------------------------------
            # Insert
            # ---------------------------------------------------------

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            # ---------------------------------------------------------
            # Commit
            # ---------------------------------------------------------

            connection.commit()

            print("Commit successful")

            # ---------------------------------------------------------
            # Verify
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM AGENT_PERFORMANCE_SUMMARY
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print("AGENT PERFORMANCE SUMMARY INSERT SUCCESSFUL")
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT PERFORMANCE SUMMARY INSERT FAILED")
            print("=" * 70)

            print("Error:", str(e))

            raise

        finally:

            cursor.close()

    def insert_group_badge_summary(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT GROUP BADGE SUMMARY")
            print("=" * 70)

            # ---------------------------------------------------------
            # Rename columns
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "assignment_group": "ASSIGNMENT_GROUP",
                    "total_incidents": "TOTAL_INCIDENTS",
                    "total_points": "TOTAL_POINTS",
                    "average_points": "AVERAGE_POINTS",
                    "resolved_count": "RESOLVED_COUNT",
                    "closed_count": "CLOSED_COUNT",
                    "sla_met": "SLA_MET",
                    "sla_breached": "SLA_BREACHED",
                    "completed_count": "COMPLETED_COUNT",
                    "sla_total": "SLA_TOTAL",
                    "sla_percentage": "SLA_PERCENTAGE",
                    "fcr_count": "FCR_COUNT",
                    "fcr_total": "FCR_TOTAL",
                    "fcr_percentage": "FCR_PERCENTAGE",
                    "level": "AGENT_LEVEL",
                    "performance_badges": "PERFORMANCE_BADGES",
                    "badge_count": "BADGE_COUNT",
                    "badges": "BADGES",
                    "group_badge": "GROUP_BADGE"
                }
            )

            # ---------------------------------------------------------
            # Validate columns
            # ---------------------------------------------------------

            required_columns = [
                "ASSIGNMENT_GROUP",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "RESOLVED_COUNT",
                "CLOSED_COUNT",
                "SLA_MET",
                "SLA_BREACHED",
                "COMPLETED_COUNT",
                "SLA_TOTAL",
                "SLA_PERCENTAGE",
                "FCR_COUNT",
                "FCR_TOTAL",
                "FCR_PERCENTAGE",
                "AGENT_LEVEL",
                "PERFORMANCE_BADGES",
                "BADGE_COUNT",
                "BADGES",
                "GROUP_BADGE"
            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # Convert NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # Convert Python list/array -> string
            # Oracle columns are VARCHAR2
            # ---------------------------------------------------------

            def convert_to_string(value):

                if value is None:
                    return None

                if isinstance(value, (list, tuple, set)):
                    return str(list(value))

                return str(value)

            df["PERFORMANCE_BADGES"] = df[
                "PERFORMANCE_BADGES"
            ].apply(
                convert_to_string
            )

            df["BADGES"] = df[
                "BADGES"
            ].apply(
                convert_to_string
            )

            # ---------------------------------------------------------
            # Delete old data
            # ---------------------------------------------------------

            cursor.execute(
                """
                DELETE FROM GROUP_BADGE_SUMMARY
                """
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO GROUP_BADGE_SUMMARY
                (
                    ASSIGNMENT_GROUP,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    RESOLVED_COUNT,
                    CLOSED_COUNT,
                    SLA_MET,
                    SLA_BREACHED,
                    COMPLETED_COUNT,
                    SLA_TOTAL,
                    SLA_PERCENTAGE,
                    FCR_COUNT,
                    FCR_TOTAL,
                    FCR_PERCENTAGE,
                    AGENT_LEVEL,
                    PERFORMANCE_BADGES,
                    BADGE_COUNT,
                    BADGES,
                    GROUP_BADGE
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10,
                    :11,
                    :12,
                    :13,
                    :14,
                    :15,
                    :16,
                    :17,
                    :18,
                    :19
                )
            """

            # ---------------------------------------------------------
            # Prepare records
            # ---------------------------------------------------------

            records = list(
                df[
                    [
                        "ASSIGNMENT_GROUP",
                        "TOTAL_INCIDENTS",
                        "TOTAL_POINTS",
                        "AVERAGE_POINTS",
                        "RESOLVED_COUNT",
                        "CLOSED_COUNT",
                        "SLA_MET",
                        "SLA_BREACHED",
                        "COMPLETED_COUNT",
                        "SLA_TOTAL",
                        "SLA_PERCENTAGE",
                        "FCR_COUNT",
                        "FCR_TOTAL",
                        "FCR_PERCENTAGE",
                        "AGENT_LEVEL",
                        "PERFORMANCE_BADGES",
                        "BADGE_COUNT",
                        "BADGES",
                        "GROUP_BADGE"
                    ]
                ].itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Total records:",
                len(records)
            )

            # ---------------------------------------------------------
            # Debug - show first record
            # ---------------------------------------------------------

            if records:

                print(
                    "First record:",
                    records[0]
                )

                print(
                    "Performance badges:",
                    records[0][15],
                    type(records[0][15])
                )

                print(
                    "Badges:",
                    records[0][17],
                    type(records[0][17])
                )

            # ---------------------------------------------------------
            # Insert
            # ---------------------------------------------------------

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records to insert."
                )

            # ---------------------------------------------------------
            # Commit
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Commit successful"
            )

            # ---------------------------------------------------------
            # Verify
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM GROUP_BADGE_SUMMARY
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print("AGENT GROUP BADGE SUMMARY INSERT SUCCESSFUL")
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT GROUP BADGE SUMMARY INSERT FAILED")
            print("=" * 70)

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()
            
    def insert_agent_badge_summary(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT BADGE SUMMARY")
            print("=" * 70)

            # ---------------------------------------------------------
            # Rename columns
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "assigned_to": "ASSIGNED_TO",
                    "total_incidents": "TOTAL_INCIDENTS",
                    "total_points": "TOTAL_POINTS",
                    "average_points": "AVERAGE_POINTS",
                    "resolved_count": "RESOLVED_COUNT",
                    "closed_count": "CLOSED_COUNT",
                    "sla_met": "SLA_MET",
                    "sla_breached": "SLA_BREACHED",
                    "completed_count": "COMPLETED_COUNT",
                    "sla_total": "SLA_TOTAL",
                    "sla_percentage": "SLA_PERCENTAGE",
                    "fcr_count": "FCR_COUNT",
                    "fcr_total": "FCR_TOTAL",
                    "fcr_percentage": "FCR_PERCENTAGE",
                    "level": "AGENT_LEVEL",
                    "performance_badges": "PERFORMANCE_BADGES",
                    "badge_count": "BADGE_COUNT",
                    "badges": "BADGES",
                    "badge_descriptions": "BADGE_DESCRIPTIONS",
                    "agent_badge": "AGENT_BADGE"
                }
            )

            # ---------------------------------------------------------
            # Validate columns
            # ---------------------------------------------------------

            required_columns = [
                "ASSIGNED_TO",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "RESOLVED_COUNT",
                "CLOSED_COUNT",
                "SLA_MET",
                "SLA_BREACHED",
                "COMPLETED_COUNT",
                "SLA_TOTAL",
                "SLA_PERCENTAGE",
                "FCR_COUNT",
                "FCR_TOTAL",
                "FCR_PERCENTAGE",
                "AGENT_LEVEL",
                "PERFORMANCE_BADGES",
                "BADGE_COUNT",
                "BADGES",
                "BADGE_DESCRIPTIONS",
                "AGENT_BADGE"
            ]

            for column in required_columns:

                if column not in df.columns:

                    raise ValueError(
                        f"Missing column: {column}"
                    )

            # ---------------------------------------------------------
            # Convert NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # Convert Python list/array -> string
            # ---------------------------------------------------------

            def convert_to_string(value):

                if value is None:
                    return None

                if isinstance(value, (list, tuple, set)):
                    return str(list(value))

                return str(value)

            df["PERFORMANCE_BADGES"] = df[
                "PERFORMANCE_BADGES"
            ].apply(
                convert_to_string
            )

            df["BADGES"] = df[
                "BADGES"
            ].apply(
                convert_to_string
            )

            # ---------------------------------------------------------
            # Delete old data
            # ---------------------------------------------------------

            cursor.execute(
                """
                DELETE FROM AGENT_BADGE_SUMMARY
                """
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO AGENT_BADGE_SUMMARY
                (
                    ASSIGNED_TO,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    RESOLVED_COUNT,
                    CLOSED_COUNT,
                    SLA_MET,
                    SLA_BREACHED,
                    COMPLETED_COUNT,
                    SLA_TOTAL,
                    SLA_PERCENTAGE,
                    FCR_COUNT,
                    FCR_TOTAL,
                    FCR_PERCENTAGE,
                    AGENT_LEVEL,
                    PERFORMANCE_BADGES,
                    BADGE_COUNT,
                    BADGES,
                    BADGE_DESCRIPTIONS,
                    AGENT_BADGE
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8,
                    :9,
                    :10,
                    :11,
                    :12,
                    :13,
                    :14,
                    :15,
                    :16,
                    :17,
                    :18,
                    :19,
                    :20
                )
            """

            # ---------------------------------------------------------
            # Prepare records
            # ---------------------------------------------------------

            records = list(
                df[
                    [
                        "ASSIGNED_TO",
                        "TOTAL_INCIDENTS",
                        "TOTAL_POINTS",
                        "AVERAGE_POINTS",
                        "RESOLVED_COUNT",
                        "CLOSED_COUNT",
                        "SLA_MET",
                        "SLA_BREACHED",
                        "COMPLETED_COUNT",
                        "SLA_TOTAL",
                        "SLA_PERCENTAGE",
                        "FCR_COUNT",
                        "FCR_TOTAL",
                        "FCR_PERCENTAGE",
                        "AGENT_LEVEL",
                        "PERFORMANCE_BADGES",
                        "BADGE_COUNT",
                        "BADGES",
                        "BADGE_DESCRIPTIONS",
                        "AGENT_BADGE"
                    ]
                ].itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Total records:",
                len(records)
            )

            # ---------------------------------------------------------
            # Debug first record
            # ---------------------------------------------------------

            if records:

                print(
                    "First record:",
                    records[0]
                )

                print(
                    "Performance badges:",
                    records[0][15],
                    type(records[0][15])
                )

                print(
                    "Badges:",
                    records[0][17],
                    type(records[0][17])
                )

            # ---------------------------------------------------------
            # Insert
            # ---------------------------------------------------------

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            else:

                print(
                    "No records to insert."
                )

            # ---------------------------------------------------------
            # Commit
            # ---------------------------------------------------------

            connection.commit()

            print(
                "Commit successful"
            )

            # ---------------------------------------------------------
            # Verify
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM AGENT_BADGE_SUMMARY
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print("AGENT BADGE SUMMARY INSERT SUCCESSFUL")
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT BADGE SUMMARY INSERT FAILED")
            print("=" * 70)

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()



    def insert_group_level_summary(self, connection, df):

        cursor = connection.cursor()
        try:
            print("=" * 70)
            print("INSERTING GROUP LEVEL SUMMARY")
            print("=" * 70)

            # ---------------------------------------------------------
            # Rename columns
            # ---------------------------------------------------------

            df = df.rename(
                columns={
                    "assignment_group": "ASSIGNMENT_GROUP",
                    "total_incidents": "TOTAL_INCIDENTS",
                    "total_points": "TOTAL_POINTS",
                    "average_points": "AVERAGE_POINTS",
                    "level": "AGENT_LEVEL",
                    "level_name": "AGNET_LEVEL_NAME",
                    "points_to_next_level": "POINTS_TO_NEXT_LEVEL",
                    "level_progress": "LEVEL_PROGRESS"
                }
            )

            # ---------------------------------------------------------
            # Required columns
            # ---------------------------------------------------------

            required_columns = [
                "ASSIGNMENT_GROUP",
                "TOTAL_INCIDENTS",
                "TOTAL_POINTS",
                "AVERAGE_POINTS",
                "AGENT_LEVEL",
                "AGNET_LEVEL_NAME",
                "POINTS_TO_NEXT_LEVEL",
                "LEVEL_PROGRESS"
            ]

            missing = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing:
                raise ValueError(
                    f"Missing columns: {missing}"
                )

            # ---------------------------------------------------------
            # Convert NaN -> None
            # ---------------------------------------------------------

            df = df.where(pd.notna(df), None)

            # ---------------------------------------------------------
            # Delete old data
            # ---------------------------------------------------------

            cursor.execute(
                "DELETE FROM GROUP_LEVEL_SUMMARY"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO GROUP_LEVEL_SUMMARY
                (
                    ASSIGNMENT_GROUP,
                    TOTAL_INCIDENTS,
                    TOTAL_POINTS,
                    AVERAGE_POINTS,
                    AGENT_LEVEL,
                    AGENT_LEVEL_NAME,
                    POINTS_TO_NEXT_LEVEL,
                    LEVEL_PROGRESS
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8
                )
            """

            # ---------------------------------------------------------
            # Prepare records
            # ---------------------------------------------------------

            records = list(
                df[
                    required_columns
                ].itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Total records:",
                len(records)
            )

            # ---------------------------------------------------------
            # Insert
            # ---------------------------------------------------------

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            # ---------------------------------------------------------
            # Commit
            # ---------------------------------------------------------

            connection.commit()

            print("Commit successful")

            # ---------------------------------------------------------
            # Verify
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM GROUP_LEVEL_SUMMARY
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print("GROUP LEVEL SUMMARY INSERT SUCCESSFUL")
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("GROUP LEVEL SUMMARY INSERT FAILED")
            print("=" * 70)

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()

    def insert_agent_level_summary(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING AGENT LEVEL SUMMARY")
            print("=" * 70)

            # ---------------------------------------------------------
            # Rename DataFrame columns
            # ---------------------------------------------------------
            print('insert agent level summy ',df.columns)
            df = df.rename(
                columns={
                    "Agent": "AGENT",
                    "total_incidents": "TOTAL_INCIDENTS",
                    "points": "POINTS",
                    "average_points": "AVERAGE_POINTS",
                    "level": "AGENT_LEVEL",
                    "level_name": "AGENT_LEVEL_NAME",
                    "points_to_next_level": "POINTS_TO_NEXT_LEVEL",
                    "level_progress": "LEVEL_PROGRESS"
                }
            )

            # ---------------------------------------------------------
            # Required columns
            # ---------------------------------------------------------

            required_columns = [
                "AGENT",
                "TOTAL_INCIDENTS",
                "POINTS",
                "AVERAGE_POINTS",
                "AGENT_LEVEL",
                "AGENT_LEVEL_NAME",
                "POINTS_TO_NEXT_LEVEL",
                "LEVEL_PROGRESS"
            ]

            missing = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing:
                raise ValueError(
                    f"Missing columns: {missing}"
                )

            # ---------------------------------------------------------
            # Convert NaN -> None
            # ---------------------------------------------------------

            df = df.where(
                pd.notna(df),
                None
            )

            # ---------------------------------------------------------
            # Delete old data
            # ---------------------------------------------------------

            cursor.execute(
                "DELETE FROM AGENT_LEVEL_SUMMARY"
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # ---------------------------------------------------------
            # SQL
            # ---------------------------------------------------------

            sql = """
                INSERT INTO AGENT_LEVEL_SUMMARY
                (
                    AGENT,
                    TOTAL_INCIDENTS,
                    POINTS,
                    AVERAGE_POINTS,
                    AGENT_LEVEL,
                    AGENT_LEVEL_NAME,
                    POINTS_TO_NEXT_LEVEL,
                    LEVEL_PROGRESS
                )
                VALUES
                (
                    :1,
                    :2,
                    :3,
                    :4,
                    :5,
                    :6,
                    :7,
                    :8
                )
            """

            # ---------------------------------------------------------
            # Prepare records
            # ---------------------------------------------------------

            records = list(
                df[
                    required_columns
                ].itertuples(
                    index=False,
                    name=None
                )
            )

            print(
                "Total records:",
                len(records)
            )

            # ---------------------------------------------------------
            # Insert
            # ---------------------------------------------------------

            if records:

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            # ---------------------------------------------------------
            # Commit
            # ---------------------------------------------------------

            connection.commit()

            print("Commit successful")

            # ---------------------------------------------------------
            # Verify
            # ---------------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM AGENT_LEVEL_SUMMARY
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)
            print("AGENT LEVEL SUMMARY INSERT SUCCESSFUL")
            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print("AGENT LEVEL SUMMARY INSERT FAILED")
            print("=" * 70)

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()


    def insert_incident_gamification_final(self, connection, df):

        cursor = connection.cursor()

        try:

            print("=" * 70)
            print("INSERTING INCIDENT GAMIFICATION FINAL")
            print("=" * 70)

            # =========================================================
            # RENAME COLUMNS
            # =========================================================

            df = df.rename(
                columns={

                    "number": "NUMBER_ID",

                    "opened_at": "OPENED_AT",
                    "resolved_at": "RESOLVED_AT",
                    "closed_at": "CLOSED_AT",

                    "priority": "INS_PRIORITY",
                    "state": "INS_STATE",

                    "assigned_to": "ASSIGNED_TO",
                    "assignment_group": "ASSIGNMENT_GROUP",

                    "category": "INS_CATEGORY",
                    "subcategory": "SUBCATEGORY",

                    "short_description": "SHORT_DESCRIPTION",
                    "description": "INS_DESCRIPTION",

                    "sys_created_on": "SYS_CREATED_ON",
                    "sys_updated_on": "SYS_UPDATED_ON",

                    "reopen_count": "REOPEN_COUNT",
                    "reassignment_count": "REASSIGNMENT_COUNT",

                    "resolution_time": "RESOLUTION_TIME",
                    "resolution_hours": "RESOLUTION_HOURS",

                    "sla_status": "SLA_STATUS",
                    "fcr": "FCR",

                    "total_incidents": "TOTAL_INCIDENTS",

                    "customer_rating": "CUSTOMER_RATING",

                    "incident_closed_points":
                        "INCIDENT_CLOSED_POINTS",

                    "sla_points":
                        "SLA_POINTS",

                    "fcr_points":
                        "FCR_POINTS",

                    "priority_points":
                        "PRIORITY_POINTS",

                    "customer_rating_points":
                        "CUSTOMER_RATING_POINTS",

                    "reopen_penalty_points":
                        "REOPEN_PENALTY_POINTS",

                    "reassignment_penalty_points":
                        "REASSIGNMENT_PENALTY_POINTS",

                    "points":
                        "POINTS",

                    "average_points":
                        "AVERAGE_POINTS",

                    "average_resolution":
                        "AVERAGE_RESOLUTION",

                    "badge":
                        "BADGE",

                    "agent_badge":
                        "AGENT_BADGE",

                    "group_badge":
                        "GROUP_BADGE",

                    "overall_badge":
                        "OVERALL_BADGE",

                    "level":
                        "AGENT_LEVEL",

                    "level_name":
                        "AGENT_LEVEL_NAME",

                    "points_to_next_level":
                        "POINTS_TO_NEXT_LEVEL",

                    "level_progress":
                        "LEVEL_PROGRESS",

                    "leaderboard_rank":
                        "LEADERBOARD_RANK",

                    "achievements":
                        "ACHIEVEMENTS",

                    "achievement_count":
                        "ACHIEVEMENT_COUNT"
                }
            )

            # =========================================================
            # COLUMN ORDER
            # =========================================================

            columns = [

                "NUMBER_ID",

                "OPENED_AT",
                "RESOLVED_AT",
                "CLOSED_AT",

                "INS_PRIORITY",
                "INS_STATE",

                "ASSIGNED_TO",
                "ASSIGNMENT_GROUP",

                "INS_CATEGORY",
                "SUBCATEGORY",

                "SHORT_DESCRIPTION",
                "INS_DESCRIPTION",

                "SYS_CREATED_ON",
                "SYS_UPDATED_ON",

                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",

                "RESOLUTION_TIME",
                "RESOLUTION_HOURS",

                "SLA_STATUS",
                "FCR",

                "TOTAL_INCIDENTS",

                "CUSTOMER_RATING",

                "INCIDENT_CLOSED_POINTS",
                "SLA_POINTS",
                "FCR_POINTS",
                "PRIORITY_POINTS",
                "CUSTOMER_RATING_POINTS",
                "REOPEN_PENALTY_POINTS",
                "REASSIGNMENT_PENALTY_POINTS",

                "POINTS",

                "AVERAGE_POINTS",
                "AVERAGE_RESOLUTION",

                "BADGE",
                "AGENT_BADGE",
                "GROUP_BADGE",
                "OVERALL_BADGE",

                "AGENT_LEVEL",
                "AGENT_LEVEL_NAME",

                "POINTS_TO_NEXT_LEVEL",
                "LEVEL_PROGRESS",

                "LEADERBOARD_RANK",

                "ACHIEVEMENTS",
                "ACHIEVEMENT_COUNT"
            ]

            # =========================================================
            # VALIDATE
            # =========================================================

            missing = [
                col for col in columns
                if col not in df.columns
            ]

            if missing:
                raise ValueError(
                    f"Missing columns: {missing}"
                )

            # =========================================================
            # VARCHAR COLUMNS
            # =========================================================

            varchar_columns = {

                "NUMBER_ID",
                "INS_PRIORITY",
                "INS_STATE",
                "ASSIGNED_TO",
                "ASSIGNMENT_GROUP",
                "INS_CATEGORY",
                "SUBCATEGORY",
                "SHORT_DESCRIPTION",
                "INS_DESCRIPTION",
                "RESOLUTION_TIME",
                "SLA_STATUS",
                "BADGE",
                "AGENT_BADGE",
                "GROUP_BADGE",
                "OVERALL_BADGE",
                "AGENT_LEVEL_NAME",
                "ACHIEVEMENTS"
            }

            # =========================================================
            # NUMBER COLUMNS
            # =========================================================

            number_columns = {

                "REOPEN_COUNT",
                "REASSIGNMENT_COUNT",
                "RESOLUTION_HOURS",
                "FCR",
                "TOTAL_INCIDENTS",
                "CUSTOMER_RATING",
                "INCIDENT_CLOSED_POINTS",
                "SLA_POINTS",
                "FCR_POINTS",
                "PRIORITY_POINTS",
                "CUSTOMER_RATING_POINTS",
                "REOPEN_PENALTY_POINTS",
                "REASSIGNMENT_PENALTY_POINTS",
                "POINTS",
                "AVERAGE_POINTS",
                "AVERAGE_RESOLUTION",
                "AGENT_LEVEL",
                "POINTS_TO_NEXT_LEVEL",
                "LEVEL_PROGRESS",
                "LEADERBOARD_RANK",
                "ACHIEVEMENT_COUNT"
            }

            # =========================================================
            # CONVERT VARCHAR VALUES
            # =========================================================

            for col in varchar_columns:

                df[col] = df[col].apply(
                    lambda x:
                        None
                        if pd.isna(x)
                        else str(x)
                )

            # =========================================================
            # CONVERT NUMBER VALUES TO PYTHON FLOAT
            # =========================================================

            for col in number_columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            # =========================================================
            # CONVERT DATE COLUMNS
            # =========================================================

            date_columns = [

                "OPENED_AT",
                "RESOLVED_AT",
                "CLOSED_AT",
                "SYS_CREATED_ON",
                "SYS_UPDATED_ON"
            ]

            for col in date_columns:

                df[col] = pd.to_datetime(
                    df[col],
                    errors="coerce"
                )

            # =========================================================
            # NaN -> None
            # =========================================================

            df = df.where(
                pd.notna(df),
                None
            )

            # =========================================================
            # DELETE OLD DATA
            # =========================================================

            print(
                "\nDeleting old INCIDENT_GAMIFICATION_FINAL data..."
            )

            cursor.execute(
                """
                DELETE FROM INCIDENT_GAMIFICATION_FINAL
                """
            )

            print(
                "Old rows deleted:",
                cursor.rowcount
            )

            # =========================================================
            # INSERT SQL
            # =========================================================

            sql = """

            INSERT INTO INCIDENT_GAMIFICATION_FINAL
            (
                NUMBER_ID,

                OPENED_AT,
                RESOLVED_AT,
                CLOSED_AT,

                INS_PRIORITY,
                INS_STATE,

                ASSIGNED_TO,
                ASSIGNMENT_GROUP,

                INS_CATEGORY,
                SUBCATEGORY,

                SHORT_DESCRIPTION,
                INS_DESCRIPTION,

                SYS_CREATED_ON,
                SYS_UPDATED_ON,

                REOPEN_COUNT,
                REASSIGNMENT_COUNT,

                RESOLUTION_TIME,
                RESOLUTION_HOURS,

                SLA_STATUS,
                FCR,

                TOTAL_INCIDENTS,

                CUSTOMER_RATING,

                INCIDENT_CLOSED_POINTS,
                SLA_POINTS,
                FCR_POINTS,
                PRIORITY_POINTS,
                CUSTOMER_RATING_POINTS,
                REOPEN_PENALTY_POINTS,
                REASSIGNMENT_PENALTY_POINTS,

                POINTS,

                AVERAGE_POINTS,
                AVERAGE_RESOLUTION,

                BADGE,
                AGENT_BADGE,
                GROUP_BADGE,
                OVERALL_BADGE,

                AGENT_LEVEL,
                AGENT_LEVEL_NAME,

                POINTS_TO_NEXT_LEVEL,
                LEVEL_PROGRESS,

                LEADERBOARD_RANK,

                ACHIEVEMENTS,
                ACHIEVEMENT_COUNT
            )

            VALUES
            (
                :1,
                :2,
                :3,
                :4,
                :5,
                :6,
                :7,
                :8,
                :9,
                :10,
                :11,
                :12,
                :13,
                :14,
                :15,
                :16,
                :17,
                :18,
                :19,
                :20,
                :21,
                :22,
                :23,
                :24,
                :25,
                :26,
                :27,
                :28,
                :29,
                :30,
                :31,
                :32,
                :33,
                :34,
                :35,
                :36,
                :37,
                :38,
                :39,
                :40,
                :41,
                :42,
                :43 
            )
            """

            # =========================================================
            # PREPARE PYTHON NATIVE RECORDS
            # =========================================================

            records = []

            for row_index, row in df.iterrows():

                record = []

                for col in columns:

                    value = row[col]

                    # -----------------------------------------------
                    # NULL
                    # -----------------------------------------------

                    if value is None or pd.isna(value):

                        value = None

                    # -----------------------------------------------
                    # VARCHAR
                    # -----------------------------------------------

                    elif col in varchar_columns:

                        value = str(value)

                    # -----------------------------------------------
                    # NUMBER
                    # -----------------------------------------------

                    elif col in number_columns:

                        value = float(value)

                    # -----------------------------------------------
                    # DATE
                    # -----------------------------------------------

                    elif col in date_columns:

                        if isinstance(value, pd.Timestamp):

                            value = value.to_pydatetime()

                    record.append(value)

                records.append(
                    tuple(record)
                )

            print(
                "\nTotal records prepared:",
                len(records)
            )

            # =========================================================
            # CHECK DATA TYPES BEFORE INSERT
            # =========================================================

            print("\nChecking Python data types...")

            for row_number, record in enumerate(records):

                for position, value in enumerate(record):

                    column_name = columns[position]

                    if (
                        column_name in varchar_columns
                        and value is not None
                        and not isinstance(value, str)
                    ):

                        print(
                            "ERROR FOUND"
                        )

                        print(
                            "Row:",
                            row_number
                        )

                        print(
                            "Column:",
                            column_name
                        )

                        print(
                            "Value:",
                            value
                        )

                        print(
                            "Python type:",
                            type(value)
                        )

                        raise TypeError(
                            f"VARCHAR column {column_name} "
                            f"contains {type(value)}"
                        )

            print(
                "Data type validation successful."
            )

            # =========================================================
            # IMPORTANT:
            # EXPLICIT ORACLE BIND TYPES
            # =========================================================

            cursor.setinputsizes(

                oracledb.DB_TYPE_VARCHAR,      # 1 NUMBER_ID

                oracledb.DB_TYPE_TIMESTAMP,    # 2 OPENED_AT
                oracledb.DB_TYPE_TIMESTAMP,    # 3 RESOLVED_AT
                oracledb.DB_TYPE_TIMESTAMP,    # 4 CLOSED_AT

                oracledb.DB_TYPE_VARCHAR,      # 5 INS_PRIORITY
                oracledb.DB_TYPE_VARCHAR,      # 6 INS_STATE

                oracledb.DB_TYPE_VARCHAR,      # 7 ASSIGNED_TO
                oracledb.DB_TYPE_VARCHAR,      # 8 ASSIGNMENT_GROUP

                oracledb.DB_TYPE_VARCHAR,      # 9 INS_CATEGORY
                oracledb.DB_TYPE_VARCHAR,      # 10 SUBCATEGORY

                oracledb.DB_TYPE_VARCHAR,      # 11 SHORT_DESCRIPTION
                oracledb.DB_TYPE_VARCHAR,      # 12 INS_DESCRIPTION

                oracledb.DB_TYPE_TIMESTAMP,    # 13 SYS_CREATED_ON
                oracledb.DB_TYPE_TIMESTAMP,    # 14 SYS_UPDATED_ON

                oracledb.DB_TYPE_NUMBER,       # 15 REOPEN_COUNT
                oracledb.DB_TYPE_NUMBER,       # 16 REASSIGNMENT_COUNT

                oracledb.DB_TYPE_VARCHAR,      # 17 RESOLUTION_TIME
                oracledb.DB_TYPE_NUMBER,       # 18 RESOLUTION_HOURS

                oracledb.DB_TYPE_VARCHAR,      # 19 SLA_STATUS
                oracledb.DB_TYPE_NUMBER,       # 20 FCR

                oracledb.DB_TYPE_NUMBER,       # 21 TOTAL_INCIDENTS

                oracledb.DB_TYPE_NUMBER,       # 22 CUSTOMER_RATING

                oracledb.DB_TYPE_NUMBER,       # 23 INCIDENT_CLOSED_POINTS
                oracledb.DB_TYPE_NUMBER,       # 24 SLA_POINTS
                oracledb.DB_TYPE_NUMBER,       # 25 FCR_POINTS
                oracledb.DB_TYPE_NUMBER,       # 26 PRIORITY_POINTS
                oracledb.DB_TYPE_NUMBER,       # 27 CUSTOMER_RATING_POINTS
                oracledb.DB_TYPE_NUMBER,       # 28 REOPEN_PENALTY_POINTS
                oracledb.DB_TYPE_NUMBER,       # 29 REASSIGNMENT_PENALTY_POINTS

                oracledb.DB_TYPE_NUMBER,       # 30 POINTS

                oracledb.DB_TYPE_NUMBER,       # 31 AVERAGE_POINTS
                oracledb.DB_TYPE_NUMBER,       # 32 AVERAGE_RESOLUTION

                oracledb.DB_TYPE_VARCHAR,      # 33 BADGE
                oracledb.DB_TYPE_VARCHAR,      # 34 AGENT_BADGE
                oracledb.DB_TYPE_VARCHAR,      # 35 GROUP_BADGE
                oracledb.DB_TYPE_VARCHAR,      # 36 OVERALL_BADGE

                oracledb.DB_TYPE_NUMBER,       # 37 AGENT_LEVEL
                oracledb.DB_TYPE_VARCHAR,      # 38 AGENT_LEVEL_NAME

                oracledb.DB_TYPE_NUMBER,       # 39 POINTS_TO_NEXT_LEVEL
                oracledb.DB_TYPE_NUMBER,       # 40 LEVEL_PROGRESS

                oracledb.DB_TYPE_NUMBER,       # 41 LEADERBOARD_RANK

                oracledb.DB_TYPE_VARCHAR,      # 42 ACHIEVEMENTS
                oracledb.DB_TYPE_NUMBER        # 43 ACHIEVEMENT_COUNT
            )

            # =========================================================
            # INSERT
            # =========================================================

            if records:

                print(
                    "\nExecuting Oracle INSERT..."
                )

                cursor.executemany(
                    sql,
                    records
                )

                print(
                    "Rows inserted:",
                    cursor.rowcount
                )

            # =========================================================
            # COMMIT
            # =========================================================

            connection.commit()

            print(
                "\nOracle COMMIT successful."
            )

            # =========================================================
            # VERIFY
            # =========================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM INCIDENT_GAMIFICATION_FINAL
                """
            )

            count = cursor.fetchone()[0]

            print(
                "Rows currently in Oracle:",
                count
            )

            print("=" * 70)

            print(
                "INCIDENT GAMIFICATION FINAL INSERT SUCCESSFUL"
            )

            print("=" * 70)

        except Exception as e:

            connection.rollback()

            print("=" * 70)
            print(
                "INCIDENT GAMIFICATION FINAL INSERT FAILED"
            )
            print("=" * 70)

            print(
                "Error type:",
                type(e).__name__
            )

            print(
                "Error:",
                str(e)
            )

            raise

        finally:

            cursor.close()



    def check_connection(self):

        print("Starting process...")

        oracle_available = self.configure_loader()

        if oracle_available:

            print("Oracle available")
            #print("Loader:", self.config.loader)

           # loder='Oracle'

        else:

            print("Oracle unavailable")
            #print("Loader:", self.config.loader)

            print("Skipping Oracle load.")
            #loder=None

        
    # ================================================================
    # STEP 5 - MAIN RUN METHOD
    # ================================================================
    def run(self, df,stage):
        if isinstance(df, str):
            df = pd.read_csv(df)
        else:
            df = df

        print(f"Received DataFrame - {stage}: {df.shape}")

        connection = None

        try:

            print("=" * 70)
            print("ORACLE DATA LOAD STARTED")
            print("=" * 70)

            print("Received DataFrame:",df.shape)
            
            connection = self.connect_oracle()

            print('Stage :',stage)
            if stage =='SAIncidents':
                self.insert_servicenow_incidents(connection,df)

            elif stage =='Incidents':
                print('Incidents')
                df = self.prepare_data(df)
                
                self.truncate_table(connection)

                self.insert_data(connection, df)

                print("=" * 70)
                print("ORACLE DATA LOAD COMPLETED")
                print("=" * 70)

            elif stage=='MTTR':
                print('MTTR')
                
                self.insert_agent_mttr_data(connection,df)

            elif stage=='AgentART':
                print('AgentART')
                            
                self.insert_agent_art_data(connection,df)
            elif stage=='AgentGroupART':
                print('AgentGroupART')
                                        
                self.insert_agent_group_art_data(connection,df)
            elif stage=="OverallSLA":
                self.insert_overall_sla_data(connection,df)
            elif stage == 'AgentSLA':
                self.insert_agent_level_sla_data(connection,df)
            elif stage == 'OverallFCR':
                self.insert_overall_fcr_data(connection,df)
            elif stage == 'AgentFCR':
                self.insert_agent_level_fcr_data(connection,df)
            elif stage == 'OverallMTCS':
                self.insert_overall_performance_metrics(connection,df)
            elif stage == 'AgentMTCS':
                self.insert_agent_performance_metrics(connection,df)
            # Gamification 
            elif stage == 'InsGMF':
                self.insert_incident_gamification(connection,df)
            elif stage == 'AgentGpRNK':
                self.insert_agent_group_ranking(connection,df)            
            elif stage == 'GPRNK':
                self.insert_group_ranking(connection,df)
            elif stage == 'AgentRNK':
                self.insert_agent_ranking(connection,df)
            elif stage == 'AgentPerSMRY':
                self.insert_agent_performance_summary(connection,df)
            elif stage == 'GPBdgeSMRY':
                self.insert_group_badge_summary(connection,df)
            elif stage == 'AgentBdgeSMRY':
                self.insert_agent_badge_summary(connection,df)
            elif stage == 'GPLvlSMRY':
                self.insert_group_level_summary(connection,df)
            elif stage == 'AgentLvlSMRY':
                self.insert_agent_level_summary(connection,df)
            elif stage == 'GMFNL':
                self.insert_incident_gamification_final(connection,df)



            return df

        except Exception as e:

            print("=" * 70)
            print("CSV TO ORACLE FAILED")
            print("=" * 70)

            print(
                "Error:",
                e
            )
            raise
        finally:
            if connection:
                connection.close()
                print(
                    "Oracle connection closed"
                )
    