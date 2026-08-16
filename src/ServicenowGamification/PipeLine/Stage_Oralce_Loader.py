import os
import pandas as pd

from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sns_Oracle_Loader import IncidentDataLoader
from ServicenowGamification import logger


Stage_Name = "Oracle Database"


class DataOracleLoaderPipeLine:

    def __init__(self):
        pass
    def main(self):
        try:

            # ========================================================
            # CONFIGURATION
            # ========================================================
            config = ConfigurationManager()
            # ========================================================
            # READ PREPROCESSED CSV
            # ========================================================

            print("=" * 70)
            print("READING PREPROCESSED CSV")
            print("=" * 70)

            csv_path = (r"Artifacts\DataPreProcessing\Datapreprocessing.csv" )

            print("CSV Path:",csv_path)

            df = pd.read_csv(csv_path)
            print("CSV loaded successfully")
            print( "DataFrame shape:", df.shape)

            # ========================================================
            # ORACLE CONFIGURATION
            # ========================================================

            data_oracle_config = (config.get_oracle_connect_config())

            # ========================================================
            # CREATE ORACLE LOADER
            # ========================================================

            data_PreProcess = IncidentDataLoader(data_oracle_config)

            # ========================================================
            # LOAD DATA INTO ORACLE
            # ========================================================

            df = data_PreProcess.run(df)

            print("=" * 70)
            print("ORACLE DATA LOAD COMPLETED")
            print("=" * 70)

            return df

        except Exception as e:

            print("=" * 70)
            print("ORACLE DATABASE STAGE FAILED")
            print("=" * 70)

            print("Error:",e)

            raise


# ====================================================================
# MAIN PROGRAM
# ====================================================================

if __name__ == "__main__":

    try:
        logger.info(f">>>>>>>>>> Stage : "f"{Stage_Name} Started <<<<<<<<<<")

        obj = DataOracleLoaderPipeLine()
        df = obj.main()
        logger.info(f">>>>>>>>>> Stage : " f"{Stage_Name} Completed Successfully <<<<<<<<<<")

    except Exception as e:

        logger.error( f"Oracle stage failed: {e}")

        raise