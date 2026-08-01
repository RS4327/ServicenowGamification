import os
os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_MetricsCalculation import MetricsCalculation
 
from ServicenowGamification import logger


Stage_Name='Data Metrics Calculation'



class DataMetricsCalculationPipeLine:
    def __init__(self):
        pass
    def main(self):
        try :
            config = ConfigurationManager()

            metrics_calculation_config = config.get_metricscalculationconfig()

            metrics_calculation = MetricsCalculation(metrics_calculation_config)   
            df=metrics_calculation.MTTR()
        except Exception as e:
            raise e
        
        
if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataMetricsCalculationPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
        
    except Exception as e:
        logger.info(e)
        raise e
        

       
                
        
        
