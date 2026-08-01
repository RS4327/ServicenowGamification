import os 
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DataIngestionConfig:
    root_dir : Path 
    source_url : str 
    user_name : str 
    password : str 
    local_data_file : Path

@dataclass 
class DataPreProcessingConfig:
    root_dir : Path
    data_path : str
    local_data_file : str
    
@dataclass
class DataMetricsCalculationConfig:
    root_dir : Path
    data_path : str
    local_data_file : str

@dataclass
class DataGamificationConfig:
  root_dir : Path 
  data_path : str
  local_data_file : str
 