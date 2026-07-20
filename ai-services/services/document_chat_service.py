from services.embedding_service import create_embeddings
from services.vector_db import collection
from services.conversation_service import (
    get_conversation_history,
    save_message,
)
from llm.router import generate_text


async def chat_with_document(session_id: str, filename: str, question: str):

    history = get_conversation_history(session_id)

    history_text = ""

    for msg in history:
        history_text += f"{msg['role']}: {msg['content']}\n"

    question_embedding = create_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5,
        where={"filename": filename}
    )

    if not results["documents"] or not results["documents"][0]:
        return {
            "answer": f"No information found in '{filename}'.",
            "sources": []
        }

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
You are NEXOVVA AI.

Answer ONLY using the context below.

Previous Conversation:
{history_text}

Context:
{context}

Question:
{question}
"""

    answer = await generate_text(prompt)

    save_message(session_id, "user", question)
    save_message(session_id, "assistant", answer)

    return {
        "answer": answer,
        "sources": results["metadatas"][0]
    }