from fastapi import FastAPI
from pydantic import BaseModel
from services.process_data import extract_info
from services.intent_fulfill import fulfill_intent
from core.sessions import get_session, update_session, append_to_history
from humanizer import humanize_reply
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/chat")
async def chat_handler(request: ChatRequest):
    # session = get_session(request.user_id)

    # # Store user message
    # append_to_history(request.user_id, "user", request.message)

    # Rishabh ************************** Detect Intent & Parameters to further process the intent
    print('request is', request)
    msg_extracted_info = extract_info(request.message)
    print('msg_extracted_info', msg_extracted_info)
    # Praveen ************************** Fulfill the intent
    raw_reply = fulfill_intent(msg_extracted_info)
    print('raw_reply', raw_reply)
    # Puneet ************************** Humanize the reply
    reply = await humanize_reply(raw_reply)
    print('reply', reply)
    # Store bot response
    # append_to_history(request.user_id, "assistant", reply)

    return {
        "reply": reply
    }
