import os 
from pathlib import Path
from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 
from ServicenowGamification.Components.Data_Sng_DataPreProcessing import *
from ServicenowGamification.Components.Data_Sng_MetricsCalculation import MetricsCalculation
from ServicenowGamification.Components.Data_Sng_Gamification import Gamification
from ServicenowGamification.Components.Data_Sng_DataPreProcessing import DataPreProcessing
from ServicenowGamification.Components.Data_Sng_MachineLearningModel import MachineLearningModels
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager 

import joblib




class PredictSLABreach:
    """
    Predict SLA Breaches using trained XGBoost model.
    """

    def __init__(self, config:DataPredictionConfig):
        self.config = config
        config_manager=ConfigurationManager()
        self.model = None
        self.scaler = None
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        #Calling the Existing Models
        self.preprocessing = DataPreProcessing(config_manager.get_data_preprocessing_config() )
        self.metrics = MetricsCalculation(config_manager.get_metricscalculationconfig())
        self.gamification = Gamification(config_manager.get_datagamificationconfig() )
        self.encoding = MachineLearningModels(config_manager.get_data_machinelearningmodels() )

    ###############################################################
    # Load Model
    ###############################################################

    def load_model(self):
        print('###########################################################')
        print('# Load Model')
        print('###########################################################')
        model_path=self.config.model_path
        print( 'model path ' ,model_path)
        print(os.path.exists(self.config.model_path))
        scaler_path=self.config.scaler_path
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        print("Model Loaded Successfully.")

    def datacleaning(self):

        df = pd.read_csv(self.config.data_path)
        print(df.columns)
        df = self.preprocessing.Datapreprocessing(df)

        return df 

    def mttr(self,df):
        df=self.metrics.MTTR(df)
        df,art=self.metrics.calculate_art(df)
        df=self.metrics.calculate_sla(df)
        df=self.metrics.calculate_fcr(df)
        df,metrics=self.metrics.performance_metrics(df)


        return df
         
    def levl(self, df):

        print(type(df))

        df = self.gamification.calculate_points(df)
        print("calculate_points :", type(df))

        df_f, df_analyst_summary = self.gamification.p_save(df)
        print("p_save :", type(df_f), type(df_analyst_summary))

        df_b = self.gamification.assign_badges(df_f)
        print("assign_badges :", type(df_b))

        df = self.gamification.b_save(df_b)
        print("b_save :", type(df))

        df_l = self.gamification.calculate_level(df)
        print("calculate_level :", type(df_l))

        df = self.gamification.l_save(df_l)
        print("l_save :", type(df))

        df,df_lead = self.gamification.generate_leaderboard(df_analyst_summary,df)
        print("generate_leaderboard :", type(df_lead))

        df = self.gamification.lead_save(df_lead)
        print("lead_save :", type(df))

        df_ach = self.gamification.calculate_achievements(df_lead)
        print("calculate_achievements :", type(df_ach))

        df = self.gamification.ach_save(df_ach)
        print("ach_save :", type(df))

        df_m = self.gamification.generate_monthly_ranking(df_f)
        print("generate_monthly_ranking :", type(df_m))

        df = self.gamification.mon_save(df_m)
        print("mon_save :", type(df))

        return df_l
    def encodings(self,df):
        df_clean=self.encoding.clean_data(df)
        df_fea=self.encoding.select_features(df_clean)
        df_enc=self.encoding.encode_features(df_fea)
        return df_enc
   
    def preprocess(self,df):

        feature_columns = [             
            "priority",
            "assignment_group",
            "assigned_to",
            "resolution_hours",
            "reopen_count",
            "reassignment_count",
            "points",
            "level"
        ]

        df = df[feature_columns]
        df["resolution_reopen"] = (df["resolution_hours"] * (df["reopen_count"] + 1))




        numeric_columns = df.select_dtypes( include=["int64", "float64"]).columns
        print('numeric_columns ',numeric_columns)
        df[numeric_columns] = self.scaler.transform(df[numeric_columns] )
        return df

    ###############################################################
    # Prediction
    ###############################################################

    def predict(self,df):
        print('###########################################################')
        print('# Prediction')
        print('###########################################################')    
        probability = self.model.predict_proba(df )[:, 1]
        prediction = self.model.predict(df )

        df["breach_probability"] = probability
        df["prediction"] = prediction
        df["prediction"] = df["prediction"].map(
            {
                0: "SLA Met",
                1: "SLA Breach"
            }
        )
        return df

    ###############################################################
    # Risk Category
    ###############################################################

    def risk_level(self,df):
        print('###########################################################')
        print('# Risk Category')
        print('###########################################################')           

        def category(probability):
            if probability >= 0.80:
                return "High"
            elif probability >= 0.50:
                return "Medium"
            else:
                return "Low"
        df["risk_level"] = df["breach_probability"].apply(category)
        return df

    ###############################################################
    # Recommendation
    ###############################################################

    def recommendation(self,df):
        print('###########################################################')
        print('# recommendation')
        print('###########################################################')           

        recommendation = []
        for _, row in df.iterrows():

            if row["risk_level"] == "High":
                recommendation.append( "Escalate Immediately" )

            elif row["risk_level"] == "Medium":
                recommendation.append("Monitor Closely")
            else:
                recommendation.append( "No Action Required" )

        df["recommendation"] = recommendation

        return df

    ###############################################################
    # Save Prediction
    ###############################################################

    def save_prediction(self,df):
        output_folder = self.config.prediction_output
      
        path = os.path.join( output_folder, "SLAPredictions.csv")

        df.to_csv( path, index=False)

        print(f"Prediction Saved : {path}")
        return df


