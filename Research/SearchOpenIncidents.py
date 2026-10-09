import json
from pathlib import Path

import faiss
import numpy as np
import oracledb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

ORACLE_USER = "SERVICENOWGAMIFICATION"
ORACLE_PASSWORD = "RSR"
ORACLE_DSN = "localhost:1521/FREEPDB1"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5

FAISS_DIR = Path(
    "C:\\Users\\RSR\\PYTHON\\ServicenowGamification"
    "\\Artifacts\\AIRECOMMENDATIONS"
)

FAISS_INDEX_PATH = (
    FAISS_DIR
    / "historical_resolved_incidents.index"
)

DOCUMENTS_PATH = (
    FAISS_DIR
    / "historical_resolved_incidents.json"
)

OUTPUT_PATH = (
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
            RESOLVED_AT,
            CLOSED_AT,
            RESOLUTION_TIME,
            RESOLUTION_HOURS,
            SLA_STATUS,
            FCR,
            REOPEN_COUNT,
            REASSIGNMENT_COUNT,
            CUSTOMER_RATING
        FROM INCIDENT_GAMIFICATION_FINAL
        WHERE   UPPER(INS_STATE) NOT IN (
              'RESOLVED',
              'CLOSED'
          )
        ORDER BY OPENED_AT
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
# CREATE SEARCH TEXT
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

Resolution Hours:
{incident.get("resolution_hours") or ""}

SLA Status:
{incident.get("sla_status") or ""}

FCR:
{incident.get("fcr") or ""}

Reopen Count:
{incident.get("reopen_count") or ""}

Reassignment Count:
{incident.get("reassignment_count") or ""}
""".strip()


# ============================================================
# LOAD FAISS
# ============================================================

def load_faiss():

    if not FAISS_INDEX_PATH.exists():

        raise FileNotFoundError(
            f"FAISS index not found: "
            f"{FAISS_INDEX_PATH}"
        )

    if not DOCUMENTS_PATH.exists():

        raise FileNotFoundError(
            f"Documents file not found: "
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

    return index, documents


# ============================================================
# SEARCH TOP 5 RESOLVED INCIDENTS
# ============================================================

def search_similar_incidents(
    incident,
    index,
    documents,
    model
):

    text = create_incident_text(
        incident
    )

    embedding = model.encode(
        [text],
        normalize_embeddings=True
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    search_k = min(
        TOP_K + 10,
        index.ntotal
    )

    scores, indices = index.search(
        embedding,
        search_k
    )

    results = []

    current_number = str(
        incident.get("number_id")
    )

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

        historical_number = str(
            historical.get("number")
        )

        if historical_number == current_number:
            continue

        result = {
            "similarity_score":
                round(float(score), 4),

            "number":
                historical.get("number"),

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

            "state":
                historical.get(
                    "state"
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

            "opened_at":
                historical.get(
                    "opened_at"
                ),

            "resolved_at":
                historical.get(
                    "resolved_at"
                ),

            "closed_at":
                historical.get(
                    "closed_at"
                ),

            "resolution_time":
                historical.get(
                    "resolution_time"
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
                ),

            "customer_rating":
                historical.get(
                    "customer_rating"
                )
        }

        results.append(result)

        if len(results) == TOP_K:
            break

    return results


# ============================================================
# FORMAT OPEN INCIDENT
# ============================================================

def format_open_incident(incident):

    return {
        "number":
            incident.get("number_id"),

        "short_description":
            incident.get("short_description"),

        "description":
            incident.get("ins_description"),

        "priority":
            incident.get("ins_priority"),

        "state":
            incident.get("ins_state"),

        "assigned_to":
            incident.get("assigned_to"),

        "assignment_group":
            incident.get("assignment_group"),

        "category":
            incident.get("ins_category"),

        "subcategory":
            incident.get("subcategory"),

        "opened_at":
            str(incident.get("opened_at"))
            if incident.get("opened_at")
            else None,

        "resolved_at":
            str(incident.get("resolved_at"))
            if incident.get("resolved_at")
            else None,

        "closed_at":
            str(incident.get("closed_at"))
            if incident.get("closed_at")
            else None,

        "resolution_time":
            incident.get("resolution_time"),

        "resolution_hours":
            incident.get("resolution_hours"),

        "sla_status":
            incident.get("sla_status"),

        "fcr":
            incident.get("fcr"),

        "reopen_count":
            incident.get("reopen_count"),

        "reassignment_count":
            incident.get("reassignment_count"),

        "customer_rating":
            incident.get("customer_rating")
    }


# ============================================================
# PROCESS ALL OPEN INCIDENTS
# ============================================================

def process_open_incidents():

    incidents = get_open_incidents()

    if not incidents:

        return []

    index, documents = load_faiss()

    model = SentenceTransformer(
        MODEL_NAME
    )

    results = []

    for incident in incidents:

        similar_incidents = (
            search_similar_incidents(
                incident,
                index,
                documents,
                model
            )
        )

        result = {
            "open_incident":
                format_open_incident(
                    incident
                ),

            "similar_resolved_incidents":
                similar_incidents
        }

        results.append(result)

    return results


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):

    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
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

    results = process_open_incidents()

    save_results(
        results
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