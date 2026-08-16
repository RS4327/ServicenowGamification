import pandas as pd 
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from ollama import Client

from ServicenowGamification.Utils.Common import *
from ServicenowGamification.Constant import * 
from ServicenowGamification.Entity.Config_Entity import * 




class CreateEmbedings:

    def __init__(
        self,
        config: CreateEmbendingsConfig
    ):

        self.config = config
        
        self.model = None
        self.index = None
        self.documents = None
        self.params = Read_Yaml(PARAMS_FILE_PATH)

    def connect(self):

        try:

            print("=" * 70)
            print("Connecting to Ollama Server")
            print("=" * 70)

            print("Host  :", self.config.base_url)
            print("Model :", self.config.model)

            self.client = Client(
                host=self.config.base_url
            )

            print("Ollama Client Created Successfully")

            return self.client

        except Exception as e:

            print("Ollama Connection Error:", e)

            raise Exception(
                "Unable to create Ollama Client."
            )

    ###############################################################
    # Test Connection
    ###############################################################
    def test_connection(self):

        try:

            print("\nChecking Ollama Server...")

            models = self.client.list()

            print("Connection Successful")

            print("\nAvailable Models:")

            for model in models.models:

                print(" -", model.model)

            return True

        except Exception as e:

            print("Actual Error:")
            print(type(e))
            print(e)

            raise Exception(
                "Unable to connect to Ollama Server."
            )

    ###############################################################
    # List Models
    ###############################################################
    def list_models(self):

        try:

            models = self.client.list()

            print("=" * 70)
            print('models ', models)
            print("Available Models")
            print("=" * 70)

            for model in models.models:

                print(model.model)
            return models

        except Exception as e:

            print("Model List Error:", e)

            raise e

    ###############################################################
    # Generate Response
    ###############################################################
    def generate_response(self, prompt):

        try:

            response = self.client.chat(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.config.system_prompt
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                options={

                    "temperature":
                        self.config.temperature,

                    "top_p":
                        self.config.top_p,

                    "num_predict":
                        self.config.max_tokens

                }
            )

            answer = response.message.content

            return answer

        except Exception as e:

            print("LLM Generation Error:")
            print(e)

            raise Exception(
                "Unable to Generate Response."
            )


    def Create_Embendings(self):

        print("=" * 70)
        print("CREATING SERVICE NOW INCIDENT EMBEDDINGS")
        print("=" * 70)

        # ------------------------------------------------------
        # Load embedding model
        # ------------------------------------------------------

        print("Loading embedding model...")

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

        # ------------------------------------------------------
        # Validate source file
        # ------------------------------------------------------

        source_path = Path(
            self.config.source_path
        )

        print("Source file:", source_path.resolve())

        if not source_path.exists():

            raise FileNotFoundError(
                f"Source CSV not found: "
                f"{source_path.resolve()}"
            )

        # ------------------------------------------------------
        # Load ServiceNow data
        # ------------------------------------------------------

        df = pd.read_csv(
            source_path
        )

        print("Data shape:", df.shape)

        # ------------------------------------------------------
        # Required columns
        # ------------------------------------------------------

        required_columns = [

            "number",
            "short_description",
            "category",
            "subcategory",
            "priority",
            "assignment_group",
            "assigned_to",
            "resolution_hours",
            "mttr",
            "sla_percentage",
            "sla_status",
            "workload_level",
            "performance_prediction",
            "confidence",
            "points",
            "badges",
            "achievement",
            "level",
            "leaderboard_rank",
            "monthly_rank"

        ]

        # ------------------------------------------------------
        # Validate columns
        # ------------------------------------------------------

        missing_columns = [

            col
            for col in required_columns
            if col not in df.columns

        ]

        if missing_columns:

            raise ValueError(
                "Missing columns for embedding: "
                f"{missing_columns}"
            )

        print(
            "All required columns are available."
        )

        # ------------------------------------------------------
        # Create incident documents
        # ------------------------------------------------------

        documents = []

        for _, row in df.iterrows():

            text = f"""
ServiceNow Incident

Incident Number:
{row['number']}

Short Description:
{row['short_description']}

Category:
{row['category']}

Sub Category:
{row['subcategory']}

Priority:
{row['priority']}

Assignment Group:
{row['assignment_group']}

Assigned To:
{row['assigned_to']}

Resolution Hours:
{row['resolution_hours']}

MTTR:
{row['mttr']}

SLA Percentage:
{row['sla_percentage']}

SLA Status:
{row['sla_status']}

Workload Level:
{row['workload_level']}

Performance Prediction:
{row['performance_prediction']}

Performance Confidence:
{row['confidence']}

Points:
{row['points']}

Badges:
{row['badges']}

Achievement:
{row['achievement']}

Level:
{row['level']}

Leaderboard Rank:
{row['leaderboard_rank']}

Monthly Rank:
{row['monthly_rank']}
"""

            documents.append(
                text.strip()
            )

        print(
            "Total documents:",
            len(documents)
        )

        # ------------------------------------------------------
        # Generate embeddings
        # ------------------------------------------------------

        print("Generating embeddings...")

        embeddings = model.encode(

            documents,

            show_progress_bar=True

        )

        print(
            "Embedding shape:",
            embeddings.shape
        )

        # ------------------------------------------------------
        # Convert to float32
        # ------------------------------------------------------

        embeddings = embeddings.astype(
            "float32"
        )

        # ------------------------------------------------------
        # Create FAISS index
        # ------------------------------------------------------

        dimension = embeddings.shape[1]

        print(
            "Embedding dimension:",
            dimension
        )

        index = faiss.IndexFlatL2(
            dimension
        )

        # ------------------------------------------------------
        # Save FAISS index
        # ------------------------------------------------------

        output_folder=self.config.root_dir
        faiss_index_path=os.path.join(output_folder, "save_faiss_index.index")
        
        faiss.write_index(

            index,

            str(faiss_index_path)

        )

        print(
            "FAISS index saved:",
            faiss_index_path
        )

        # ------------------------------------------------------
        # Save documents
        # ------------------------------------------------------


        documents_path = faiss_index_path=os.path.join(output_folder, "documents.pkl")
       
        with open(
            documents_path,
            "wb"
        ) as f:
            pickle.dump(
                documents,
                f
            )

        print(
            "Documents saved:",
            documents_path
        )

        model_path = Path("Artifacts/LLMEmbenddings/embeddings.npy")
        model.save(str(model_path))

        #np.save("Artifacts/LLMEmbeddings/embeddings.npy",embeddings)

        # model_path = "Artifacts/LLMEmbenddings/embedding_model.pkl"

        # with open(model_path, "wb") as f:
        #     pickle.dump(model, f)



    def load_embedding_model(self):
        print("=" * 70)
        print("LOADING EMBEDDING MODEL")
        print("=" * 70)

        try:
            self.model = SentenceTransformer(
                self.config.embedding_model
            )

            print(
                "Embedding Model:",
                self.config.embedding_model
            )

            print("Embedding Model Loaded Successfully")

            return self.model

        except Exception as e:

            print("Embedding Model Error:")
            print(e)

            raise Exception(
                "Unable to load embedding model."
            )
    ###############################################################
    # Load FAISS Index
    ###############################################################

    def load_faiss_index(self):

        print("=" * 70)
        print("LOADING FAISS INDEX")
        print("=" * 70)

        index_path = Path(
            self.config.faiss_index
        )

        print(
            "FAISS Index:",
            index_path.resolve()
        )

        if not index_path.exists():

            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{index_path.resolve()}"
            )

        try:

            self.index = faiss.read_index(
                str(index_path)
            )

            print(
                "FAISS Index Loaded Successfully"
            )

            print(
                "Total Vectors:",
                self.index.ntotal
            )

            return self.index

        except Exception as e:

            print("FAISS Loading Error:")
            print(e)

            raise Exception(
                "Unable to load FAISS index."
            )

    ###############################################################
    # Load Documents
    ###############################################################

    def load_documents(self):

        print("=" * 70)
        print("LOADING INCIDENT DOCUMENTS")
        print("=" * 70)

        documents_path = Path(
            self.config.documents_path
        )

        print(
            "Documents:",
            documents_path.resolve()
        )

        if not documents_path.exists():

            raise FileNotFoundError(
                f"Documents file not found: "
                f"{documents_path.resolve()}"
            )

        try:

            with open(
                documents_path,
                "rb"
            ) as f:

                self.documents = pickle.load(f)

            print(
                "Documents Loaded Successfully"
            )

            print(
                "Total Documents:",
                len(self.documents)
            )

            return self.documents

        except Exception as e:

            print("Document Loading Error:")
            print(e)

            raise Exception(
                "Unable to load incident documents."
            )
    ###############################################################
    # Load Everything
    ###############################################################

    def load_resources(self):

        print("=" * 70)
        print("LOADING FAISS RESOURCES")
        print("=" * 70)

        self.load_embedding_model()

        self.load_faiss_index()

        self.load_documents()

        print("=" * 70)
        print("ALL FAISS RESOURCES LOADED")
        print("=" * 70)
    ###############################################################
    # Create Query Embedding
    ###############################################################

    def create_query_embedding(
        self,
        query
    ):

        if self.model is None:

            self.load_embedding_model()

        print(
            "\nCreating query embedding..."
        )

        query_embedding = self.model.encode(
            [query]
        )

        query_embedding = query_embedding.astype(
            "float32"
        )

        print(
            "Query embedding shape:",
            query_embedding.shape
        )

        return query_embedding
     ###############################################################
    # Search FAISS
    ###############################################################

    def search(self,query,top_k=None):

        print("=" * 70)
        print("SEARCHING RELEVANT INCIDENTS")
        print("=" * 70)
        if self.index is None:
            self.load_faiss_index()
        if self.documents is None:
            self.load_documents()
        if self.model is None:
            self.load_embedding_model()
        # ----------------------------------------------------------
        # Get top K
        # ----------------------------------------------------------

        if top_k is None:
            top_k = self.config.top_k
        # ----------------------------------------------------------
        # Make sure K doesn't exceed document count
        # ----------------------------------------------------------

        top_k = min(top_k,len(self.documents))

        # ----------------------------------------------------------
        # Create query embedding
        # ----------------------------------------------------------

        query_embedding = self.create_query_embedding( query)

        # ----------------------------------------------------------
        # Search FAISS
        # ----------------------------------------------------------

        distances, indices = self.index.search( query_embedding, top_k)

        # ----------------------------------------------------------
        # Prepare results
        # ----------------------------------------------------------

        results = []

        for rank, (index_id, distance) in enumerate(
            zip(
                indices[0],
                distances[0]
            ),
            start=1
        ):

            # FAISS can return -1 if no result
            if index_id == -1:
                continue

            document = self.documents[index_id]

            result = {

                "rank": rank,

                "index": int(index_id),

                "distance": float(distance),

                "document": document

            }

            results.append(
                result
            )

        # ----------------------------------------------------------
        # Display results
        # ----------------------------------------------------------

        print(
            "\nQuery:",
            query
        )

        print(
            "\nRetrieved Incidents:",
            len(results)
        )

        for result in results:

            print("\n" + "-" * 70)

            print(
                "Rank:",
                result["rank"]
            )

            print(
                "FAISS Index:",
                result["index"]
            )

            print(
                "Distance:",
                round(
                    result["distance"],
                    4
                )
            )

            print(
                "Incident:"
            )

            print(
                result["document"]
            )

        print("\n" + "=" * 70)

        return results

     ###############################################################
    # Retrieve Only Documents
    ###############################################################

    def retrieve_documents(self,query,top_k=None):

        results = self.search(
            query,
            top_k
        )

        documents = [
            result["document"]
            for result in results

        ]

        return documents




class PromptBuilder:

    def __init__(self, config=None):
        self.config = config

    # ============================================================
    # Safe value
    # ============================================================

    def _get_value( self,data,key,default="N/A"):
        if data is None:
            return default
        value = data.get(key, default)

        if value is None:
            return default
        return value

    # ============================================================
    # Incident Data
    # ============================================================

    def format_incident_data(self,incident_data):

        incident_context = f"""
================ INCIDENT DATA ================

Incident Number:
{self._get_value(incident_data, "number")}

Short Description:
{self._get_value(incident_data, "short_description")}

Description:
{self._get_value(incident_data, "description")}

Category:
{self._get_value(incident_data, "category")}

Subcategory:
{self._get_value(incident_data, "subcategory")}

Priority:
{self._get_value(incident_data, "priority")}

Assignment Group:
{self._get_value(incident_data, "assignment_group")}

Assigned Agent:
{self._get_value(incident_data, "assigned_to")}

Resolution Hours:
{self._get_value(incident_data, "resolution_hours")}

MTTR:
{self._get_value(incident_data, "mttr")}

Customer Rating:
{self._get_value(incident_data, "customer_rating")}
"""
        return incident_context.strip()

    # ============================================================
    # SLA Prediction
    # ============================================================

    def format_sla_prediction(self,sla_data):

        if not sla_data:
            return """
================ SLA PREDICTION ================

SLA prediction is not available.
""".strip()

        sla_context = f"""
================ SLA PREDICTION ================

Predicted SLA Status:
{self._get_value(
    sla_data,
    "sla_prediction"
)}

SLA Confidence:
{self._get_value(
    sla_data,
    "sla_confidence"
)}

SLA Percentage:
{self._get_value(
    sla_data,
    "sla_percentage"
)}

Predicted Resolution Hours:
{self._get_value(
    sla_data,
    "predicted_resolution_hours"
)}
"""

        return sla_context.strip()

    # ============================================================
    # Combine Incident + SLA
    # ============================================================

#     def build_incident_sla_context(self, incident_data,sla_data):

#         incident_context = self.format_incident_data(incident_data)

#         sla_context = self.format_sla_prediction(sla_data)

#         combined_context = f"""
# {incident_context}

# {sla_context}
# """

#         return combined_context.strip()

#     # ============================================================
#     # Create SLA Analysis Prompt
#     # ============================================================

#     def build_sla_prompt(self,incident_data,sla_data):

#         context = self.build_incident_sla_context(incident_data,sla_data)

#         prompt = f"""
# You are an AI-powered IT Service Desk Assistant.

# Analyze the following ServiceNow incident and its
# SLA prediction.

# {context}

# Based on the information provided:

# 1. Explain the current incident situation.
# 2. Analyze the SLA risk.
# 3. Determine whether immediate action is required.
# 4. Explain the main factors contributing to the SLA risk.
# 5. Provide a recommended action for the Service Desk agent.

# Important rules:

# - Use only the information provided.
# - Do not invent missing values.
# - If information is unavailable, state "Not Available".
# - Keep the recommendation practical and concise.

# Return the response using the following format:

# Incident Analysis:
# <analysis>

# SLA Risk:
# <Low / Medium / High>

# Reason:
# <reason>

# Recommended Action:
# <action>
# """

#         return prompt.strip()


    # ============================================================
    # Workload Prediction
    # ============================================================

    def format_workload_prediction(
        self,
        workload_data
    ):

        if not workload_data:

            return """
================ WORKLOAD PREDICTION ================

Workload prediction is not available.
""".strip()

        workload_context = f"""
================ WORKLOAD PREDICTION ================

Predicted Workload:
{self._get_value(
    workload_data,
    "workload_prediction"
)}

Workload Level:
{self._get_value(
    workload_data,
    "workload_level"
)}

Workload Confidence:
{self._get_value(
    workload_data,
    "confidence"
)}

Total Incidents:
{self._get_value(
    workload_data,
    "total_incidents"
)}

Active Incidents:
{self._get_value(
    workload_data,
    "active_incidents"
)}

Pending Incidents:
{self._get_value(
    workload_data,
    "pending_incidents"
)}

Resolved Incidents:
{self._get_value(
    workload_data,
    "resolved_incidents"
)}
"""

        return workload_context.strip()

    # ============================================================
    # Agent Performance
    # ============================================================

    def format_agent_performance(
        self,
        performance_data
    ):

        if not performance_data:

            return """
================ AGENT PERFORMANCE ================

Agent performance prediction is not available.
""".strip()

        performance_context = f"""
================ AGENT PERFORMANCE ================

Agent:
{self._get_value(
    performance_data,
    "assigned_to"
)}

Performance Prediction:
{self._get_value(
    performance_data,
    "performance_prediction"
)}

Performance Category:
{self._get_value(
    performance_data,
    "performance_category"
)}

Performance Confidence:
{self._get_value(
    performance_data,
    "confidence"
)}

Quality Score:
{self._get_value(
    performance_data,
    "quality_score"
)}

Skill Score:
{self._get_value(
    performance_data,
    "skill_score"
)}

FCR:
{self._get_value(
    performance_data,
    "fcr"
)}

MTTR:
{self._get_value(
    performance_data,
    "mttr"
)}

SLA Percentage:
{self._get_value(
    performance_data,
    "sla_percentage"
)}
"""

        return performance_context.strip()

   
     # ============================================================
    # Gamification Data
    # ============================================================

    def format_gamification(
        self,
        gamification_data
    ):

        if not gamification_data:

            return """
================ GAMIFICATION ================

Gamification data is not available.
""".strip()

        gamification_context = f"""
================ GAMIFICATION ================

Agent:
{self._get_value(
    gamification_data,
    "assigned_to"
)}

Total Points:
{self._get_value(
    gamification_data,
    "total_points"
)}

Points Per Ticket:
{self._get_value(
    gamification_data,
    "points_per_ticket"
)}

Badges:
{self._get_value(
    gamification_data,
    "badges"
)}

Rewards:
{self._get_value(
    gamification_data,
    "rewards"
)}

Achievements:
{self._get_value(
    gamification_data,
    "achievements"
)}

Level:
{self._get_value(
    gamification_data,
    "level"
)}

Leaderboard Rank:
{self._get_value(
    gamification_data,
    "leaderboard_rank"
)}

Monthly Rank:
{self._get_value(
    gamification_data,
    "monthly_rank"
)}

Recognition Score:
{self._get_value(
    gamification_data,
    "recognition_score"
)}
"""

        return gamification_context.strip()

    # ============================================================
    # FAISS Retrieved Incidents
    # ============================================================

    def format_faiss_results(self,retrieved_incidents):

        if not retrieved_incidents:

            return """
================ FAISS SIMILAR INCIDENTS ================

No similar incidents were retrieved from FAISS.
""".strip()

        formatted_results = []

        for index, result in enumerate(
            retrieved_incidents,
            start=1
        ):

            rank = result.get(
                "rank",
                index
            )

            distance = result.get(
                "distance",
                "N/A"
            )

            document = result.get(
                "document",
                "N/A"
            )

            result_text = f"""
Similar Incident {rank}

FAISS Distance:
{distance}

Incident Information:
{document}
""".strip()

            formatted_results.append(
                result_text
            )

        return (
            "\n\n".join(
                formatted_results
            )
        )

        # ============================================================
    # Complete Operational Context
    # ============================================================

    def build_complete_context(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        incident_context = (self.format_incident_data(incident_data))
        sla_context = ( self.format_sla_prediction(sla_data))
        workload_context = (self.format_workload_prediction(workload_data))
        performance_context = (self.format_agent_performance(performance_data))
        gamification_context = (self.format_gamification(gamification_data))
        faiss_context = (self.format_faiss_results(retrieved_incidents ))

        complete_context = f"""

{incident_context}
{sla_context}
{workload_context}
{performance_context}
{gamification_context}
{faiss_context}

""".strip()

        return complete_context
        
        # ============================================================
    # Task 1 - AI Recommendation
    # ============================================================

    def build_recommendation_prompt(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        context = self.build_complete_context(
            incident_data,
            sla_data,
            workload_data,
            performance_data,
            gamification_data,
            retrieved_incidents
        )

        prompt = f"""
You are an AI-powered IT Service Desk Performance Assistant.

Analyze the following ServiceNow operational information:

{context}

Provide an actionable recommendation.

Analyze:

1. Incident situation
2. SLA risk
3. Workload risk
4. Agent performance
5. Gamification performance
6. Similar incident patterns

Then provide:

7. Immediate action
8. Preventive action
9. Agent recommendation
10. Escalation recommendation
11. Recognition or reward recommendation

Rules:

- Use only the provided information.
- Do not invent values.
- Do not invent incident numbers.
- Do not invent knowledge article numbers.
- If information is unavailable, say "Not Available".
- Use FAISS incidents only as supporting historical context.

Return:

Incident Analysis:
<analysis>

SLA Risk:
<risk>

Workload Risk:
<risk>

Agent Performance:
<analysis>

Gamification Analysis:
<analysis>

Immediate Action:
<action>

Preventive Action:
<action>

Escalation Recommendation:
<action>

Recognition Recommendation:
<action>
"""

        return prompt.strip()

        # ============================================================
    # Task 2 - Incident Summary
    # ============================================================

    def build_incident_summary_prompt(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        context = self.build_complete_context(
            incident_data,
            sla_data,
            workload_data,
            performance_data,
            gamification_data,
            retrieved_incidents
        )

        prompt = f"""
You are an IT Service Desk Incident Analyst.

Analyze the following information:

{context}

Create a concise incident summary.

Include:

1. Incident Overview
2. Current Situation
3. SLA Status
4. Workload Impact
5. Agent Performance
6. Similar Incident Pattern
7. Recommended Next Action

Rules:

- Use only the provided information.
- Do not invent missing information.
- Do not invent incident details.
- Clearly state unavailable information.

Return the response using:

Incident Overview:
<summary>

Current Situation:
<summary>

SLA Status:
<status>

Workload Impact:
<impact>

Agent Performance:
<assessment>

Similar Incident Pattern:
<pattern>

Recommended Next Action:
<action>
"""

        return prompt.strip()

        # ============================================================
    # Task 3 - Manager Insights
    # ============================================================

    def build_manager_insights_prompt(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        context = self.build_complete_context(
            incident_data,
            sla_data,
            workload_data,
            performance_data,
            gamification_data,
            retrieved_incidents
        )

        prompt = f"""
You are an IT Service Desk Manager Assistant.

Analyze the following operational information:

{context}

Generate actionable management insights.

Focus on:

1. SLA performance
2. Workload risk
3. Agent performance
4. Service Desk efficiency
5. Performance risks
6. Coaching opportunities
7. Recognition opportunities
8. Escalation requirements
9. Staffing concerns
10. Process improvement opportunities

Rules:

- Do not invent metrics.
- Use only the information provided.
- Clearly distinguish actual information from recommendations.
- Use historical FAISS incidents only as supporting evidence.

Return:

Management Summary:
<summary>

SLA Insights:
<insights>

Workload Insights:
<insights>

Agent Insights:
<insights>

Coaching Opportunities:
<opportunities>

Recognition Opportunities:
<opportunities>

Recommended Management Actions:
<actions>
"""

        return prompt.strip()

        # ============================================================
    # Task 4 - Knowledge Article Suggestion
    # ============================================================

    def build_knowledge_article_prompt(
        self,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        context = self.build_complete_context(
            incident_data,
            sla_data,
            workload_data,
            performance_data,
            gamification_data,
            retrieved_incidents
        )

        prompt = f"""
You are an IT Service Desk Knowledge Management Assistant.

Analyze the current incident and similar historical incidents.

{context}

Determine whether a knowledge article would help resolve
or prevent this type of incident.

Provide:

1. Recommended Article Title
2. Problem Description
3. Symptoms
4. Possible Root Cause
5. Resolution Steps
6. Preventive Steps
7. Target Support Group
8. Search Keywords

Rules:

- Do not invent an existing knowledge article.
- Do not invent a knowledge article number.
- If no existing article is available, recommend a new article.
- Use similar FAISS incidents as supporting context.
- Clearly state when information is unavailable.

Return:

Article Recommendation:
<recommendation>

Article Title:
<title>

Problem:
<problem>

Symptoms:
<symptoms>

Possible Root Cause:
<root cause>

Resolution:
<resolution>

Prevention:
<prevention>

Target Support Group:
<group>

Keywords:
<keywords>
"""

        return prompt.strip()

        # ============================================================
    # Generic Task-Specific Prompt Builder
    # ============================================================

    def build_prompt(
        self,
        task,
        incident_data,
        sla_data=None,
        workload_data=None,
        performance_data=None,
        gamification_data=None,
        retrieved_incidents=None
    ):

        task = task.lower().strip()

        if task in [
            "recommendation",
            "recommendations",
            "ai_recommendation"
        ]:

            return self.build_recommendation_prompt(
                incident_data,
                sla_data,
                workload_data,
                performance_data,
                gamification_data,
                retrieved_incidents
            )

        elif task in [
            "summary",
            "incident_summary"
        ]:

            return self.build_incident_summary_prompt(
                incident_data,
                sla_data,
                workload_data,
                performance_data,
                gamification_data,
                retrieved_incidents
            )

        elif task in [
            "manager",
            "manager_insights"
        ]:

            return self.build_manager_insights_prompt(
                incident_data,
                sla_data,
                workload_data,
                performance_data,
                gamification_data,
                retrieved_incidents
            )

        elif task in [
            "knowledge",
            "knowledge_article",
            "knowledge_article_suggestion"
        ]:

            return self.build_knowledge_article_prompt(
                incident_data,
                sla_data,
                workload_data,
                performance_data,
                gamification_data,
                retrieved_incidents
            )

        else:

            raise ValueError(
                f"Unsupported prompt task: {task}"
            )





