from fastapi import FastAPI
from pydantic import BaseModel
from services.intent import detect_intent
from services.intent_dispatcher import fulfill_intent
from core.sessions import get_session, update_session, append_to_history
from humanizer import humanize_reply

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    phone_no : str

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    # session = get_session(request.user_id)

    # # Store user message
    # append_to_history(request.user_id, "user", request.message)

    # Rishabh ************************** Detect Intent & Parameters to further process the intent
    intent = await detect_intent(request.message)

    # Praveen ************************** Fulfill the intent
    raw_reply = await fulfill_intent(intent, request.message, request.phone_no)

    # Puneet ************************** Humanize the reply
    reply = humanize_reply(raw_reply)

    # Store bot response
    # append_to_history(request.user_id, "assistant", reply)

    return {
        "reply": reply
    }
