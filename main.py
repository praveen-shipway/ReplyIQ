from fastapi import FastAPI
from pydantic import BaseModel
from services.intent import detect_intent
from services.intent_dispatcher import fulfill_intent
from core.sessions import get_session, update_session, append_to_history
from AI_API import humanize_reply

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    phone_no : str

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    session = get_session(request.user_id)

    # Store user message
    append_to_history(request.user_id, "user", request.message)

    # Rishabh **************************
    intent = await detect_intent(request.message)

    # Praveen **************************
    reply = await fulfill_intent(intent, request.message, request.phone_no, session)

    # Puneet
    reply = humanize_reply(reply)

    # Store bot response
    append_to_history(request.user_id, "assistant", reply)

    return {
        "reply": reply,
        "intent": intent,
        "history": session["history"]
    }
