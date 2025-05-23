from fastapi import FastAPI
from pydantic import BaseModel
from services.process_data import extract_info
from services.intent_fulfill import fulfill_intent
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
    msg_extracted_info = await extract_info(request.message)

    # Praveen ************************** Fulfill the intent
    raw_reply = await fulfill_intent(msg_extracted_info)

    # Puneet ************************** Humanize the reply
    reply = await humanize_reply(raw_reply)

    # Store bot response
    # append_to_history(request.user_id, "assistant", reply)

    return {
        "reply": reply
    }
