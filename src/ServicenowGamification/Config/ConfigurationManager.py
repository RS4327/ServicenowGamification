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
from ServicenowGamification.Entity.Config_Entity import DataPredictWorkloadConfig
from ServicenowGamification.Entity.Config_Entity import DataAgentPerformanceConfig
from ServicenowGamification.Entity.Config_Entity import CreateEmbendingsConfig
from ServicenowGamification.Entity.Config_Entity import AIRecommendationConfig
from ServicenowGamification.Entity.Config_Entity import OracleConnectConfig



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
         self.Predict_Workload = self.config.Predict_Workload 
         self.Agent_Performance=self.config.Agent_Performance
         self.Create_Embeddings=self.config.Create_Embeddings
         self.AI_Recommendation=self.config.AI_Recommendations
         self.Oracle_Connect=self.config.Oracle_Connect

        
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
    
    def get_datapredictworkload(self)->DataPredictWorkloadConfig:
                 Config=self.Predict_Workload
                 create_directories([Config.root_dir])
                 data_prediction_config=DataPredictWorkloadConfig(
                      root_dir=Config.root_dir,
                      data_path=Config.data_path,
                      model_path=Config.model_path, 
                      scaler_path =Config.scaler_path, 
                      output_path =Config.output_path,                   
                      prediction_file =Config.prediction_file, 
                      high_workload =Config.high_workload, 
                      medium_workload =Config.medium_workload, 
                      low_workload =Config.low_workload, 
                 )
                 return data_prediction_config
    def get_dataagentperformance(self)->DataAgentPerformanceConfig:
               
               Config=self.Agent_Performance
               create_directories([Config.root_dir])
    
               data_agent_performance=DataAgentPerformanceConfig(
                     root_dir=Config.root_dir,
                     data_path=Config.data_path,
                     model_path=Config.model_path, 
                     scaler_path =Config.scaler_path, 
                     feature_path =Config.feature_path, 
                     achievements_path =Config.achievements_path,                  
                     output_path =Config.output_path, 
                     prediction_file =Config.prediction_file
                     
               )
               return data_agent_performance

    def get_create_embendings_config(self) -> CreateEmbendingsConfig:
        Config=self.Create_Embeddings
        create_directories([Config.root_dir])
        
        Create_Embeddings_Config=CreateEmbendingsConfig(
            root_dir=Config.root_dir,
            source_path=Config.source_path,
            faiss_index=Config.faiss_index,
            provider=Config.provider,
            model=Config.model, 
            base_url=Config.base_url, 
            temperature =Config.temperature,
            top_p =Config.top_p,
            max_tokens =Config.max_tokens, 
            timeout =Config.timeout,
            embedding_model= Config.embedding_model,
            load_faiss_index = Config.load_faiss_index,
            documents_path =Config.documents_path ,
            top_k =Config.top_k ,
            system_prompt=Config.system_prompt,
            )
        return Create_Embeddings_Config

    def get_ai_recommendation_config(self) -> AIRecommendationConfig:
            Config=self.AI_Recommendation
            create_directories([Config.root_dir])
            
            ai_recommendation_config=AIRecommendationConfig(
                root_dir=Config.root_dir,
                source_path=Config.source_path,           
                local_datafile=Config.local_datafile
            )
            return ai_recommendation_config  

    def get_oracle_connect_config(self) -> OracleConnectConfig:
        Config=self.Oracle_Connect
        #create_directories([Config.root_dir])
        
        oracle_connect_config=OracleConnectConfig(
            username=Config.username,
            password=Config.password,           
            host=Config.host,
            port=Config.port,
            service_name=Config.service_name
        )
        return oracle_connect_config      
    
    


