import os
#os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification/src")
from ServicenowGamification.Entity.Config_Entity import *
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager
from ServicenowGamification.Components.Data_Sng_MachineLearningModel import MachineLearningModels
 
from ServicenowGamification import logger

Stage_Name='Data Machine Learning Models'

class DataMachineLearningModelsPipeLine:
    def __init__(self):
        pass
    def main(self,df):
        try :

            config = ConfigurationManager()

            data_mlm_config = config.get_data_machinelearningmodels()

            data_mlm = MachineLearningModels(data_mlm_config)    
            df_clean=data_mlm.clean_data(df)
            df_fea=data_mlm.select_features(df_clean)
            df_enc=data_mlm.encode_features(df_fea)
            X_train,X_test,y_train, y_test=data_mlm.split_dataset(df_enc)
            data_mlm.train_test_save(X_train,X_test,y_train, y_test)
            train_df,test_df=data_mlm.create_time_features()
            train_df,test_df=data_mlm.create_interaction_features(train_df,test_df)
            train_df,test_df=data_mlm.log_transform(train_df,test_df)
            train_df,test_df,scaler=data_mlm.scale_features(train_df,test_df)
            data_mlm.save_scaler(scaler)
            data_mlm.save_dataset(train_df,test_df)
            models=data_mlm.get_models()
            ml_model_name,best_accuracy,best_model,results=data_mlm.ModelsTraining(models)
        except Exception as e:
            raise e

if __name__=="__main__":
    try :
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Started <<<<<<<<<<")
        obj=DataMachineLearningModelsPipeLine()
        df=obj.main()
        logger.info(f">>>>>>>>>> Stage : {Stage_Name} Completed Successfully <<<<<<<<<<")
        
    except Exception as e:
        logger.info(e)
        raise e

