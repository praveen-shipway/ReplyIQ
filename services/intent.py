import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def detect_intent(message: str) -> str:
    system_prompt = (
        "You are an intent detection system for an e-commerce chatbot. "
        "Possible intents: wismo, cancel, reschedule, faq, general, unknown, "
        "Based on the user message, return only the correct intent label."
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0
                }
            )
            intent = response.json()['choices'][0]['message']['content'].strip().lower()
            return intent
    except Exception as e:
        print("Intent detection error:", e)
        return "unknown"
