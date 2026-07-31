import os
import sys
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(r"C:\Users\RSR\PYTHON\ServicenowGamification")

# Change working directory
os.chdir(PROJECT_ROOT)

# Add src folder to Python Path
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Imports
from ServicenowGamification.PipeLine.Stage_01_Data_Ingestion import DataIngestionPipeLine
 
from ServicenowGamification import logger

STAGE_NAME = "Data Ingestion"

try:
    logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")

    obj = DataIngestionPipeLine()
    df=obj.main()
    print(df)

    logger.info(
        f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<"
    )

except Exception as e:
    logger.exception(e)
    raise
