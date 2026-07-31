import os 
from pathlib import Path
from ServicenowGamification.Utils.Common import *

from ServicenowGamification.Constant import CONFIG_FILE_PATH, PARAMS_FILE_PATH
from ServicenowGamification.Entity.Config_Entity import  DataIngestionConfig 



class ConfigurationManager:
    def __init__(self,
                 CONFIG_PATH=CONFIG_FILE_PATH,
                 PARAMS_PATH=PARAMS_FILE_PATH

                 ):
         
         ROOT_DIR = Path(__file__).resolve().parents[3]
                 # Read configuration files
         print("ROOT_DIR :", ROOT_DIR)
         
         config_path = ROOT_DIR / "Config" / "Config.yaml"
         params_path = ROOT_DIR / "Params.yaml"
         
         print("Config Path :", config_path)
         print("Config Exists :", config_path.exists())
         
         self.config = Read_Yaml(config_path)
         self.params = Read_Yaml(params_path)
                 
                   
         
         print("Current Working Directory:", os.getcwd())
         
         for p in Path(".").rglob("*.yaml"):
            print("Found YAML:", p.resolve())
         create_directories([self.config.artifacts_root])        
         self.Data_Ingestion = self.config.Data_Ingestion
        
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



