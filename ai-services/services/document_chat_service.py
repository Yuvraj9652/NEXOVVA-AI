import urllib.parse
import traceback

from services.embedding_service import create_embeddings
from services.vector_db import collection
from services.conversation_service import (
    get_conversation_history,
    save_message,
)
from llm.router import generate_text
from config.logger import logger


async def chat_with_document(session_id: str, filename: str, question: str, organization_id: str = "default"):
    # URL-decode filename to prevent mismatch issues
    filename = urllib.parse.unquote(filename)
    logger.info(f"[DOC-CHAT] Session {session_id} - Question for '{filename}' (Org: {organization_id}): '{question}'")

    try:
        history = get_conversation_history(session_id)
        history_text = ""
        for msg in history:
            history_text += f"{msg['role']}: {msg['content']}\n"
    except Exception as e:
        logger.warning(f"[DOC-CHAT] Failed to retrieve history for session {session_id}: {e}")
        history_text = ""

    try:
        logger.info("[DOC-CHAT] Generating query embedding...")
        question_embeddings = create_embeddings([question])
        if not question_embeddings:
            raise Exception("Failed to generate query embedding.")
        question_embedding = question_embeddings[0]
    except Exception as e:
        logger.error(f"[DOC-CHAT] Embedding generation failed: {e}")
        return {
            "answer": "Error: Embedding generation failed.",
            "sources": []
        }

    # Build multi-tenant filter query
    where_filter = {"organization_id": str(organization_id)}
    if filename and filename not in ["all", "undefined", "null", ""]:
        where_filter = {
            "$and": [
                {"organization_id": str(organization_id)},
                {"filename": filename}
            ]
        }

    logger.info(f"[DOC-CHAT] Querying ChromaDB with filter: {where_filter}")
    results = None
    try:
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=5,
            where=where_filter
        )
    except Exception as e:
        logger.error(f"[DOC-CHAT] ChromaDB query failed: {e}\n{traceback.format_exc()}")
        return {
            "answer": "Error: ChromaDB unavailable.",
            "sources": []
        }

    # Diagnostic checks if no documents returned
    if not results or not results.get("documents") or not results["documents"][0]:
        logger.warning("[DOC-CHAT] No chunks returned. Running diagnostics...")
        try:
            # 1. Check if organization has any vectors stored
            org_count_res = collection.get(where={"organization_id": str(organization_id)}, limit=1)
            if not org_count_res or not org_count_res.get("ids"):
                logger.info("[DOC-CHAT] Diagnostic: No vectors found for this organization.")
                return {
                    "answer": "Error: No vectors stored.",
                    "sources": []
                }
            
            # 2. Check if the specific document is indexed (if filtered)
            if filename and filename not in ["all", "undefined", "null", ""]:
                doc_count_res = collection.get(where={
                    "$and": [
                        {"organization_id": str(organization_id)},
                        {"filename": filename}
                    ]
                }, limit=1)
                if not doc_count_res or not doc_count_res.get("ids"):
                    logger.info(f"[DOC-CHAT] Diagnostic: Document '{filename}' is not indexed.")
                    return {
                        "answer": "Error: Document not indexed.",
                        "sources": []
                    }

            logger.info("[DOC-CHAT] Diagnostic: Document exists but metadata filter/similarity query returned empty.")
            return {
                "answer": "Error: Metadata filter returned zero matches.",
                "sources": []
            }
        except Exception as diag_err:
            logger.error(f"[DOC-CHAT] Diagnostic failed: {diag_err}")
            return {
                "answer": "Error: Metadata filter returned zero matches.",
                "sources": []
            }

    documents = results["documents"][0]
    metadata = results["metadatas"][0]
    distances = results.get("distances", [[]])[0]

    logger.info(f"[DOC-CHAT] Retrieved {len(documents)} chunks. Distances: {distances}")
    for idx, (doc, meta) in enumerate(zip(documents, metadata)):
        logger.info(f"Chunk {idx+1} | Source: {meta.get('filename')} | Snippet: {doc[:100]}...")

    context = "\n\n".join(documents)
    if not context.strip():
        return {
            "answer": "Error: No readable text found in document.",
            "sources": []
        }

    # Summarization check
    is_summary_request = any(w in question.lower() for w in ["summarize", "summary", "overview"])
    if is_summary_request:
        logger.info("[DOC-CHAT] Detected summary request. Formulating structured prompt...")
        prompt = f"""You are NEXOVVA AI.

You must answer ONLY using the supplied context. Do NOT use outside knowledge.
Generate a structured summary of the document using ONLY the provided context chunks.

The summary MUST include:
- Document title: [Document title, if available or extractable from context, otherwise use '{filename}']
- Overall purpose: [Brief summary of the main goal/purpose of the document]
- Main topics: [List the major topics covered]
- Key points: [Bullet points of the critical details]
- Important entities: [List people, companies, dates, technologies, skills, etc., mentioned in the context]
- Final conclusion: [Summary of the conclusion or final remarks]

Previous Conversation:
{history_text}

Context:
{context}

Question:
{question}
"""
    else:
        prompt = f"""You are NEXOVVA AI.

Answer ONLY using the context below.

Rules:
1. Do NOT use outside knowledge.
2. If the answer is not present, reply exactly:
'I couldn't find that information in the uploaded document.'
3. Keep answers short and factual.

Previous Conversation:
{history_text}

Context:
{context}

Question:
{question}
"""

    logger.info(f"[DOC-CHAT] Sending prompt to Gemini (Size: {len(prompt)} characters)...")
    try:
        answer = await generate_text(prompt)
        logger.info(f"[DOC-CHAT] Gemini Response: {answer[:150]}...")
    except Exception as e:
        logger.error(f"[DOC-CHAT] Gemini call failed: {e}")
        return {
            "answer": "Error: Gemini API failed.",
            "sources": []
        }

    try:
        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)
    except Exception as e:
        logger.warning(f"[DOC-CHAT] Failed to save messages to history: {e}")

    unique_sources = list(set([m.get("filename") for m in metadata if m.get("filename")]))

    return {
        "answer": answer,
        "sources": unique_sources
    }
