import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sns_PredictWorkLoad import PredictWorkLoad 
 
from ServicenowGamification import logger

Stage_Name='Data Predict WordLoad'

class DataPredictWorkLoadPipeLine:
    def __init__(self):
        pass
    def main(self):
        try :
            config = ConfigurationManager()
            data_predict_wrk = config.get_datapredictworkload()
            Predictwrk=PredictWorkLoad(data_predict_wrk)
            #df_load=Predictwrk.load_model()
            df=Predictwrk.datacleaning()
            df=Predictwrk.feature_engineering(df)
            df=Predictwrk.mttr(df)
            df=Predictwrk.levl(df)
            df,train_df,test_df,scaler=Predictwrk.encodings(df)
            df=Predictwrk.preprocess(df,scaler)
            df_load=Predictwrk.load_model()
            df=Predictwrk.predict_workload(df)
            df=Predictwrk.categorize_workload(df)
            df=Predictwrk.generate_recommendation(df)
            df,summary=Predictwrk.workload_summary(df)
            df=Predictwrk.save_prediction(df,summary)
        except Exception as e:
                    raise e
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataPredictWorkLoadPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e


