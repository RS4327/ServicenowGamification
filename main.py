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
from ServicenowGamification.PipeLine.Stage_02_Data_PreProcessing import DataPreProcessingPipeLine
from ServicenowGamification.PipeLine.Stage_03_Data_Metricalculation import DataMetricsCalculationPipeLine
 
from ServicenowGamification import logger

STAGE_NAME = "Data Ingestion"

try:
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Started <<<<<<<")

    obj = DataIngestionPipeLine()
    df=obj.main()
    print(df)

    logger.info(
        f">>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<"
    )

except Exception as e:
    logger.exception(e)
    raise
print("\n")
STAGE_NAME = "Data Pre Processing"
try :
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Started <<<<<<<")
    #print("\n")
    obj=DataPreProcessingPipeLine()
    df=obj.main()
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<")
          
except Exception as e:
    logger.info(e)
    raise e

print("\n")
STAGE_NAME = "Data Metrics Calculation"

try :
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Started <<<<<<<")
    obj=DataMetricsCalculationPipeLine()
    df=obj.main()
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<")
        
except Exception as e:
    logger.info(e)
    raise e