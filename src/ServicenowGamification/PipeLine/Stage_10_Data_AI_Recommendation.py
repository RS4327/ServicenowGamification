import os
import sys
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_AI_Recommendation import AIRecommendation
from ServicenowGamification.Components.Data_Sns_LLM_Embendings import CreateEmbedings,PromptBuilder
  
from ServicenowGamification import logger

Stage_Name='Data AI Recommendation'

class DataAIRecommendationPipeLine:
    def __init__(self):
        pass

    def main(self):
   
        log_file = open("debug_output.txt", "w")
        sys.stdout = log_file

        try:

            config = ConfigurationManager()
            data_ai_config = config.get_ai_recommendation_config()
            data_ll_config = config.get_create_embendings_config()
            llm=AIRecommendation(data_ai_config,data_ll_config)
            df_load=llm.connect_llm() 
            #df_faiss=llm.faiss_search()
            #llm.single_generate_recommendation(incident_data)
            df=llm.generate_recommendations()
        except Exception as e:
            raise e
        sys.stdout = sys.__stdout__
        log_file.close()

        print("Debug output saved.")
           
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataAIRecommendationPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
                
    except Exception as e:
        logger.info(e)
        raise e


