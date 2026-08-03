import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_Gamification import Gamification
 
from ServicenowGamification import logger

Stage_Name='Data Gamification'

class DataGamificationPipeLine:
    def __init__(self):
        pass
    def main(self,df):
        try :
            config = ConfigurationManager()

            gamification_config = config.get_datagamificationconfig()

            gamification = Gamification(gamification_config)   
            print(type(df))
            df=gamification.calculate_points(df)
            print(type(df))
            df_f,df_analyst_summary=gamification.p_save(df)
            df_b=gamification.assign_badges(df_f)
            df=gamification.b_save(df_b)
            df_l=gamification.calculate_level(df)
            df=gamification.l_save(df_l)
            df_lead=gamification.generate_leaderboard(df_analyst_summary)
            df=gamification.lead_save(df_lead)
            df_ach=gamification.calculate_achievements(df_lead)
            df=gamification.ach_save(df_ach)
            df_m=gamification.generate_monthly_ranking(df_f)
            df=gamification.mon_save(df_m)
            return df_l
        except Exception as e:
            raise e

if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataGamificationPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
        
    except Exception as e:
        logger.info(e)
        raise e