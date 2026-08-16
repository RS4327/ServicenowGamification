from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 
import oracledb
import numpy as np
import pandas as pd


import pandas as pd
import oracledb


class IncidentDataLoader:

    # ================================================================
    # INITIALIZATION
    # ================================================================

    def __init__(self, config):

        self.config = config

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

            print(
                "Oracle connection successful"
            )

            print(
                "Host:",
                self.config.host
            )

            print(
                "Service:",
                self.config.service_name
            )

            return connection

        except Exception as e:

            print(
                "Oracle connection failed"
            )

            print(
                "Error:",
                e
            )

            raise

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
            if stage =='Incidents':
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
    