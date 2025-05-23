from fastapi import FastAPI
from pydantic import BaseModel
from services.process_data import extract_info
from services.intent_fulfill import fulfill_intent
from core.sessions import get_or_create_session
from humanizer import humanize_reply
from fastapi.middleware.cors import CORSMiddleware
from sqlite import log_interaction, create_chat_logs_table

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str  
    session_id: str

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    print('request is', request)
    await create_chat_logs_table()
    sessionId = get_or_create_session(request.user_id)

    # # Store user message
    # append_to_history(request.user_id, "user", request.message)

    # Rishabh ************************** Detect Intent & Parameters to further process the intent
    msg_extracted_info = extract_info(request.message)
    print('msg_extracted_info', msg_extracted_info)
    # Praveen ************************** Fulfill the intent
    raw_reply = fulfill_intent(msg_extracted_info)
    print('raw_reply', raw_reply)
    # Puneet ************************** Humanize the reply
    reply = await humanize_reply(raw_reply)
    print('reply', reply)

    # Logging to sqlite start
    was_successful = not any(keyword in reply.lower() for keyword in [
        "couldn't find", "not able", "invalid", "unknown", "error", "try again"
    ])

    await log_interaction(
        user_id=request.user_id,
        session_id=sessionId,
        user_message=request.message,
        detected_intent=msg_extracted_info.get("intent"),
        response_sent=reply,
        was_successful=was_successful
    )
    # Logging to sqlite end

    # Store bot response
    # append_to_history(request.user_id, "assistant", reply)

    return {
        "sessionId": sessionId,
        "reply": reply,
        "intent": msg_extracted_info.get("intent")
    }
