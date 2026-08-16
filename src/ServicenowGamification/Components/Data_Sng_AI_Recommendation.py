import os
import numpy as np
from dataclasses import dataclass
from pathlib import Path
import pandas as pd 
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from ollama import Client

from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 
from ServicenowGamification.Components.Data_Sns_LLM_Embendings import PromptBuilder,CreateEmbedings
from ServicenowGamification.Config.ConfigurationManager import ConfigurationManager 

class AIRecommendation:
    def __init__(self, config:AIRecommendationConfig,
                 p_config:CreateEmbendingsConfig):
        self.config = config
        self.p_config=p_config
        config_manager=ConfigurationManager()
        
        self.params = Read_Yaml(PARAMS_FILE_PATH)

        self.model = None
        self.scaler = None
        self.features = None
        self.original_df = pd.DataFrame(columns=[])
       
        self.llmconnect = CreateEmbedings(config_manager.get_create_embendings_config() )
        self.prompt = PromptBuilder(config_manager.get_ai_recommendation_config() )
    def connect_llm(self):
        self.llmconnect.connect()
        self.llmconnect.test_connection()
    def faiss_search(self): 
        self.llmconnect.load_faiss_index()
        self.llmconnect.load_documents()
        self.llmconnect.load_embedding_model()
     # ============================================================
    # CREATE FAISS QUERY
    # ============================================================

    def create_search_query(self,incident_data):

        query = f"""

ServiceNow Incident

Short Description:
{incident_data.get("short_description", "")}

Category:
{incident_data.get("category", "")}

Subcategory:
{incident_data.get("subcategory", "")}

Priority:
{incident_data.get("priority", "")}

Assignment Group:
{incident_data.get("assignment_group", "")}

Resolution Hours:
{incident_data.get("resolution_hours", "")}

SLA Status:
{incident_data.get("sla_status", "")}

Workload Level:
{incident_data.get("workload_level", "")}

Agent Performance:
{incident_data.get("performance_prediction", "")}

"""

        return query.strip()

    # ============================================================
    # SINGLE INCIDENT
    # ============================================================

    def single_generate_recommendation(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None
    ):

        print("=" * 80)
        print("STEP 41 - AI RECOMMENDATION")
        print("=" * 80)

        # --------------------------------------------------------
        # Connect Ollama
        # --------------------------------------------------------

        self.llmconnect.connect()

        self.llmconnect.test_connection()

        # --------------------------------------------------------
        # Create FAISS query
        # --------------------------------------------------------

        query = self.create_search_query(incident_data)

        # print(
        #     "\nFAISS Query:"
        # )

        # print(query)

        # --------------------------------------------------------
        # Search similar incidents
        # --------------------------------------------------------

        retrieved_incidents = (
            self.llmconnect.search(
                query=query,
                top_k=self.p_config.top_k
            )
        )

        print(
            "\nSimilar incidents found:",
            len(retrieved_incidents)
        )

    # --------------------------------------------------------
        # Build prompt
        # --------------------------------------------------------

        prompt = self.prompt.build_prompt(
            task="recommendation",
            incident_data=incident_data,
            sla_data=sla_data,
            workload_data=workload_data,
            performance_data=performance_data,
            gamification_data=gamification_data,
            retrieved_incidents=retrieved_incidents
        )

        print(
            "\nPrompt created successfully."
        )

        # --------------------------------------------------------
        # Ollama
        # --------------------------------------------------------

        response = self.llmconnect.generate_response(
            prompt
        )

        return response


     # =========================================================
    # GENERATE RECOMMENDATIONS
    # =========================================================

    def generate_recommendations(self):

        print("=" * 70)
        print("STEP 41 - AI RECOMMENDATIONS")
        print("=" * 70)

        # --------------------------------------------------------
                # Connect Ollama
                # --------------------------------------------------------
        
        self.llmconnect.connect()
        
        self.llmconnect.test_connection()

        # -----------------------------------------------------
        # LOAD DATA
        # -----------------------------------------------------

        df = pd.read_csv(self.config.source_path)

        print("Input Shape:",df.shape)


        # -----------------------------------------------------
        # CREATE OUTPUT COLUMN
        # -----------------------------------------------------

        df["ai_recommendation"] = ""


        # -----------------------------------------------------
        # PROCESS EACH INCIDENT
        # -----------------------------------------------------

        for index, row in df.iterrows():

            print(
                f"\nProcessing "
                f"{index + 1}/{len(df)}"
            )


            # =================================================
            # INCIDENT
            # =================================================

            incident_data = (
                row.to_dict()
            )


            # =================================================
            # SLA
            # =================================================

            sla_data = {

                "sla_prediction":
                    row.get(
                        "sla_prediction",
                        "Not Available"
                    ),

                "sla_status":
                    row.get(
                        "sla_status",
                        "Not Available"
                    ),

                "sla_confidence":
                    row.get(
                        "sla_confidence",
                        "Not Available"
                    ),

                "sla_percentage":
                    row.get(
                        "sla_percentage",
                        "Not Available"
                    ),

                "predicted_resolution_hours":
                    row.get(
                        "predicted_resolution_hours",
                        "Not Available"
                    )
            }


            # =================================================
            # WORKLOAD
            # =================================================

            workload_data = {

                "workload":
                    row.get(
                        "workload",
                        "Not Available"
                    ),

                "workload_level":
                    row.get(
                        "workload_level",
                        "Not Available"
                    ),

                "workload_confidence":
                    row.get(
                        "workload_confidence",
                        "Not Available"
                    ),

                "total_incidents":
                    row.get(
                        "total_incidents",
                        "Not Available"
                    ),

                "active_incidents":
                    row.get(
                        "active_incidents",
                        "Not Available"
                    ),

                "pending_incidents":
                    row.get(
                        "pending_incidents",
                        "Not Available"
                    ),

                "resolved_incidents":
                    row.get(
                        "resolved_incidents",
                        "Not Available"
                    )
            }


            # =================================================
            # PERFORMANCE
            # =================================================

            performance_data = {

                "assigned_to":
                    row.get(
                        "assigned_to",
                        "Not Available"
                    ),

                "performance_prediction":
                    row.get(
                        "performance_prediction",
                        "Not Available"
                    ),

                "performance_category":
                    row.get(
                        "performance_category",
                        "Not Available"
                    ),

                "performance_confidence":
                    row.get(
                        "performance_confidence",
                        "Not Available"
                    ),

                "quality_score":
                    row.get(
                        "quality_score",
                        "Not Available"
                    ),

                "skill_score":
                    row.get(
                        "skill_score",
                        "Not Available"
                    ),

                "fcr":
                    row.get(
                        "fcr",
                        "Not Available"
                    )
            }


            # =================================================
            # GAMIFICATION
            # =================================================

            gamification_data = {

                "assigned_to":
                    row.get(
                        "assigned_to",
                        "Not Available"
                    ),

                "total_points":
                    row.get(
                        "total_points",
                        row.get(
                            "points",
                            "Not Available"
                        )
                    ),

                "points_per_ticket":
                    row.get(
                        "points_per_ticket",
                        "Not Available"
                    ),

                "badges":
                    row.get(
                        "badges",
                        "Not Available"
                    ),

                "rewards":
                    row.get(
                        "rewards",
                        "Not Available"
                    ),

                "achievements":
                    row.get(
                        "achievements",
                        "Not Available"
                    ),

                "level":
                    row.get(
                        "level",
                        "Not Available"
                    ),

                "leaderboard_rank":
                    row.get(
                        "leaderboard_rank",
                        "Not Available"
                    ),

                "monthly_rank":
                    row.get(
                        "monthly_rank",
                        "Not Available"
                    )
            }

                            # =================================================
                # CREATE FAISS QUERY
                # =================================================

            query = self.create_search_query(
                    incident_data
                )

                # =================================================
                # SEARCH FAISS
                # =================================================

            retrieved_incidents = (
                    self.llmconnect.search(
                        query=query,
                        top_k=self.p_config.top_k
                    )
                )

            print(
                    "Similar incidents:",
                    len(retrieved_incidents)
                )

                # =================================================
                # BUILD PROMPT
                # =================================================

            prompt = self.prompt.build_prompt(
                    task="recommendation",
                    incident_data=incident_data,
                    sla_data=sla_data,
                    workload_data=workload_data,
                    performance_data=performance_data,
                    gamification_data=gamification_data,
                    retrieved_incidents=retrieved_incidents
                )

            print(
                    "Prompt created successfully."
                )

                # =================================================
                # GENERATE RESPONSE
                # =================================================

            response = (
                    self.llmconnect.generate_response(
                        prompt
                    )
                )

                # =================================================
                # STORE RESPONSE
                # =================================================

            df.loc[index,"ai_recommendation"] = response

            print(
                    "Recommendation generated successfully."
                )

                    # ========================================================
            # SAVE ONCE AFTER ALL INCIDENTS
            # ========================================================
            output_path =os.path.join('Artifacts/AIRecommendation/AIRecommendation.csv')
            df.to_csv(output_path,index=False)

            print("\n" + "=" * 80)
            print("AI RECOMMENDATIONS COMPLETED")
            print("=" * 80)

            # print(
            #     "Output file:",
            #     self.config.local_datafile
            # )

        return df

           