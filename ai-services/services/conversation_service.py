from collections import defaultdict

# Temporary in-memory storage
# Later this will be replaced by Redis or a database
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