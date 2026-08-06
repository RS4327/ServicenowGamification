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


os.chdir(r"C:\Users\RSR\PYTHON\ServicenowGamification")

from sklearn.preprocessing import StandardScaler
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager 


from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.svm import SVC 
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split ,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
 
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)





class AgentPerformance:
    def __init__(self, config:DataAgentPerformanceConfig):
        self.config = config
        
        config_manager=ConfigurationManager()
        
        self.params = Read_Yaml(PARAMS_FILE_PATH)

        self.model = None
        self.scaler = None
        self.features = None
        self.original_df = pd.DataFrame(columns=[])
       
        self.preprocessing = DataPreProcessing(config_manager.get_data_preprocessing_config() )
        self.metrics = MetricsCalculation(config_manager.get_metricscalculationconfig())
        self.gamification = Gamification(config_manager.get_datagamificationconfig() )
        self.encoding = MachineLearningModels(config_manager.get_data_machinelearningmodels() )

    ###############################################################
    # Load Model
    ###############################################################

    def load_artifacts(self):
        #print("Loading Agent Performance Model...")

        self.model = joblib.load(self.config.model_path)
        self.scaler = joblib.load( self.config.scaler_path)
        #self.features = joblib.load(self.config.feature_path)
        print("Artifacts Loaded Successfully")

    def datacleaning(self):
    
            df = pd.read_csv(self.config.data_path)
            #print(self.config.data_path)
            df.drop_duplicates(inplace=True)

            df.fillna(0,inplace=True )
            return df 
    ##########################################################
    # Feature Engineering
    ##########################################################
    def feature_engineering(self,df):
         if "sla_percentage" not in df.columns : 
            sla = (df.groupby("assigned_to")["sla_status"].apply(
                lambda x: (x == "Met").mean() * 100
                ).reset_index(name="sla_percentage")
                )
         
            df = df.merge(
                    sla,
                    on="assigned_to",
                    how="left"
                )
         df["customer_rating"] = np.where(df["sla_status"] == "Met",5,3)     
         #print(df.columns.tolist())
         df["quality_score"] = (df["sla_percentage"] * df["customer_rating"])
      
         badge_map = {
               "Rookie":0,
               "Bronze":1,
                "Silver":2,
                "Gold":3,
                "Diamond":4
                }

         df["badges"] = df["badge"].map(badge_map)
         if 'achievement' not in df.columns:
            ach_df=pd.read_csv(self.config.achievements_path)

            df = df.merge(
                ach_df[["assigned_to", "achievements"]],
                on="assigned_to",
                how="left"
            )

            df = df.rename(columns={"achievements": "achievement"})
            df = df.rename(columns={"complexity": "complexity_score"})

         achievement_map = {
             "None":0,
             "Top Performer":1,
             "SLA Master":2,
             "Speed Resolver":3
             }

         df["achievements"] = (df["achievement"].map(achievement_map))
         df["recognition_score"] = (df["badges"]+df["achievements"])
         if 'total_incidents' not in df.columns:
            incidents = (df.groupby("assigned_to") .size() .reset_index(name="total_incidents"))

            df = df.merge(
                incidents,
                on="assigned_to",
                how="left"
                )

            
         df["points_per_ticket"] = (df["points"] /  df["total_incidents"].replace(0,1))
        #
         df["mttr"] = (df.groupby("assigned_to")["resolution_hours"].transform("mean"))
        #Average Response Time)
        #  df["art"] = (df.groupby("assigned_to")["response_hours"].transform("mean"))   
        #  ART was not included because the extracted ServiceNow Incident dataset does not contain first response timestamps. In a production ServiceNow environment,
        #  ART can be calculated from the task_sla table (Response SLA) or from journal/audit records.

         df["resolved_incidents"] = (df.groupby("assigned_to")["state"].transform(lambda x: (x == "Resolved").sum()))

         resolved = (df["state"].isin(["Resolved", "Closed"]).groupby(df["assigned_to"]).sum())

         df["resolved_incidents"] = (df["assigned_to"].map(resolved))
         active = (df["state"].eq("In Progress").groupby(df["assigned_to"]).sum())

         df["active_incidents"] = (df["assigned_to"].map(active))
         pending = (df["state"].eq("Pending").groupby(df["assigned_to"]).sum())

         df["pending_incidents"] = (df["assigned_to"].map(pending))

         reward_map = { "Bronze":100,
                       "Silver":250,
                       "Gold":500,
                       "Diamond":1000
                       }

         df["rewards"] = df["badge"].map(reward_map)
         #or 
         #df["rewards"] = df["total_points"] // 100

         df["leaderboard_rank"] = (df["points"].rank(
             ascending=False,
             method="dense"
             ).astype(int)
             )
         df["month"] = (pd.to_datetime(df["opened_at"]).dt.to_period("M"))

         df["monthly_rank"] = (df.groupby("month")["points"].rank(
             ascending=False,
             method="dense"
             )
             )

         workload = (df.groupby("assigned_to").size())

         df["workload"] = (df["assigned_to"].map(workload))

         conditions = [
               df["workload"] >= 50,
                df["workload"] >= 25
                ]

         choices = ["High","Medium"]

         df["workload_level"] = np.select(
             conditions,
             choices,
             default="Low"
             )
         df["fcr_percentage"] = (df.groupby("assigned_to")["fcr"].transform("mean") * 100)
         skill_map = {"Beginner": 40,"Intermediate": 70,"Expert": 100}

         df["skill_score"] = (df["level_name"].map(skill_map))
        # or
        #  df["skill_score"] = (
        #      0.40 * df["sla_percentage"]
        #      + 0.30 * df["fcr_percentage"]
        #      + 0.20 * df["customer_rating"]
        #      + 0.10 * df["experience_years"]
        #      )

         df["opened_weekday"] = (pd.to_datetime(df["opened_at"]).dt.weekday )

         df["performance_index"] = (
             0.30 * df["sla_percentage"]
             + 0.25 * df["customer_rating"]
             + 0.20 * df["fcr_percentage"]
             + 0.15 * df["skill_score"]
             + 0.10 * (100 - df["mttr"])
             )
            #Calcualte Perfomance
            # Feature	      Weight
            # SLA Percentage	30%
            # Customer Rating	20%
            # FCR Percentage	20%
            # MTTR	15%
            # Total Points	10%
            # Reopen Count	5%

         df["performance_score"] = (
             0.30 * df["sla_percentage"]
             + 0.20 * (df["customer_rating"] * 20)   # 1-5 → 20-100
             + 0.20 * df["fcr_percentage"]
             + 0.15 * (100 - df["mttr"])
             + 0.10 * (df["points"] / df["points"].max() * 100)
             + 0.05 * (100 - df["reopen_count"] * 10)
             )
         conditions = [
               df["performance_score"] >= 85,
               df["performance_score"] >= 70,
               df["performance_score"] >= 55
               ]

         choices = [
              "Excellent",
              "Good",
              "Average"
              ]

         df["performance_rating"] = np.select(
              conditions,
              choices,
              default="Poor"
              )

         df["opened_at"] = pd.to_datetime(df["opened_at"] )
         df["opened_hour"] = (df["opened_at"].dt.hour )
         df["quality_score"] = (df["sla_percentage"] * df["customer_rating"])
         
         #print(df.columns)
         return df

    ##########################################################
    # Feature Engineering
    ##########################################################


    def mttr(self,df):
            df=self.metrics.MTTR(df)
            df,art=self.metrics.calculate_art(df)
            df=self.metrics.calculate_sla(df)
            df=self.metrics.calculate_fcr(df)
            df,metrics=self.metrics.performance_metrics(df)
            #print('mttr columns ',df.columns)
    
    
            return df

    def levl(self, df):

        df = self.gamification.calculate_points(df)
        df_f, df_analyst_summary = self.gamification.p_save(df)
        df_b = self.gamification.assign_badges(df_f)
        df = self.gamification.b_save(df_b)
        df_l = self.gamification.calculate_level(df)
        df = self.gamification.l_save(df_l)
        df_lead = self.gamification.generate_leaderboard(df_analyst_summary)
        df = self.gamification.lead_save(df_lead)
        df_ach = self.gamification.calculate_achievements(df_lead)
        df = self.gamification.ach_save(df_ach)
        df_m = self.gamification.generate_monthly_ranking(df_f)
        df = self.gamification.mon_save(df_m)
        #print(df_l.columns)

        return df_l

    def encodings(self,df):            
        df_clean=self.encoding.clean_data(df)
        #original_df=df_clean.copy()

        # def select_features(df_clean):
        #     df=df_clean
        #     columns = self.params.agent_performance["feature_columns"]
        #     #print(f"selct features {columns}")
                
        #     target = self.params.agent_performance["target_column"]
        #     #print(f"target feature {target}")
        #     columns = columns + [target]
                
        #     df = df[columns]
        #     #print(df.head(2))
        #     return df

        # def encode_features(df):
        #         df=df
        #         #print('encoding ',df.columns)
        #         encoders={}
        #         categorical = df.select_dtypes(include=['object', 'str']).columns
        
        #         for column in categorical:        
        #             encoder = LabelEncoder()        
        #             df[column] = encoder.fit_transform(
        
        #                 df[column].astype(str))
        #             encoders[column] = encoder
        
        #         if df[self.params.agent_performance["target_column"]].dtype == object:
        
        #             target_encoder = LabelEncoder()
        
        #             df[self.params.agent_performance["target_column"]] = (
        #                  target_encoder.fit_transform(
        #                  df[self.params.agent_performance["target_column"]]
        #                  )
        #                  )
        
        #             encoders["target"] = target_encoder
        #         #print(df.head(2))
        #         return df
       
    
        def split_dataset(df):
                    df=df
                    # print('###########################################################')
                    # print('# Encode Categorical Columns')
                    # print('###########################################################')
        
                    target = self.params.agent_performance["target_column"]
                    df = df.drop(columns=["resolution_time"])
                    df = df.drop(columns=["opened_at"])
                    df = df.drop(columns=["resolved_at"])
                    df = df.drop(columns=["closed_at"])
                    X = df.drop(columns=[target])
                    y = df[target]
                    X_train, X_test, y_train, y_test = (train_test_split(X,y,test_size=self.params.agent_performance["test_size"],
                                                                                            random_state=self.params.agent_performance["random_state"],
                                                                                            stratify=y
                                                                                            )
                                                                                            )
        
                    # print("Training Shape :", X_train.shape)
                    # print("Testing Shape :", X_test.shape)
                    output_folder=self.config.output_path
                    X_train_s=os.path.join(output_folder, "X_train_s.csv")
                    X_test_s=os.path.join(output_folder, "X_test_s.csv")
                    X_train.to_csv( X_train_s,index=False )
                    X_test.to_csv( X_test_s,index=False ) 

                    y_train_s = os.path.join(output_folder, "y_train.csv")
                    y_test_s = os.path.join(output_folder, "y_test.csv")
                    y_train.to_csv( y_train_s,index=False )
                    y_test.to_csv( y_test_s,index=False )  
                    self.original_df=X_train.copy()
                    return (
                        X_train,
                        X_test,
                        y_train,
                        y_test
                    )
                              
        X_train,X_test,y_train, y_test=split_dataset(df)
        from sklearn.preprocessing import LabelEncoder
        
        def encode_features(X_train, X_test, y_train, y_test):

                feature_columns = self.params.agent_performance["feature_columns"]

                X_train = X_train[feature_columns].copy()
                X_test = X_test[feature_columns].copy()

                print("X_train Shape :", X_train.shape)
                print("X_test Shape :", X_test.shape)
                print("Selected Features :", X_train.columns.tolist())
        
                encoders = {}
        
                categorical = X_train.select_dtypes(include=["object", "string"]).columns
        
                for col in categorical:
        
                    encoder = LabelEncoder()
        
                    X_train[col] = encoder.fit_transform(
                        X_train[col].astype(str)
                    )
        
                    X_test[col] = encoder.transform(
                        X_test[col].astype(str)
                    )
        
                    encoders[col] = encoder
        
                # Encode target
                if y_train.dtype == object:
        
                    target_encoder = LabelEncoder()
        
                    y_train = target_encoder.fit_transform(y_train)
        
                    y_test = target_encoder.transform(y_test)
        
                    encoders["target"] = target_encoder
        
                return X_train, X_test, y_train, y_test
        

        X_train, X_test, y_train, y_test=encode_features(X_train, X_test, y_train, y_test)

        def create_interaction_features(df,train_df, test_df):
                   
                        for df in [train_df, test_df]:
                
                            if {"resolution_hours", "reopen_count"}.issubset(df.columns):
                
                                df["resolution_reopen"] = (df["resolution_hours"] * (df["reopen_count"] + 1))
                
                            if {"resolution_hours", "customer_rating"}.issubset(df.columns):
                
                                df["resolution_rating"] = (df["resolution_hours"] * df["customer_rating"])
                
                            if {"points", "level"}.issubset(df.columns):
                
                                df["points_per_level"] = np.where( df["level"] == 0,0,df["points"] / df["level"])
                        # print("Training Shape :", X_train.shape)
                        # print("Testing Shape :", X_test.shape)
                        return df,train_df, test_df
        
        df,train_df,test_df=create_interaction_features(df,X_train,X_test)

        def log_transform(df,train_df, test_df):
                        
                        columns = ["resolution_hours","points"]
                
                        for df in [train_df, test_df]:
                
                            for column in columns:
                
                                if column in df.columns:
                
                                    df[column] = np.log1p(df[column])
                                return df,train_df, test_df
                
        df,train_df,test_df=log_transform(df,train_df,test_df)
        
        def scale_features(df,train_df, test_df):
                        scaler = StandardScaler()
                        df=df
                        #print(df.info())
                       
                        numeric_columns = train_df.select_dtypes(include=["int64","int32", "float64"] ).columns
                        #print('scaler numeric_columns ',numeric_columns)
                
                        train_df[numeric_columns] = scaler.fit_transform( train_df[numeric_columns])
                
                        test_df[numeric_columns] = scaler.transform(test_df[numeric_columns] )
                        output_path=self.config.output_path
                         
                        Xtrainengineered=os.path.join(output_path, "Xtrainengineered.csv")
                        Xtestengineered=os.path.join(output_path, "Xtestengineered.csv")
                        train_df.to_csv( Xtrainengineered,index=False )
                        test_df.to_csv( Xtestengineered,index=False )  
                        
                        joblib.dump( scaler, self.config.scaler_path )
                         
                
                        return df,train_df,test_df,scaler
        
        df,train_df,test_df,scaler=scale_features(df,train_df,test_df)


        def get_models():
        
                p = self.params.model_training
        
                models = {
        
                    "Random Forest": RandomForestClassifier(
                        n_estimators=p.random_forest.n_estimators,
                        max_depth=p.random_forest.max_depth,
                        min_samples_split=p.random_forest.min_samples_split,
                        min_samples_leaf=p.random_forest.min_samples_leaf,
                        max_features=p.random_forest.max_features,
                        bootstrap=p.random_forest.bootstrap,
                        random_state=p.random_forest.random_state
                    )                    ,        
                    "XGBoost": XGBClassifier(
                        objective=p.xgboost.objective,
                        eval_metric=p.xgboost.eval_metric,
                        learning_rate=p.xgboost.learning_rate,
                        max_depth=p.xgboost.max_depth,
                        n_estimators=p.xgboost.n_estimators,
                        subsample=p.xgboost.subsample,
                        colsample_bytree=p.xgboost.colsample_bytree,
                        gamma=p.xgboost.gamma,
                        min_child_weight=p.xgboost.min_child_weight,
                        random_state=p.xgboost.random_state
                    ),
                     
                    "Decision Tree": DecisionTreeClassifier(
                        criterion=p.decision_tree.criterion,
                        max_depth=p.decision_tree.max_depth,
                        min_samples_split=p.decision_tree.min_samples_split,
                        min_samples_leaf=p.decision_tree.min_samples_leaf,
                        random_state=p.decision_tree.random_state
                    )
        
             
                }
        
                print("Models Created Successfully")
        
                return models    
        models=get_models()

        def get_param_grid():
            param_grid = {
                "Random Forest": {
                      "n_estimators":[100,200,300],
                       "max_depth":[5,10,None],
                       "min_samples_split":[2,5]
                       }
                       ,
                "XGBoost": {
                      "learning_rate":[0.01,0.1],
                      "max_depth":[3,6],
                      "n_estimators":[100,200]
                      },
                "Decision Tree": {
                      "max_depth":[5,10,None],
                      "min_samples_split":[2,5]
                      }
                      
                }
                
            return param_grid

        def ModelsTraining( models):
        
                # ==========================================================
                # Load Data
                # ==========================================================
                output_folder=self.config.output_path
                Xtrainengineered = os.path.join(output_folder, "Xtrainengineered.csv")
                Xtestengineered = os.path.join(output_folder, "Xtestengineered.csv")
                X_train = pd.read_csv(Xtrainengineered)
                X_test = pd.read_csv(Xtestengineered)

                print('X_train :',X_train.columns)
                print('X_test :',X_test.columns)

                y_train_s = os.path.join(output_folder, "y_train.csv")
                y_test_s = os.path.join(output_folder, "y_test.csv")
        
                y_train = pd.read_csv(y_train_s).squeeze()
                y_test = pd.read_csv(y_test_s).squeeze()
        
                param_grid = get_param_grid()
        
                results = []
        
                best_accuracy = 0.0
                best_model = None
                best_model_name = None
        
                # ==========================================================
                # Train Models
                # ==========================================================
                for name, model in models.items():
                
        
                    print("\n" + "=" * 80)
                    print(f"Training : {name}")
                    print("=" * 80)
        
                    try:
        
                        grid = GridSearchCV(
                            estimator=model,
                            param_grid=param_grid[name],
                            cv=5,
                            scoring="accuracy",
                            n_jobs=-1,
                            error_score="raise"
                        )
        
                        grid.fit(X_train, y_train)
     
                        best_estimator = grid.best_estimator_
                        print('best_estimator ',best_estimator)
                        prediction = best_estimator.predict(X_test)
                        accuracy = accuracy_score(y_test, prediction)
                        precision = precision_score(y_test,
                                                    prediction,
                                                    average="weighted",
                                                    zero_division=0
                                                    )

                        # precision = precision_score(
                        #     y_test,
                        #     prediction,
                        #     average="binary",
                        #     zero_division=0
                        # )
        
                        recall = recall_score(y_test,
                                              prediction,
                                              average="weighted",
                                              zero_division=0
                                              )
        
                        f1 = f1_score(y_test,
                                      prediction,
                                      average="weighted",
                                      zero_division=0
                                      )
        
                        if hasattr(best_estimator, "predict_proba"):

                            proba = best_estimator.predict_proba(X_test)

                            print("Predict Proba Shape:", proba.shape)

                            if proba.shape[1] == 2:

                                probability = proba[:, 1]

                                roc_auc = roc_auc_score(y_test, probability)

                            else:

                                roc_auc = np.nan
                                print("Only one class present. ROC AUC skipped.")

                        else:

                            roc_auc = np.nan
        
                        cm = confusion_matrix(y_test,
                                              prediction
                                              )
        
                        print("\nBest Parameters")
                        print(grid.best_params_)
        
                        print("\nAccuracy :", accuracy)
                        print("Precision :", precision)
                        print("Recall :", recall)
                        print("F1 Score :", f1)
                        print("ROC AUC :", roc_auc)
        
                        print("\nConfusion Matrix")
                        print(cm)
        
                        print("\nClassification Report")

                        print(
                            classification_report(
                                y_test,
                                prediction,
                                zero_division=0
                            )
                        )
        
                        # ==================================================
                        # Feature Importance
                        # ==================================================
        
                        if hasattr(best_estimator, "feature_importances_"):
        
                            importance = pd.DataFrame({
                                  "Feature": X_train.columns,
                                  "Importance": best_estimator.feature_importances_
                                   }
                                   )
        
                            importance = importance.sort_values(by="Importance",
                                                                ascending=False)
        
                            importance_file = os.path.join(self.config.root_dir,
                                                            f"{name}_FeatureImportance.csv")
        
                            importance.to_csv(importance_file,
                                              index=False)
        
                            # print("\nFeature Importance")
        
                            # print(importance)
        
                        # ==================================================
                        # Store Results
                        # ==================================================
        
                        results.append(
                              {
                                    "Model": name,
                                    "Accuracy": round(accuracy,4),
                                      "Precision": round(precision,4),
                                      "Recall": round(recall,4),
                                      "F1 Score": round(f1,4),"ROC AUC": round(roc_auc,4) if not np.isnan(roc_auc) else np.nan,
                                      "Best Parameters": str(grid.best_params_)
                                      }
                                      )
        
                        # ==================================================
                        # Best Model
                        # ==================================================
        
                        if accuracy > best_accuracy:
        
                            best_accuracy = accuracy
                            best_model = best_estimator
                            best_model_name = name
        
                    except Exception as e:
        
                        print(f"\n{name} Failed")
                        print(e)
        
                 ###############################################################
                # Evaluation Report
                ###############################################################

                results_df = pd.DataFrame(results)
                output_folder=self.config.output_path
                report_path = os.path.join(
                    output_folder,
                    "Model_Evaluation.csv"
                )

                results_df.to_csv(
                    report_path,
                    index=False
                )

                ###############################################################
                # Save Final Best Model Again
                ###############################################################

                if best_model is not None:

                    model_path = os.path.join(  output_folder, "AgentPerformanceModel.pkl" )
                    joblib.dump( best_model, model_path )
                    #print("\nFinal Best Model Saved Successfully")
                    #print(model_path)
                else:
                    print("\nNo Best Model Found")
                 ###############################################################
                # Summary
                ###############################################################

                print("\n" + "=" * 80)
                print("Training Completed")
                print("=" * 80)
                print("Best Model :", best_model_name)
                print("Best Accuracy :", best_accuracy)
                print("\nEvaluation Results")
                print(results_df)

                ###############################################################
                # Return
                ###############################################################

                return (best_model_name,best_accuracy,best_model,results_df)
 
        
        ModelsTraining(models)

        return df,train_df,test_df,scaler

        
        
        return df,train_df,test_df,scaler
    def preprocess(self,df,scaler):
            # scaler_path=self.config.scaler_path
            # self.scaler = joblib.load(scaler_path)
            # print('feature_names_in_',self.scaler.feature_names_in_)
            numeric = df.select_dtypes(include=[np.number]).columns
            print('numeric : ',numeric)
    
            df[numeric] = scaler.transform(df[numeric])
    
            print("Data Preprocessing Completed")
    
            return df
        ##########################################################
    # Prediction
    ##########################################################

    def predict(self,df):
        print('Last Step')
        prediction = self.model.predict(df)
        probability = self.model.predict_proba(df)

        # df["performance_prediction"] = prediction

        # df["confidence"] = (probability.max(axis=1))
        self.original_df["performance_prediction"] = prediction
        self.original_df["confidence"] = probability.max(axis=1)
        df=self.original_df
       
        return df

    ##########################################################
    # Performance Categorization
    ##########################################################

    def categorize_performance(self,df):
        print("Categorizing Agent Performance...")
        performance_category = []
        for value in df["performance_prediction"]:
            if value == 3:
                performance_category.append("Excellent")
            elif value == 2:
                performance_category.append("Good")            
            elif value == 1:
                performance_category.append("Average")
            else:
                performance_category.append("Needs Improvement")
        df["performance_category"] = performance_category

        print("Performance Categorization Completed")

        return df

    ##########################################################
    # Recommendation Engine
    ##########################################################

    def generate_recommendation(self,df):
        print("Generating Recommendations...")
        recommendation = []
        for category in df["performance_category"]:
            if category == "Excellent":
                recommendation.append(
                    "Eligible for reward and leadership opportunities"
                )
            elif category == "Good":
                recommendation.append(
                    "Maintain performance and pursue advanced certifications"
                )
            elif category == "Average":
                recommendation.append(
                    "Improve SLA compliance and reduce resolution time"
                )
            else:
                recommendation.append(
                    "Training required and manager intervention recommended"
                )
        df["recommendation"] = recommendation
        print("Recommendation Generation Completed")

        return df

    def performance_summary(self, df):

        print("Generating Performance Summary...")

        summary = (
            df.groupby("assigned_to")
            .agg(
                Total_Incidents=("number", "count"),
                Average_Confidence=("confidence", "mean"),
                Latest_Prediction=("performance_prediction", "last")
            )
            .reset_index()
        )

        summary["Average_Confidence"] = summary["Average_Confidence"].round(2)

        return summary

    def performance_incident_summary(self, df):

        print("Generating Incident Level Performance Summary...")

        summary = df.copy()

        # Round confidence
        summary["confidence"] = summary["confidence"].round(2)

        # Performance Category
        category_map = {
            0: "Needs Improvement",
            1: "Average",
            2: "Good",
            3: "Excellent"
        }

        summary["performance_category"] = (
            summary["performance_prediction"].map(category_map)
        )

        # Recommendation
        recommendation_map = {
            "Excellent": "Eligible for Reward",
            "Good": "Maintain Performance",
            "Average": "Provide Skill Training",
            "Needs Improvement": "Coaching Required"
        }

        summary["recommendation"] = (
            summary["performance_category"].map(recommendation_map)
        )

        # Final Output
        inc_summary = summary[
            [
                "number",
                "assigned_to",
                "assignment_group",
                "priority",
                "points",
                "performance_prediction",
                "performance_category",
                "confidence",
                "recommendation"
            ]
        ]

        return inc_summary
    ##########################################################
    # Save Prediction
    ##########################################################

    def save_prediction(self,df,summary,inc_summary):

        print("Saving Prediction...")

         

        summary_file = os.path.join(
            self.config.output_path,
            "AgentPerformanceSummary.csv"
        )

        df.to_csv(
            self.config.prediction_file,
            index=False
        )

        summary.to_csv(
            summary_file,
            index=False
        )

        inc_summary_file = os.path.join(
                    self.config.output_path,
                    "AgentIncidentPerformanceSummary.csv"
                )
        
        inc_summary.to_csv(
                    inc_summary_file,
                    index=False
                )
        print("Prediction Saved Successfully")

        #print(prediction_file)

        #print(summary_file)
                

        

    
             
    
