from fastapi import FastAPI
from pydantic import BaseModel
from services.intent import detect_intent
from services.process_data import extract_info
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

    # Rishabh ************************** Detect Intent & Parameters to further process the intent
    analysis_result = await extract_info(request.message)
    print(f"Detected Intent: {analysis_result['intent']}")
    print(f"Extracted Entities: {analysis_result['entities']}")
    print(f"Missing Entities: {analysis_result['missing']}")

    # Praveen ************************** Fulfill the intent
    reply = await fulfill_intent(analysis_result['intent'],analysis_result['entities'], analysis_result['missing'],request.message, request.phone_no, session)

    # Puneet ************************** Humanize the reply
    reply = humanize_reply(reply)

    # Store bot response
    append_to_history(request.user_id, "assistant", reply)

    return {
        "reply": reply,
        "intent": intent,
        "history": session["history"]
    }
