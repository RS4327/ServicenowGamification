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
  incident_points : str
  analyst_points  : str
  badgeresults  : Path
  badgesummary : Path
  levelresults : Path
  levelsummary : Path
  leaderboardfile : Path 
  topfile : Path 
  bottomfile : Path
  teamfile : Path 
  groupfile : Path 
  achievementfile : Path
  summaryfile : Path
  monthlyranking : Path
  monthlytopfile  : Path
  monthlysummaryfile : Path

@dataclass 
class DataMachineLearningModelsConfig:
    root_dir : Path 
    data_path : Path
    X_train : Path
    X_test : Path
    y_train : Path
    y_test : Path
    scalerpkl : Path
    Xtrainengineered : Path
    Xtestengineered : Path

@dataclass
class DataPredictionConfig:   
    root_dir : Path
    data_path : Path
    model_path: Path
    scaler_path: Path
    prediction_output: Path
    probability_threshold: float

@dataclass 
class DataPredictWorkloadConfig:
    root_dir :Path
    data_path : Path 
    model_path: Path
    scaler_path: Path
    output_path: Path
    prediction_file: Path
    high_workload: int
    medium_workload: int
    low_workload: int
    
@dataclass 
class DataAgentPerformanceConfig:
    root_dir : Path
    data_path : Path
    model_path: Path 
    scaler_path: Path 
    feature_path: Path
    achievements_path: Path
    output_path: Path
    prediction_file: Path
@dataclass
class LLMConfig:
    root_dir : Path
    provider: str
    model: str
    base_url : str
    temperature: float
    top_p : float
    max_tokens: int
    timeout : int 
    prediction_file: Path
    output_path: Path
    response_file: Path
    system_prompt  : str

    prompt_output_path: str
    prompt_output_file: str
    include_similar_incidents: bool
    max_similar_incidents: int
    include_gamification: bool
    include_sla_prediction: bool
    include_workload_prediction: bool
    include_agent_performance: bool
    include_manager_insights: bool
    include_knowledge_suggestion: bool
    max_prompt_length: int
    prompt_version: str

@dataclass
class CreateEmbendingsConfig:
    root_dir : Path 
    source_path : str 
    faiss_index : str
    provider: str
    model: str
    base_url : str
    temperature: float
    top_p : float
    max_tokens: int
    timeout : int
    embedding_model: str
    load_faiss_index: str
    documents_path: str
    top_k : int
    system_prompt  : str

@dataclass(frozen=True)
class AIRecommendationConfig:
    root_dir : Path 
    source_path : str 
    local_datafile : str

@dataclass(frozen=True)
class OracleConnectConfig: 
    username : str
    password : str
    host : str
    port : str
    service_name : str

