import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_PredictSLABreach import PredictSLABreach 
 
from ServicenowGamification import logger

Stage_Name='Data Predict SLA Breach'

class DataPredictSLABreachPipeLine:
    def __init__(self):
        pass
    def main(self):
        try :
            config = ConfigurationManager()
            data_predict_mod = config.get_dataprediction()
            PredictSLAB=PredictSLABreach(data_predict_mod)
            df_load=PredictSLAB.load_model()
            df=PredictSLAB.datacleaning()
            df=PredictSLAB.mttr(df)
            df=PredictSLAB.levl(df)
            df=PredictSLAB.encodings(df)
            df=PredictSLAB.preprocess(df)
            df=PredictSLAB.predict(df)
            df=PredictSLAB.risk_level(df)
            df=PredictSLAB.recommendation(df)
            df=PredictSLAB.save_prediction(df)
        except Exception as e:
                    raise e
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataPredictSLABreachPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e
        
         