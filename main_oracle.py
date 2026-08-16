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
from ServicenowGamification.PipeLine.Stage_Oralce_Loader import DataOracleLoaderPipeLine
from ServicenowGamification import logger


log_file = open("Log_DataLLMEmbenddingsPromptBuilder.txt", "w")
sys.stdout = log_file

STAGE_NAME='Oracle Database'
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
        obj=DataOracleLoaderPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e
sys.stdout = sys.__stdout__
log_file.close()