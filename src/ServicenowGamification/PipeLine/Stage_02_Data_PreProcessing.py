import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_DataPreProcessing import DataPreProcessing
 
from ServicenowGamification import logger


Stage_Name='Data PreProcessing'


class DataPreProcessingPipeLine:
    def __init__(self):
        pass
    def main(self,df):

        try:
            config = ConfigurationManager()
            data_preprocessing_config = config.get_data_preprocessing_config()
            data_PreProcess = DataPreProcessing(data_preprocessing_config)   # ✅ Correct
            df=data_PreProcess.Datapreprocessing(df)
            return df
            
        except Exception as e:
            raise e


if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataPreProcessingPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
        
    except Exception as e:
        logger.info(e)
        raise e
        

