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


from sklearn.preprocessing import StandardScaler


from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.svm import SVC 
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split ,GridSearchCV
from sklearn.linear_model import LogisticRegression
 
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





class PredictWorkLoad:
    """
    Predict SLA Breaches using trained XGBoost model.
    """

    def __init__(self, config:DataPredictWorkloadConfig):
        self.config = config
        config_manager=ConfigurationManager()
        self.model = None
        self.scaler = None
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        self.results = {}
       
        self.preprocessing = DataPreProcessing(config_manager.get_data_preprocessing_config() )

        self.metrics = MetricsCalculation(config_manager.get_metricscalculationconfig())

        self.gamification = Gamification(config_manager.get_datagamificationconfig() )
        self.encoding = MachineLearningModels(config_manager.get_data_machinelearningmodels() )

    ###############################################################
    # Load Model
    ###############################################################
    
    def load_model(self):
        #print('###########################################################')
        #print('# Load Model')
        #print('###########################################################')
        model_path=self.config.model_path
        #print( 'model path ' ,model_path)
        #print(os.path.exists(self.config.model_path))
        scaler_path=self.config.scaler_path
        self.model = joblib.load(model_path)
        #self.scaler = joblib.load(scaler_path)
        #print("Model Loaded Successfully.")
        
    def datacleaning(self):

        df = pd.read_csv(self.config.data_path)
        print(df.columns)
        df = self.preprocessing.Datapreprocessing(df)

        return df 
    
    def feature_engineering(self,df):
        if "opened_at" in df.columns:
            df["opened_at"] = pd.to_datetime(df["opened_at"] )
            df["hour"] =   df["opened_at"].dt.hour
            df["day"] = df["opened_at"].dt.day
            df["weekday"] = df["opened_at"].dt.weekday
            df["month"] = df["opened_at"].dt.month

        if "priority" in df.columns:

            df["priority_score"] = df["priority"]

        if {"reassignment_count","reopen_count"}.issubset(df.columns):

            df["complexity"] = (df["reassignment_count"]+df["reopen_count"])
        #print(df.columns)
        return df
    

    def mttr(self,df):
        df=self.metrics.MTTR(df)
        df,art=self.metrics.calculate_art(df)
        df=self.metrics.calculate_sla(df)
        df=self.metrics.calculate_fcr(df)
        df,metrics=self.metrics.performance_metrics(df)
        #print('mttr columns ',df.columns)


        return df
         
    def levl(self, df):
        #print(type(df))
        df = self.gamification.calculate_points(df)
        #print("calculate_points :", type(df))
        df_f, df_analyst_summary = self.gamification.p_save(df)
        #print("p_save :", type(df_f), type(df_analyst_summary))
        df_b = self.gamification.assign_badges(df_f)
        #print("assign_badges :", type(df_b))
        df = self.gamification.b_save(df_b)
        #print("b_save :", type(df))
        df_l = self.gamification.calculate_level(df)
        #print("calculate_level :", type(df_l))
        df = self.gamification.l_save(df_l)
        #print("l_save :", type(df))
        df_lead = self.gamification.generate_leaderboard(df_analyst_summary)
        #print("generate_leaderboard :", type(df_lead))
        df = self.gamification.lead_save(df_lead)
        #print("lead_save :", type(df))
        df_ach = self.gamification.calculate_achievements(df_lead)
        #print("calculate_achievements :", type(df_ach))
        df = self.gamification.ach_save(df_ach)
        #print("ach_save :", type(df))
        df_m = self.gamification.generate_monthly_ranking(df_f)
        #print("generate_monthly_ranking :", type(df_m))
        df = self.gamification.mon_save(df_m)
        #print("mon_save :", type(df))
        #print('df_l columns ',df_l.columns)
        return df_l

    def encodings(self,df):
        
        df_clean=self.encoding.clean_data(df)

        def select_features(df_clean):
                df=df_clean
                
                columns = self.params.predict_workload["feature_columns"]
                #print(f"selct features {columns}")
        
                target = self.params.predict_workload["target_column"]
                #print(f"target feature {target}")
                columns = columns + [target]
        
                df = df[columns]
                #print(df.head(2))
                return df
        df=select_features(df_clean)
        df_enc=self.encoding.encode_features(df)
        #print('before split ',df_enc.columns)
        def split_dataset(df):
            df=df
            # print('###########################################################')
            # print('# Encode Categorical Columns')
            # print('###########################################################')

            target = self.params.predict_workload["target_column"]

            X = df.drop(columns=[target])
            y = df[target]
            X_train, X_test, y_train, y_test = (train_test_split(X,y,test_size=self.params.predict_workload["test_size"],
                                                                                    random_state=self.params.predict_workload["random_state"],
                                                                                    stratify=y
                                                                                    )
                                                                                    )

            # print("Training Shape :", X_train.shape)
            # print("Testing Shape :", X_test.shape)
            output_folder=self.config.output_path
            y_train_s = os.path.join(output_folder, "y_train.csv")
            y_test_s = os.path.join(output_folder, "y_test.csv")
            y_train.to_csv( y_train_s,index=False )
            y_test.to_csv( y_test_s,index=False )  

            return (
                X_train,
                X_test,
                y_train,
                y_test
            )
              

        X_train,X_test,y_train, y_test=split_dataset(df_enc)
        def create_interaction_features(df,train_df, test_df):
           
                for df in [train_df, test_df]:
        
                    if {"resolution_hours", "reopen_count"}.issubset(df.columns):
        
                        df["resolution_reopen"] = (df["resolution_hours"] * (df["reopen_count"] + 1))
        
                    if {"resolution_hours", "customer_rating"}.issubset(df.columns):
        
                        df["resolution_rating"] = (df["resolution_hours"] * df["customer_rating"])
        
                    if {"total_points", "level"}.issubset(df.columns):
        
                        df["points_per_level"] = np.where( df["level"] == 0,0,df["total_points"] / df["level"])
                # print("Training Shape :", X_train.shape)
                # print("Testing Shape :", X_test.shape)
                return df,train_df, test_df

        df,train_df,test_df=create_interaction_features(df_enc,X_train,X_test)
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
                print('scaler numeric_columns ',numeric_columns)
        
                train_df[numeric_columns] = scaler.fit_transform( train_df[numeric_columns])
        
                test_df[numeric_columns] = scaler.transform(test_df[numeric_columns] )
                output_path=self.config.output_path
                 
                Xtrainengineered=os.path.join(output_path, "Xtrainengineered.csv")
                Xtestengineered=os.path.join(output_path, "Xtestengineered.csv")
                train_df.to_csv( Xtrainengineered,index=False )
                test_df.to_csv( Xtestengineered,index=False )  
                 
        
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
                    ),
        
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
        
                    # "SVM": SVC(
                    #     C=p.svm.C,
                    #     kernel=p.svm.kernel,
                    #     gamma=p.svm.gamma,
                    #     probability=p.svm.probability,
                    #     random_state=p.svm.random_state
                    # ),
        
                    # "Logistic Regression": LogisticRegression(
                    #     C=p.logistic_regression.C,
                    #     solver=p.logistic_regression.solver,
                    #     max_iter=p.logistic_regression.max_iter,
                    #     random_state=p.logistic_regression.random_state
                    # ),
        
                    "Decision Tree": DecisionTreeClassifier(
                        criterion=p.decision_tree.criterion,
                        max_depth=p.decision_tree.max_depth,
                        min_samples_split=p.decision_tree.min_samples_split,
                        min_samples_leaf=p.decision_tree.min_samples_leaf,
                        random_state=p.decision_tree.random_state
                    )
        
                    # "KNN": KNeighborsClassifier(
                    #     n_neighbors=p.knn.n_neighbors,
                    #     weights=p.knn.weights,
                    #     metric=p.knn.metric
                    # ),
        
                    # "Gradient Boosting": GradientBoostingClassifier(
                    #     learning_rate=p.gradient_boosting.learning_rate,
                    #     n_estimators=p.gradient_boosting.n_estimators,
                    #     max_depth=p.gradient_boosting.max_depth,
                    #     random_state=p.gradient_boosting.random_state
                    # )
        
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
                    },
                    "XGBoost": {
                        "learning_rate":[0.01,0.1],
                        "max_depth":[3,6],
                        "n_estimators":[100,200]
                    },
                    # "SVM": {
                    #     "C":[0.1,1,10],
                    #     "kernel":["linear","rbf"]
                    # },
                    # "Logistic Regression": {
                    #     "C":[0.01,0.1,1]
                    # },
                    "Decision Tree": {
                        "max_depth":[5,10,None],
                        "min_samples_split":[2,5]
                    }
                    # "KNN": {
                    #     "n_neighbors":[3,5,7]
                    # },
        
                    # "Gradient Boosting": {
                    #     "learning_rate":[0.01,0.1],
                    #     "n_estimators":[100,200]
                    # }
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
                        prediction = best_estimator.predict(X_test)
                        accuracy = accuracy_score(y_test, prediction)
                        precision = precision_score(
                            y_test,
                            prediction,
                            average="binary",
                            zero_division=0
                        )
        
                        recall = recall_score(
                            y_test,
                            prediction,
                            average="binary",
                            zero_division=0
                        )
        
                        f1 = f1_score(
                            y_test,
                            prediction,
                            average="binary",
                            zero_division=0
                        )
        
                        if hasattr(best_estimator, "predict_proba"):
        
                            probability = best_estimator.predict_proba(X_test)[:, 1]
        
                            roc_auc = roc_auc_score(
                                y_test,
                                probability
                            )
        
                        else:
        
                            roc_auc = np.nan
        
                        cm = confusion_matrix(
                            y_test,
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
                            })
        
                            importance = importance.sort_values(
                                by="Importance",
                                ascending=False
                            )
        
                            importance_file = os.path.join(
                                self.config.root_dir,
                                f"{name}_FeatureImportance.csv"
                            )
        
                            importance.to_csv(
                                importance_file,
                                index=False
                            )
        
                            print("\nFeature Importance")
        
                            print(importance)
        
                        # ==================================================
                        # Store Results
                        # ==================================================
        
                        results.append({
        
                            "Model": name,
        
                            "Accuracy": round(accuracy,4),
        
                            "Precision": round(precision,4),
        
                            "Recall": round(recall,4),
        
                            "F1 Score": round(f1,4),
        
                            "ROC AUC": round(roc_auc,4) if not np.isnan(roc_auc) else np.nan,
        
                            "Best Parameters": str(grid.best_params_)
        
                        })
        
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

                    model_path = os.path.join(  output_folder, "Best_Model.pkl" )
                    joblib.dump( best_model, model_path )
                    print("\nFinal Best Model Saved Successfully")
                    print(model_path)
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

     ############################################################
    # Preprocessing
    ############################################################

    def preprocess(self,df,scaler):
        # scaler_path=self.config.scaler_path
        # self.scaler = joblib.load(scaler_path)
        # print('feature_names_in_',self.scaler.feature_names_in_)
        numeric = df.select_dtypes(include=[np.number]).columns
        print('numeric : ',numeric)

        df[numeric] = scaler.transform(df[numeric])

        print("Data Preprocessing Completed")

        return df
    
    def predict_workload(self,df):
        prediction = self.model.predict(df)
        probability = self.model.predict_proba(df)
        df["predicted_workload"] = prediction
        df["confidence"] = np.max(probability, axis=1)
        
        output_folder=self.config.output_path
        report_path = os.path.join(output_folder,"predict_workload.csv")
        df.to_csv(report_path,index=False)

        return df

        ############################################################
    # Categorize Workload
    ############################################################

    def categorize_workload(self,df):

        print("Categorizing Workload...")

        high = self.params.predict_workload["high_workload"]
        medium = self.params.predict_workload["medium_workload"]

        workload_level = []

        for value in df["predicted_workload"]:
            if value >= high:
                workload_level.append("High")
            elif value >= medium:
                workload_level.append("Medium")
            else:
                workload_level.append("Low")
        df["workload_level"] = workload_level
        print("Workload Categorization Completed")
        return df

    ############################################################
    # Resource Recommendation
    ############################################################

    def generate_recommendation(self,df):

        print("Generating Recommendations...")
        recommendation = []

        for _, row in df.iterrows():
            if row["workload_level"] == "High":
                recommendation.append("Assign additional engineer")
            elif row["workload_level"] == "Medium":
                recommendation.append("Monitor workload")
            else:
                recommendation.append("Current capacity is sufficient")

        df["recommendation"] = recommendation
        print("Recommendation Completed")
        return df
    ############################################################
    # Team Summary
    ############################################################

    def workload_summary(self,df):

        print("Preparing Summary...")
        # summary = (df .groupby("workload_level").agg(
        #         Total_Incidents=("number", "count"),
        #         Average_Workload=("predicted_workload","mean")
        #     ) .reset_index()
        # )
        summary = (
             df.groupby("workload_level").agg(
                  Incident_Count=("workload_level", "size"),
                  Average_Workload=("predicted_workload", "mean"),
                  Max_Workload=("predicted_workload", "max"),
                  Min_Workload=("predicted_workload", "min")
                )
                .reset_index()
            )

        summary["Average_Workload"] = (summary["Average_Workload"].round(2))
        summary = summary
        return df,summary


    ############################################################
    # Save Prediction
    ############################################################

    def save_prediction(self,df,summary):

        savepath = self.config.output_path
        prediction_file =  self.config.prediction_file
        summary_file = os.path.join(savepath,"WorkloadSummary.csv")
        df.to_csv(prediction_file,index=False)
        summary.to_csv(summary_file,index=False )

        print("Prediction Saved")
        print(prediction_file)
        print(summary_file)
        

