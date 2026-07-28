import uuid
import urllib.parse
import traceback

from utils.document_loader import load_document
from utils.text_splitter import split_text
from services.embedding_service import create_embeddings
from services.vector_db import collection
from llm.router import generate_text
from config.logger import logger


async def upload_document(file_path: str, file_name: str, organization_id: str = "default"):
    logger.info(f"[RAG-UPLOAD] Start indexing process for file: {file_name} (Org: {organization_id})")
    
    try:
        text = load_document(file_path)
    except Exception as e:
        logger.error(f"[RAG-UPLOAD] Text extraction failed: {e}")
        raise Exception(f"OCR/Extraction failed: {str(e)}")

    logger.info(f"[RAG-UPLOAD] Extraction complete. Total character length: {len(text)}")
    if not text.strip():
        raise Exception("No readable text found in document.")

    try:
        chunks = split_text(text)
    except Exception as e:
        logger.error(f"[RAG-UPLOAD] Text splitting failed: {e}")
        raise Exception(f"Chunking failed: {str(e)}")

    logger.info(f"[RAG-UPLOAD] Text split into {len(chunks)} chunks.")
    if len(chunks) == 0:
        raise Exception("No chunks generated.")

    MAX_CHUNKS = 200
    if len(chunks) > MAX_CHUNKS:
        logger.warning(f"[RAG-UPLOAD] Document chunks ({len(chunks)}) exceed limit. Truncating to {MAX_CHUNKS}.")
        chunks = chunks[:MAX_CHUNKS]

    # Pre-upload clean: delete previous vectors for this exact filename and organization
    try:
        logger.info(f"[RAG-UPLOAD] Deleting previous vectors for {file_name} (Org: {organization_id}) to prevent duplicates...")
        collection.delete(
            where={
                "$and": [
                    {"filename": file_name},
                    {"organization_id": str(organization_id)}
                ]
            }
        )
    except Exception as e:
        logger.warning(f"[RAG-UPLOAD] Clean phase warning: {e}")

    logger.info("[RAG-UPLOAD] Generating embeddings...")
    try:
        embeddings = create_embeddings(chunks)
    except Exception as e:
        logger.error(f"[RAG-UPLOAD] Embeddings generation failed: {e}")
        raise Exception(f"Embedding generation failed: {str(e)}")

    logger.info(f"[RAG-UPLOAD] Storing {len(chunks)} vectors in ChromaDB...")
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = []

    for i in range(len(chunks)):
        metadatas.append({
            "filename": file_name,
            "organization_id": str(organization_id),
            "chunk": i
        })

    try:
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"[RAG-UPLOAD] Successfully indexed {file_name} in ChromaDB (Collection count: {collection.count()})")
    except Exception as e:
        logger.error(f"[RAG-UPLOAD] ChromaDB insertion failed: {e}")
        raise Exception(f"ChromaDB storage failed: {str(e)}")

    return {
        "status": "success",
        "document": file_name,
        "chunks": len(chunks),
        "text": text
    }


async def ask_document(filename: str, question: str, organization_id: str = "default"):
    # URL-decode filename to prevent URL encoding mismatches
    filename = urllib.parse.unquote(filename)
    logger.info(f"[RAG-QUERY] New question for '{filename}' (Org: {organization_id}): '{question}'")

    try:
        logger.info("[RAG-QUERY] Generating embedding for the query...")
        question_embeddings = create_embeddings([question])
        if not question_embeddings:
            raise Exception("No embedding generated for query.")
        question_embedding = question_embeddings[0]
    except Exception as e:
        logger.error(f"[RAG-QUERY] Embedding generation failed: {e}")
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

    logger.info(f"[RAG-QUERY] Querying ChromaDB with filter: {where_filter}")
    results = None
    try:
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=5,
            where=where_filter
        )
    except Exception as e:
        logger.error(f"[RAG-QUERY] ChromaDB query failed: {e}\n{traceback.format_exc()}")
        return {
            "answer": "Error: ChromaDB unavailable.",
            "sources": []
        }

    # Verify if search returned relevant documents
    if not results or not results.get("documents") or not results["documents"][0]:
        logger.warning("[RAG-QUERY] No chunks returned. Running diagnostics...")
        # Check why retrieval failed
        try:
            # 1. Check if organization has any vectors stored
            org_count_res = collection.get(where={"organization_id": str(organization_id)}, limit=1)
            if not org_count_res or not org_count_res.get("ids"):
                logger.info("[RAG-QUERY] Diagnostic: No vectors found for this organization.")
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
                    logger.info(f"[RAG-QUERY] Diagnostic: Document '{filename}' is not indexed.")
                    return {
                        "answer": "Error: Document not indexed.",
                        "sources": []
                    }

            logger.info("[RAG-QUERY] Diagnostic: Document exists but metadata filter/similarity query returned empty.")
            return {
                "answer": "Error: Metadata filter returned zero matches.",
                "sources": []
            }
        except Exception as diag_err:
            logger.error(f"[RAG-QUERY] Diagnostic failed: {diag_err}")
            return {
                "answer": "Error: Metadata filter returned zero matches.",
                "sources": []
            }

    documents = results["documents"][0]
    metadata = results["metadatas"][0]
    distances = results.get("distances", [[]])[0]

    logger.info(f"[RAG-QUERY] Retrieved {len(documents)} chunks. Distances: {distances}")
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
        logger.info("[RAG-QUERY] Detected summary request. Formulating structured prompt...")
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

Context:
{context}

Question:
{question}
"""
    else:
        prompt = f"""You are NEXOVVA AI.

You must answer ONLY using the supplied context.

Rules:
1. Do NOT use outside knowledge.
2. If the answer is not present, reply exactly:
'I couldn't find that information in the uploaded document.'
3. Keep answers short and factual.

Context:
{context}

Question:
{question}
"""

    logger.info(f"[RAG-QUERY] Sending prompt to Gemini (Size: {len(prompt)} characters)...")
    try:
        answer = await generate_text(prompt)
        logger.info(f"[RAG-QUERY] Gemini Response: {answer[:150]}...")
    except Exception as e:
        logger.error(f"[RAG-QUERY] Gemini call failed: {e}")
        return {
            "answer": "Error: Gemini API failed.",
            "sources": []
        }

    # Extract unique sources
    unique_sources = list(set([m.get("filename") for m in metadata if m.get("filename")]))

    return {
        "answer": answer,
        "sources": unique_sources
    }
