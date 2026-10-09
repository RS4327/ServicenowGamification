import json
from pathlib import Path

import faiss
import numpy as np
import oracledb
import requests

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

ORACLE_USER = "SERVICENOWGAMIFICATION"
ORACLE_PASSWORD = "RSR"
ORACLE_DSN = "localhost:1521/FREEPDB1"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

TOP_K = 5


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(
    "C:\\Users\\RSR\\PYTHON\\ServicenowGamification"
)

FAISS_DIR = (
    BASE_DIR
    / "Artifacts"
    / "AIRECOMMENDATIONS"
)

FAISS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FAISS_INDEX_PATH = (
    FAISS_DIR
    / "historical_resolved_incidents.index"
)

DOCUMENTS_PATH = (
    FAISS_DIR
    / "historical_resolved_incidents.json"
)

SEARCH_RESULTS_PATH = (
    FAISS_DIR
    / "open_incident_similar_results.json"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )


# ============================================================
# GET ALL OPEN INCIDENTS
# ============================================================

def get_open_incidents():

    query = """
        SELECT
            i.NUMBER_ID,
            i.SHORT_DESCRIPTION,
            i.INS_DESCRIPTION,
            i.INS_PRIORITY,
            i.INS_STATE,
            i.ASSIGNED_TO,
            i.ASSIGNMENT_GROUP,
            i.INS_CATEGORY,
            i.SUBCATEGORY,
            i.OPENED_AT,
            i.RESOLUTION_TIME,
            i.RESOLUTION_HOURS,
            i.SLA_STATUS,
            i.FCR,
            i.REOPEN_COUNT,
            i.REASSIGNMENT_COUNT,
            i.CUSTOMER_RATING
        FROM INCIDENT_GAMIFICATION_FINAL i
        WHERE NVL(UPPER(TRIM(i.INS_STATE)), 'UNKNOWN')
              NOT IN ('RESOLVED', 'CLOSED')
          AND NOT EXISTS (
                SELECT 1
                FROM AI_RECOMMENDATION_HISTORY r
                WHERE TRIM(UPPER(r.INCIDENT_NUMBER))
                      = TRIM(UPPER(i.NUMBER_ID))
          )
        ORDER BY i.OPENED_AT
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

    return [
        dict(zip(columns, row))
        for row in rows
    ]


# ============================================================
# GET ONE INCIDENT
# ============================================================

def get_incident(incident_number):

    query = """
        SELECT
            NUMBER_ID,
            SHORT_DESCRIPTION,
            INS_DESCRIPTION,
            INS_PRIORITY,
            INS_STATE,
            ASSIGNED_TO,
            ASSIGNMENT_GROUP,
            INS_CATEGORY,
            SUBCATEGORY,
            OPENED_AT,
            RESOLUTION_TIME,
            RESOLUTION_HOURS,
            SLA_STATUS,
            FCR,
            REOPEN_COUNT,
            REASSIGNMENT_COUNT,
            CUSTOMER_RATING
        FROM INCIDENT_GAMIFICATION_FINAL
        WHERE NUMBER_ID = :incident_number
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                {
                    "incident_number": incident_number
                }
            )

            row = cursor.fetchone()

            if not row:
                return None

            columns = [
                column[0].lower()
                for column in cursor.description
            ]

    return dict(
        zip(columns, row)
    )


# ============================================================
# CREATE INCIDENT SEARCH TEXT
# ============================================================

def create_incident_text(incident):

    return f"""
ServiceNow Incident

Short Description:
{incident.get("short_description") or ""}

Description:
{incident.get("ins_description") or ""}

Priority:
{incident.get("ins_priority") or ""}

Category:
{incident.get("ins_category") or ""}

Subcategory:
{incident.get("subcategory") or ""}

Assignment Group:
{incident.get("assignment_group") or ""}

Assigned To:
{incident.get("assigned_to") or ""}

Reopen Count:
{incident.get("reopen_count") or ""}

Reassignment Count:
{incident.get("reassignment_count") or ""}
""".strip()


# ============================================================
# LOAD FAISS INDEX
# ============================================================

def load_faiss():

    if not FAISS_INDEX_PATH.exists():

        raise FileNotFoundError(
            f"FAISS index not found:\n"
            f"{FAISS_INDEX_PATH}"
        )

    if not DOCUMENTS_PATH.exists():

        raise FileNotFoundError(
            f"Historical documents not found:\n"
            f"{DOCUMENTS_PATH}"
        )

    index = faiss.read_index(
        str(FAISS_INDEX_PATH)
    )

    with open(
        DOCUMENTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        documents = json.load(file)

    if index.ntotal != len(documents):

        raise ValueError(
            "FAISS vector count does not match "
            "historical document count."
        )

    if index.ntotal == 0:

        raise ValueError(
            "FAISS index contains zero vectors."
        )

    return index, documents


# ============================================================
# SEARCH TOP 5 SIMILAR INCIDENTS
# ============================================================

def search_similar_incidents(
    incident,
    index,
    documents,
    model
):

    search_text = create_incident_text(
        incident
    )

    embedding = model.encode(
        [search_text],
        normalize_embeddings=True
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    search_count = min(
        TOP_K,
        index.ntotal
    )

    scores, indices = index.search(
        embedding,
        search_count
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id < 0:
            continue

        if index_id >= len(documents):
            continue

        historical = documents[
            int(index_id)
        ]

        results.append(
            {
                "similarity_score": round(
                    float(score),
                    4
                ),

                "number": historical.get(
                    "number"
                ),

                "short_description":
                    historical.get(
                        "short_description"
                    ),

                "description":
                    historical.get(
                        "description"
                    ),

                "priority":
                    historical.get(
                        "priority"
                    ),

                "category":
                    historical.get(
                        "category"
                    ),

                "subcategory":
                    historical.get(
                        "subcategory"
                    ),

                "assignment_group":
                    historical.get(
                        "assignment_group"
                    ),

                "assigned_to":
                    historical.get(
                        "assigned_to"
                    ),

                "resolution_hours":
                    historical.get(
                        "resolution_hours"
                    ),

                "sla_status":
                    historical.get(
                        "sla_status"
                    ),

                "fcr":
                    historical.get(
                        "fcr"
                    ),

                "reopen_count":
                    historical.get(
                        "reopen_count"
                    ),

                "reassignment_count":
                    historical.get(
                        "reassignment_count"
                    )
            }
        )

    return results


# ============================================================
# BUILD OLLAMA PROMPT
# ============================================================

def build_prompt(
    incident,
    similar_incidents
):

    historical_text = ""

    for position, item in enumerate(
        similar_incidents,
        start=1
    ):

        historical_text += f"""

HISTORICAL INCIDENT {position}

Incident Number:
{item.get("number")}

Similarity Score:
{item.get("similarity_score")}

Short Description:
{item.get("short_description")}

Description:
{item.get("description")}

Priority:
{item.get("priority")}

Category:
{item.get("category")}

Subcategory:
{item.get("subcategory")}

Assignment Group:
{item.get("assignment_group")}

Assigned To:
{item.get("assigned_to")}

Resolution Hours:
{item.get("resolution_hours")}

SLA Status:
{item.get("sla_status")}

FCR:
{item.get("fcr")}

Reopen Count:
{item.get("reopen_count")}

Reassignment Count:
{item.get("reassignment_count")}

----------------------------------------
"""

    prompt = f"""
You are an expert ServiceNow IT incident resolution assistant.

Analyze the current OPEN incident.

Use ONLY the historical resolved incidents provided below.

Recommend the most appropriate resolution based on the
similar historical incidents.

CURRENT OPEN INCIDENT

Incident Number:
{incident.get("number_id")}

Short Description:
{incident.get("short_description")}

Description:
{incident.get("ins_description")}

Priority:
{incident.get("ins_priority")}

State:
{incident.get("ins_state")}

Category:
{incident.get("ins_category")}

Subcategory:
{incident.get("subcategory")}

Assignment Group:
{incident.get("assignment_group")}

Assigned To:
{incident.get("assigned_to")}

Reopen Count:
{incident.get("reopen_count")}

Reassignment Count:
{incident.get("reassignment_count")}


HISTORICAL RESOLVED INCIDENTS

{historical_text}


Provide a practical resolution recommendation.

Use EXACTLY this format:

RECOMMENDATION:
<recommended resolution>

REASON:
<reason based on historical incidents>

RECOMMENDED_ASSIGNMENT_GROUP:
<recommended assignment group>

RECOMMENDED_ACTIONS:
1. <first action>
2. <second action>
3. <third action>

CONFIDENCE:
<High / Medium / Low>

SIMILAR_INCIDENTS_USED:
<comma separated incident numbers>

Rules:

1. Do not invent historical incidents.
2. Do not invent incident numbers.
3. Do not claim that an action has already been performed.
4. Base the recommendation on the supplied historical incidents.
5. If historical incidents disagree, explain the uncertainty.
""".strip()

    return prompt


# ============================================================
# CALL OLLAMA
# ============================================================

def generate_ollama_response(prompt):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    data = response.json()

    recommendation = data.get(
        "response"
    )

    if not recommendation:

        raise ValueError(
            "Ollama returned an empty response."
        )

    return recommendation.strip()


# ============================================================
# SAVE RECOMMENDATION
# ============================================================

def save_recommendation(
    incident_number,
    recommendation
):

    connection = get_connection()

    cursor = None

    try:

        cursor = connection.cursor()

        recommendation_id_var = cursor.var(
            oracledb.NUMBER
        )

        sql = """
            INSERT INTO AI_RECOMMENDATION_HISTORY
            (
                INCIDENT_NUMBER,
                RECOMMENDATION,
                CREATED_AT
            )
            VALUES
            (
                :incident_number,
                :recommendation,
                CURRENT_TIMESTAMP
            )
            RETURNING RECOMMENDATION_ID
            INTO :recommendation_id
        """

        cursor.execute(
            sql,
            {
                "incident_number":
                    incident_number,

                "recommendation":
                    recommendation,

                "recommendation_id":
                    recommendation_id_var
            }
        )

        value = (
            recommendation_id_var
            .getvalue()
        )

        if isinstance(value, list):
            value = value[0]

        recommendation_id = int(
            value
        )

        connection.commit()

        return recommendation_id

    except Exception:

        connection.rollback()

        raise

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# SAVE SIMILAR INCIDENTS
# ============================================================

def save_similar_incidents(
    recommendation_id,
    similar_incidents
):

    connection = get_connection()

    cursor = None

    try:

        cursor = connection.cursor()

        sql = """
            INSERT INTO AI_SIMILAR_INCIDENTS
            (
                RECOMMENDATION_ID,
                SIMILAR_INCIDENT_NUMBER,
                SIMILARITY_SCORE,
                SHORT_DESCRIPTION,
                ASSIGNMENT_GROUP,
                ASSIGNED_TO,
                PRIORITY,
                CATEGORY,
                SUBCATEGORY,
                RESOLUTION_HOURS,
                SLA_STATUS,
                FCR,
                REOPEN_COUNT,
                REASSIGNMENT_COUNT
            )
            VALUES
            (
                :recommendation_id,
                :similar_incident_number,
                :similarity_score,
                :short_description,
                :assignment_group,
                :assigned_to,
                :priority,
                :category,
                :subcategory,
                :resolution_hours,
                :sla_status,
                :fcr,
                :reopen_count,
                :reassignment_count
            )
        """

        for item in similar_incidents:

            cursor.execute(
                sql,
                {
                    "recommendation_id":
                        recommendation_id,

                    "similar_incident_number":
                        item.get("number"),

                    "similarity_score":
                        item.get(
                            "similarity_score"
                        ),

                    "short_description":
                        item.get(
                            "short_description"
                        ),

                    "assignment_group":
                        item.get(
                            "assignment_group"
                        ),

                    "assigned_to":
                        item.get(
                            "assigned_to"
                        ),

                    "priority":
                        item.get(
                            "priority"
                        ),

                    "category":
                        item.get(
                            "category"
                        ),

                    "subcategory":
                        item.get(
                            "subcategory"
                        ),

                    "resolution_hours":
                        item.get(
                            "resolution_hours"
                        ),

                    "sla_status":
                        item.get(
                            "sla_status"
                        ),

                    "fcr":
                        item.get(
                            "fcr"
                        ),

                    "reopen_count":
                        item.get(
                            "reopen_count"
                        ),

                    "reassignment_count":
                        item.get(
                            "reassignment_count"
                        )
                }
            )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        if cursor:
            cursor.close()

        connection.close()


# ============================================================
# PROCESS ONE OPEN INCIDENT
# ============================================================

def process_incident(
    incident,
    index,
    documents,
    model
):

    incident_number = incident.get(
        "number_id"
    )

    similar_incidents = (
        search_similar_incidents(
            incident,
            index,
            documents,
            model
        )
    )

    if not similar_incidents:

        raise ValueError(
            "No similar historical incidents found."
        )

    prompt = build_prompt(
        incident,
        similar_incidents
    )

    recommendation = (
        generate_ollama_response(
            prompt
        )
    )

    recommendation_id = (
        save_recommendation(
            incident_number,
            recommendation
        )
    )

    save_similar_incidents(
        recommendation_id,
        similar_incidents
    )

    return {
        "recommendation_id":
            recommendation_id,

        "incident_number":
            incident_number,

        "recommendation":
            recommendation,

        "similar_incidents":
            similar_incidents
    }


# ============================================================
# PROCESS ALL OPEN INCIDENTS
# ============================================================

def process_all_open_incidents():

    incidents = get_open_incidents()

    if not incidents:

        return []

    index, documents = load_faiss()

    model = SentenceTransformer(
        MODEL_NAME
    )

    results = []

    for incident in incidents:

        incident_number = incident.get(
            "number_id"
        )

        try:

            result = process_incident(
                incident,
                index,
                documents,
                model
            )

            results.append(
                {
                    "status":
                        "SUCCESS",

                    **result
                }
            )

        except Exception as error:

            results.append(
                {
                    "status":
                        "FAILED",

                    "incident_number":
                        incident_number,

                    "error":
                        str(error)
                }
            )

    return results


# ============================================================
# SAVE JSON RESULTS
# ============================================================

def save_results(results):

    with open(
        SEARCH_RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
            default=str
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("AI INCIDENT RECOMMENDATION")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1: GET OPEN INCIDENTS
    # --------------------------------------------------------

    print("\nLoading open incidents...")

    incidents = get_open_incidents()

    if not incidents:

        print(
            "No open incidents found."
        )

        return

    print(
        f"Open incidents found: {len(incidents)}"
    )

    # --------------------------------------------------------
    # STEP 2: LOAD FAISS
    # --------------------------------------------------------

    print("\nLoading FAISS index...")

    index, documents = load_faiss()

    print(
        f"Historical incidents loaded: "
        f"{len(documents)}"
    )

    print(
        f"FAISS vectors: "
        f"{index.ntotal}"
    )

    # --------------------------------------------------------
    # STEP 3: LOAD EMBEDDING MODEL
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print(
        "Embedding model loaded successfully."
    )

    # --------------------------------------------------------
    # STEP 4: PROCESS INCIDENTS
    # --------------------------------------------------------

    results = []

    for incident in incidents:

        incident_number = incident.get(
            "number_id"
        )

        print(
            "\n" + "-" * 70
        )

        print(
            f"Processing incident: "
            f"{incident_number}"
        )

        try:

            result = process_incident(
                incident,
                index,
                documents,
                model
            )

            results.append(
                {
                    "status":
                        "SUCCESS",

                    **result
                }
            )

            print(
                f"Completed: "
                f"{incident_number}"
            )

            print(
                f"Recommendation ID: "
                f"{result.get('recommendation_id')}"
            )

            print(
                "Similar incidents:"
            )

            for item in result.get(
                "similar_incidents",
                []
            ):

                print(
                    f"  {item.get('number')} "
                    f"-> "
                    f"{item.get('similarity_score')}"
                )

        except Exception as error:

            results.append(
                {
                    "status":
                        "FAILED",

                    "incident_number":
                        incident_number,

                    "error":
                        str(error)
                }
            )

            print(
                f"Failed: "
                f"{incident_number}"
            )

            print(
                f"Error: {error}"
            )

    # --------------------------------------------------------
    # STEP 5: SAVE JSON
    # --------------------------------------------------------

    save_results(
        results
    )

    # --------------------------------------------------------
    # FINAL OUTPUT
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "PROCESS COMPLETED"
    )

    print(
        "=" * 70
    )

    print(
        f"Results saved to:"
    )

    print(
        SEARCH_RESULTS_PATH
    )

    print(
        f"\nTotal processed: "
        f"{len(results)}"
    )

    success_count = sum(
        1
        for result in results
        if result.get("status") == "SUCCESS"
    )

    failed_count = sum(
        1
        for result in results
        if result.get("status") == "FAILED"
    )

    print(
        f"Successful: {success_count}"
    )

    print(
        f"Failed: {failed_count}"
    )

    print(
        "\nJSON RESULT:"
    )

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
            default=str
        )
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()