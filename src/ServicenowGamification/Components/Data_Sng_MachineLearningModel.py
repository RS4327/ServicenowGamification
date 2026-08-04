import os 
import pandas as pd 
import numpy as np 
from pathlib import Path 
from  dataclasses import dataclass
from ServicenowGamification.Utils.Common import * 
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
import joblib
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


class MachineLearningModels:
    def __init__(self,config:DataMachineLearningModelsConfig):
        self.config=config
        self.params = Read_Yaml(PARAMS_FILE_PATH)
        self.results = {}
          
    def clean_data(self,df):
        if df is None:
            df=pd.read_csv(self.config.data_path)
        

        print('###########################################################')
        print('# Data Cleaning')
        print('###########################################################')

        #df=pd.read_csv(self.config.data_path)
        df = df.drop_duplicates()
        df = df.fillna(0)

        return df
     ###########################################################
    # Select Features
    ###########################################################

    def select_features(self,df):
        df=df
        print('###########################################################')
        print('# Select Features')
        print('###########################################################')

        columns = self.params.machine_learning["feature_columns"]
        print(f"selct features {columns}")

        target = self.params.machine_learning["target_column"]
        print(f"target feature {target}")
        columns = columns + [target]

        df = df[columns]
        #print(df.head(2))
        return df
     ###########################################################
    # Encode Categorical Columns
    ###########################################################

    def encode_features(self,df):
        df=df
        #print('encoding ',df.columns)
        encoders={}
        print('###########################################################')
        print('# Encode Categorical Columns')
        print('###########################################################')

        categorical = df.select_dtypes(include=['object', 'string']).columns

        for column in categorical:

            encoder = LabelEncoder()

            df[column] = encoder.fit_transform(

                df[column].astype(str)

            )

            encoders[column] = encoder

        if df[self.params.machine_learning["target_column"]].dtype == object:

            target_encoder = LabelEncoder()

            df[self.params.machine_learning["target_column"]] = (

                target_encoder.fit_transform(

                    self.df[self.params.machine_learning["target_column"]]

                )

            )

            encoders["target"] = target_encoder
        #print(df.head(2))
        return df
    ###########################################################
    # Split Dataset
    ###########################################################

    def split_dataset(self,df):
        df=df
        print('###########################################################')
        print('# Encode Categorical Columns')
        print('###########################################################')

        target = self.params.machine_learning["target_column"]

        X = df.drop(columns=[target])
        y = df[target]
        X_train, X_test, y_train, y_test = (train_test_split(X,y,test_size=self.params.machine_learning["test_size"],
                                                                                 random_state=self.params.machine_learning["random_state"],
                                                                                 stratify=y
                                                                                 )
                                                                                 )

        print("Training Shape :", X_train.shape)
        print("Testing Shape :", X_test.shape)
        return (
            X_train,
            X_test,
            y_train,
            y_test
        )
    def train_test_save(self,X_train,X_test, y_train,y_test):
        print('###########################################################')
        print('#  Save Dataset ')
        print('###########################################################')
        X_train_s=self.config.X_train
        print(X_train)
        X_test_s=self.config.X_test
        y_train_s=self.config.y_train
        y_test_s=self.config.y_test

        X_train.to_csv( X_train_s,index=False )
        X_test.to_csv( X_test_s,index=False )
        y_train.to_csv( y_train_s,index=False )
        y_test.to_csv( y_test_s,index=False )

        print("Training dataset saved successfully.")

    #########################################################
    # Time Features
    #########################################################
    def create_time_features(self):
        print('###########################################################')
        print('#  Time Features ')
        print('###########################################################')
        
        train_df = pd.read_csv(self.config.X_train)
        test_df  =pd.read_csv(self.config.X_test)
               
        if "opened_at" in train_df.columns:

            train_df["opened_at"] = pd.to_datetime(train_df["opened_at"]
            )
            test_df["opened_at"] = pd.to_datetime(test_df["opened_at"]
            )

            for df in [self.train_df, self.test_df]:

                df["opened_hour"] = df["opened_at"].dt.hour

                df["opened_day"] = df["opened_at"].dt.day

                df["opened_month"] = df["opened_at"].dt.month

                df["opened_weekday"] = df["opened_at"].dt.weekday

                df.drop(columns=["opened_at"], inplace=True)

        return train_df,test_df

    #########################################################
    # Interaction Features
    #########################################################

    def create_interaction_features(self,train_df, test_df):
        print('###########################################################')
        print('#  Interaction Features ')
        print('###########################################################')

        for df in [train_df, test_df]:

            if {"resolution_hours", "reopen_count"}.issubset(df.columns):

                df["resolution_reopen"] = (df["resolution_hours"] * (df["reopen_count"] + 1))

            if {"resolution_hours", "customer_rating"}.issubset(df.columns):

                df["resolution_rating"] = (df["resolution_hours"] * df["customer_rating"])

            if {"total_points", "level"}.issubset(df.columns):

                df["points_per_level"] = np.where( df["level"] == 0,0,df["total_points"] / df["level"])

        return train_df, test_df

    #########################################################
    # Log Transformation
    #########################################################

    def log_transform(self,train_df, test_df):
        print('###########################################################')
        print('#  Log Transformation')
        print('###########################################################')

        columns = ["resolution_hours","points"]

        for df in [train_df, test_df]:

            for column in columns:

                if column in df.columns:

                    df[column] = np.log1p(df[column])

        return train_df, test_df

    # #########################################################
    # # Feature Scaling
    # #########################################################

    def scale_features(self,train_df, test_df):
        scaler = StandardScaler()
        print('###########################################################')
        print('#  Feature Scaling')
        print('###########################################################')

        numeric_columns = train_df.select_dtypes(include=["int64", "float64"] ).columns
        print('scaler numeric_columns ',numeric_columns)

        train_df[numeric_columns] = scaler.fit_transform( train_df[numeric_columns])

        test_df[numeric_columns] = scaler.transform(test_df[numeric_columns] )

        return train_df,test_df,scaler

    # #########################################################
    # # Save Scaler
    # #########################################################

    def save_scaler(self,scaler):
        scalerpkl=self.config.scalerpkl
        
        joblib.dump(scaler,scalerpkl)

    # #########################################################
    # # Save Engineered Data
    # #########################################################

    def save_dataset(self,train_df,test_df):
        Xtrainengineered=self.config.Xtrainengineered
        Xtestengineered =self.config.Xtestengineered
        train_df.to_csv( Xtrainengineered,index=False )
        test_df.to_csv( Xtestengineered,index=False )  

        print("Feature engineered dataset saved.")


    ###########################################################
    # Configure Model
    ###########################################################
  
    def get_models(self):

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

    def get_param_grid(self):
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

    def ModelsTraining(self, models):

        # ==========================================================
        # Load Data
        # ==========================================================
        X_train = pd.read_csv(self.config.Xtrainengineered)
        X_test = pd.read_csv(self.config.Xtestengineered)

        y_train = pd.read_csv(self.config.y_train).squeeze()
        y_test = pd.read_csv(self.config.y_test).squeeze()

        param_grid = self.get_param_grid()

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

        # ==========================================================
        # Save Best Model
        # ==========================================================
    
        if best_model is not None:

            model_path = os.path.join(
                self.config.root_dir,
                "Best_Model.pkl"
            )

            joblib.dump(
                best_model,
                model_path
            )

        # ==========================================================
        # Save Evaluation Report
        # ==========================================================

        results_df = pd.DataFrame(results)

        results_path = os.path.join(
            self.config.root_dir,
            "Model_Evaluation.csv"
        )

        results_df.to_csv(
            results_path,
            index=False
        )

        # ==========================================================
        # Final Summary
        # ==========================================================

        print("\n" + "=" * 80)
        print("Training Completed")
        print("=" * 80)

        print("Best Model :", best_model_name)
        print("Best Accuracy :", round(best_accuracy,4))

        print("\nResults")

        print(results_df)

        # ==========================================================
        # Return
        # ==========================================================

        return (
            best_model_name,
            best_accuracy,
            best_model,
            results_df
        )

            
    

