import uuid

def get_or_create_session(session_id=None):
    return session_id or str(uuid.uuid4())
