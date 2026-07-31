import os
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_Ingestion import DataIngestion
from ServicenowGamification import logger



Stage_Name ="Data Ingestion"



class DataIngestionPipeLine:
    def __init__(self):
        pass
    def main(self):

        try:
            config = ConfigurationManager().get_data_ingestion_config()
            ingestion = DataIngestion(config)
            #ingestion.create_table()
            df=ingestion.LoadIncidents()
            #print(df.head())
            #return df
            
        except Exception as e:
            raise e


if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataIngestionPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
        
    except Exception as e:
        logger.info(e)
        raise e
        
