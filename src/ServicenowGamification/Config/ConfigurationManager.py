import os 
from pathlib import Path
from ServicenowGamification.Utils.Common import *

from ServicenowGamification.Constant import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from ServicenowGamification.Entity.Config_Entity import  DataIngestionConfig 
from ServicenowGamification.Entity.Config_Entity import DataPreProcessingConfig
from ServicenowGamification.Entity.Config_Entity import DataMetricsCalculationConfig
from ServicenowGamification.Entity.Config_Entity import DataGamificationConfig
from ServicenowGamification.Entity.Config_Entity import DataMachineLearningModelsConfig
from ServicenowGamification.Entity.Config_Entity import DataPredictionConfig



class ConfigurationManager:
    def __init__(self,
                 CONFIG_PATH=CONFIG_FILE_PATH,
                 PARAMS_PATH=PARAMS_FILE_PATH

                 ):
         
         ROOT_DIR = Path(__file__).resolve().parents[3]
                 # Read configuration files
         #print("ROOT_DIR :", ROOT_DIR)
         
         config_path = ROOT_DIR / "Config" / "Config.yaml"
         params_path = ROOT_DIR / "Params.yaml"
         
         #print("Config Path :", config_path)
         #print("Config Exists :", config_path.exists())
         
         self.config = Read_Yaml(config_path)
         self.params = Read_Yaml(params_path)
                 
                   
         
         #print("Current Working Directory:", os.getcwd())
         
         for p in Path(".").rglob("*.yaml"):
            print("Found YAML:", p.resolve())
         create_directories([self.config.artifacts_root]) 
        # print(f"Parent Directory {self.config.artifacts_root}")

         self.Data_Ingestion = self.config.Data_Ingestion

         self.Data_PreProcessing = self.config.Data_PreProcessing
         self.Data_MetricsCalculation = self.config.Data_MetricsCalculation
         self.Data_Gamification=self.config.Data_Gamification
         self.Data_MachineLearningModels = self.config.Data_MachineLearningModels
         self.Data_Prediction = self.config.Data_Prediction
        #  print("Artifacts Root:", self.config.artifacts_root)
        #  print("Data Ingestion Root:", self.Data_Ingestion.root_dir)
        #  print("Data PreProcessing Root:", self.Data_PreProcessing.root_dir)
        #  print("Data Metrics Root:", self.Data_MetricsCalculation.root_dir)

        
    def get_data_ingestion_config(self)->DataIngestionConfig:
        Config=self.Data_Ingestion
        create_directories([Config.root_dir])
        data_ingestion_config=DataIngestionConfig(
            root_dir=Config.root_dir,
            source_url=Config.source_url,
            user_name=Config.user_name,
            password=Config.password,
            local_data_file=Config.local_data_file

        )

        return data_ingestion_config
    def get_data_preprocessing_config(self)->DataPreProcessingConfig:
             
        Config=self.Data_PreProcessing
        create_directories([Config.root_dir])
        data_preprocessingconfig=DataPreProcessingConfig(
            root_dir=Config.root_dir,
            data_path=Config.data_path,
            local_data_file=Config.local_data_file
        )
        return data_preprocessingconfig
    def get_metricscalculationconfig(self)->DataMetricsCalculationConfig:
        Config=self.Data_MetricsCalculation
        create_directories([Config.root_dir])
        data_preprocessingconfig=DataMetricsCalculationConfig(
            root_dir=Config.root_dir,
             data_path=Config.data_path,
            local_data_file=Config.local_data_file
        )
        return data_preprocessingconfig
    def get_datagamificationconfig(self)->DataGamificationConfig:
             Config=self.Data_Gamification
             create_directories([Config.root_dir])
             data_gamification_config=DataGamificationConfig(
                  root_dir =Config.root_dir,
                  data_path=Config.data_path,
                  local_data_file=Config.local_data_file,
                  incident_points=Config.incident_points,
                  analyst_points=Config.analyst_points,
                  badgeresults=Config.badgeresults,
                  badgesummary=Config.badgesummary,
                  levelresults=Config.levelresults,
                  levelsummary= Config.levelsummary,
                  leaderboardfile= Config.leaderboardfile, 
                  topfile= Config.topfile, 
                  bottomfile= Config.bottomfile,
                  teamfile= Config.teamfile,
                  groupfile= Config.groupfile ,
                  achievementfile= Config.achievementfile ,
                  summaryfile= Config.summaryfile   ,
                  monthlyranking= Config.monthlyranking ,
                  monthlytopfile= Config.monthlytopfile ,
                  monthlysummaryfile= Config.monthlysummaryfile            
             )
             return data_gamification_config
    
    def get_data_machinelearningmodels(self)->DataMachineLearningModelsConfig:
            Config=self.Data_MachineLearningModels
            create_directories([Config.root_dir])
            data_machinelearningmodels_config=DataMachineLearningModelsConfig(
                root_dir=Config.root_dir,
                data_path=Config.data_path, 
                X_train =Config.X_train, 
                X_test =Config.X_test, 
                y_train =Config.y_train, 
                y_test =Config.y_test,
                scalerpkl =Config.scalerpkl, 
                Xtrainengineered =Config.Xtrainengineered, 
                Xtestengineered =Config.Xtestengineered  
            )
            return data_machinelearningmodels_config
    def get_dataprediction(self)->DataPredictionConfig:
             Config=self.Data_Prediction
             create_directories([Config.root_dir])
             data_prediction_config=DataPredictionConfig(
                  root_dir=Config.root_dir,
                  data_path=Config.data_path,
                  model_path=Config.model_path, 
                  scaler_path =Config.scaler_path, 
                  prediction_output =Config.prediction_output, 
                  probability_threshold =Config.probability_threshold 
             )
             return data_prediction_config


