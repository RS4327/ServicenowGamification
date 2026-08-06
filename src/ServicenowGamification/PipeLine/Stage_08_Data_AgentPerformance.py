import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_AgentPerformance import AgentPerformance 
 
from ServicenowGamification import logger

Stage_Name='Data Agent Performance'

class DataAgentPerformancePipeLine:
    def __init__(self):
        pass
    def main(self):
        try :
            
            config = ConfigurationManager()
            data_agent_config = config.get_dataagentperformance()
            agentper=AgentPerformance(data_agent_config)
            #df_load=Predictwrk.load_model()
            df=agentper.datacleaning() 
            df=agentper.feature_engineering(df)
            df=agentper.mttr(df)
            df_l=agentper.levl(df)
            #df=pd.read_csv('C:\\Users\\RSR\\PYTHON\\ServicenowGamification\\Artifacts\\DataGamification\\LevelResults.csv')
            df,train_df,test_df,scaler=agentper.encodings(df_l)

            df_load=agentper.load_artifacts()
            df=agentper.preprocess(df,scaler)
            df=agentper.predict(df)
            df=agentper.categorize_performance(df)
            df=agentper.generate_recommendation(df)
            summary=agentper.performance_summary(df)
            inc_summary=agentper.performance_incident_summary(df)
            agentper.save_prediction(df,summary,inc_summary)
            # df=Predictwrk.save_prediction(df,summary)

        except Exception as e:
                    raise e
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataAgentPerformancePipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e


