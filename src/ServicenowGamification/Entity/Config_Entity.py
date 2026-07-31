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