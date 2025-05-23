from typing import Dict, List

_sessions: Dict[str, Dict] = {}

def get_session(user_id: str) -> Dict:
    """Initialize or return existing session"""
    if user_id not in _sessions:
        _sessions[user_id] = {
            "history": [],
            "order_context": None,
            "pending_info": None
        }
    return _sessions[user_id]

def update_session(user_id: str, key: str, value):
    if user_id in _sessions:
        _sessions[user_id][key] = value

def append_to_history(user_id: str, role: str, content: str):
    if user_id in _sessions:
        _sessions[user_id]["history"].append({
            "role": role,
            "content": content
        })

def clear_session(user_id: str):
    if user_id in _sessions:
        del _sessions[user_id]
