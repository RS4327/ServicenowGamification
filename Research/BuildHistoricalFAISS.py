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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT/ "ServicenowGamification"
    / "Artifacts"
    / "AILLMRECOMMENDATIONS"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FAISS_INDEX_PATH = (
    OUTPUT_DIR
    / "historical_resolved_incidents.index"
)

DOCUMENTS_PATH = (
    OUTPUT_DIR
    / "historical_resolved_incidents.json"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "historical_resolved_incidents_metadata.json"
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
# GET RESOLVED INCIDENTS
# ============================================================

def get_resolved_incidents():

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
        WHERE RESOLVED_AT IS NOT NULL
           OR (
                RESOLVED_AT IS NULL
                AND UPPER(INS_STATE) IN (
                    'RESOLVED',
                    'CLOSED'
                )
           )
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
# CREATE SEARCHABLE TEXT
# ============================================================

def create_incident_text(incident):

    return f"""
ServiceNow Historical Resolved Incident

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
# BUILD FAISS INDEX
# ============================================================

def build_faiss_index(incidents):

    if not incidents:

        raise ValueError(
            "No resolved incidents found."
        )

    texts = [
        create_incident_text(incident)
        for incident in incidents
    ]

    model = SentenceTransformer(
        MODEL_NAME
    )

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    if embeddings.ndim != 2:

        raise ValueError(
            "Invalid embedding shape."
        )

    if embeddings.shape[0] != len(incidents):

        raise ValueError(
            "Embedding count does not match incident count."
        )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    return index, dimension


# ============================================================
# SAVE DOCUMENTS
# ============================================================

def save_documents(incidents):

    documents = []

    for incident in incidents:

        documents.append(
            {
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
        )

    with open(
        DOCUMENTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2,
            default=str
        )


# ============================================================
# SAVE METADATA
# ============================================================

def save_metadata(
    total_documents,
    vector_dimension
):

    metadata = {
        "embedding_model":
            MODEL_NAME,

        "vector_dimension":
            vector_dimension,

        "total_documents":
            total_documents,

        "index_type":
            "IndexFlatIP",

        "normalized_embeddings":
            True,

        "document_file":
            DOCUMENTS_PATH.name,

        "faiss_index_file":
            FAISS_INDEX_PATH.name
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# MAIN
# ============================================================

def main():

    incidents = get_resolved_incidents()

    if not incidents:

        raise ValueError(
            "No resolved incidents available for FAISS."
        )

    index, vector_dimension = build_faiss_index(
        incidents
    )

    faiss.write_index(
        index,
        str(FAISS_INDEX_PATH)
    )

    save_documents(
        incidents
    )

    save_metadata(
        total_documents=len(incidents),
        vector_dimension=vector_dimension
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()