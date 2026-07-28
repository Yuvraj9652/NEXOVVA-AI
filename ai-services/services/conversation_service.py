from collections import defaultdict

# Shared in-memory storage for chat sessions
conversation_store = defaultdict(list)


def get_history(session_id: str):
    return conversation_store[session_id]


def add_message(session_id: str, role: str, message: str):
    conversation_store[session_id].append({
        "role": role,
        "content": message
    })

    # Keep only the last 10 messages
    conversation_store[session_id] = conversation_store[session_id][-10:]


def get_conversation_history(session_id: str):
    return conversation_store[session_id]


def save_message(session_id: str, role: str, content: str):
    conversation_store[session_id].append(
        {
            "role": role,
            "content": content,
        }
    )


def clear_conversation(session_id: str):
    conversation_store.pop(session_id, None)