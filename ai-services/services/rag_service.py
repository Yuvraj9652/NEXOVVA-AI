import uuid

from utils.pdf_loader import load_pdf
from utils.text_splitter import split_text
from services.embedding_service import create_embeddings
from services.vector_db import collection
from llm.router import generate_text


async def upload_document(file_path: str, file_name: str):

    text = load_pdf(file_path)

    if not text.strip():
        raise Exception("No readable text found.")

    chunks = split_text(text)

    if len(chunks) == 0:
        raise Exception("No chunks generated.")

    MAX_CHUNKS = 200
    chunks = chunks[:MAX_CHUNKS]

    embeddings = create_embeddings(chunks)

    ids = [str(uuid.uuid4()) for _ in chunks]

    metadatas = []

    for i in range(len(chunks)):
        metadatas.append({
            "filename": file_name,
            "chunk": i
        })

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "document": file_name,
        "chunks": len(chunks)
    }


async def ask_document(filename: str, question: str):

    question_embedding = create_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5,
        where={"filename": filename}
    )

    if not results["documents"] or not results["documents"][0]:
        return {
            "answer": f"No information found for '{filename}'.",
            "sources": []
        }

    documents = results["documents"][0]
    metadata = results["metadatas"][0]

    context = "\n\n".join(documents)

    prompt = f"""
You are NEXOVVA AI.

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

    answer = await generate_text(prompt)

    return {
        "answer": answer,
        "sources": metadata
    }