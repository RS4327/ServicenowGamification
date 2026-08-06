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
from ServicenowGamification.PipeLine.Stage_04_Data_Gamification import DataGamificationPipeLine
from ServicenowGamification.PipeLine.Stage_05_Data_MachineLearning_Models import DataMachineLearningModelsPipeLine
from ServicenowGamification.PipeLine.Stage_06_Data_PredictSLABreach import DataPredictSLABreachPipeLine
from ServicenowGamification.PipeLine.Stage_07_Data_PredictWorkLoad import DataPredictWorkLoadPipeLine
from ServicenowGamification.PipeLine.Stage_08_Data_AgentPerformance import  DataAgentPerformancePipeLine
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
    df=obj.main(df)
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<")
          
except Exception as e:
    logger.info(e)
    raise e

print("\n")
STAGE_NAME = "Data Metrics Calculation"

try :
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Started <<<<<<<")
    obj=DataMetricsCalculationPipeLine()
    df,metrics=obj.main(df)
    logger.info(f">>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<")
        
except Exception as e:
    logger.info(e)
    raise e

STAGE_NAME = "Data Gamification"

try :
    logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
    obj=DataGamificationPipeLine()
    df=obj.main(df)
    logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
        
except Exception as e:
    logger.info(e)
    raise e

STAGE_NAME = "Data Machine Learning"

try :
    logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
    obj=DataMachineLearningModelsPipeLine()
    df=obj.main(df)
    logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
        
except Exception as e:
    logger.info(e)
    raise e

STAGE_NAME = "Data Predict SLA Breach"
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
        obj=DataPredictSLABreachPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e


STAGE_NAME='Data Predict WordLoad'
 
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
        obj=DataPredictWorkLoadPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e

STAGE_NAME='Data Agent Performance'
try :
      logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Started <<<<<<<<<<")
      obj=DataAgentPerformancePipeLine()
      df=obj.main()
      logger.info(f">>>>>>>>>> Stage : {STAGE_NAME} Completed Successfully <<<<<<<<<<")
                
except Exception as e:
    logger.info(e)
    raise e