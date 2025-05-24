from sqlite import get_session_history
import aiohttp

# Sample dummy data for simulation (ORDER_ID or AWB can be used)
dummy_orders = {
    "ord1": {"status": "processing", "can_cancel": True, "awb": "awb1"},
    "ord2": {"status": "shipped", "can_cancel": False, "awb": "awb2"}
}

dummy_tracking = {
    "ord1": {"status": "Out for delivery"},
    "ord2": {"status": "Delivered"},
    "awb1": {"status": "Out for delivery"},
    "awb2": {"status": "Delivered"}
}

dummy_faqs = {
    "shipping policy": "Standard shipping takes 3–5 business days.",
    "cancel order": "You can cancel an order before it is shipped by providing the order ID or AWB.",
    "return policy": "Items can be returned within 30 days of delivery. Please ensure they are unused and in original packaging.",
    "payment methods": "We accept Visa, MasterCard, UPI, Netbanking, and Cash on Delivery.",
    "track my order": "To track your order, please provide your Order ID or AWB number.",
    "customer support": "You can contact our support team 24/7 via email at support@example.com or call 1800-123-456.",
    "change address": "You can change the delivery address before the item is shipped. Please provide your order ID to proceed.",
    "invoice request": "Invoices are sent to your registered email after the order is shipped. You can also request a copy from support."
}

def order_cancel(entities):
    order_id = entities.get("ORDER_ID")
    awb = entities.get("TRACKING_NUMBER")

    if not order_id and not awb:
        return "Missing order_id or awb for cancellation."

    # Try to find by order_id or by matching AWB
    order = None
    if order_id:
        order = dummy_orders.get(order_id)
    elif awb:
        order = next((o for o in dummy_orders.values() if o.get("awb") == awb), None)

    if not order:
        return f"No order found for given ID or AWB."

    if order["can_cancel"]:
        return f"Order has been successfully canceled."
    else:
        return f"Order has already shipped and cannot be canceled."

def wismo(entities):
    order_id = entities.get("ORDER_ID")
    awb = entities.get("TRACKING_NUMBER")

    if not order_id and not awb:
        return "Please provide either order ID or AWB to track your order."

    tracking_info = dummy_tracking.get(order_id or awb)
    if tracking_info:
        return f"Tracking info: {tracking_info['status']}"
    else:
        return "No tracking information found for the given ID or AWB."

def faq(entities):
    question = entities.get("question", "").lower()
    if not question:
        return "Please provide a question for FAQ lookup."

    for key, answer in dummy_faqs.items():
        if key in question:
            return answer

    return "Sorry, I couldn't find an answer to that question."


async def fulfill_intent(msg_extracted_info, user_id, session_id, user_message):
    intent = msg_extracted_info.get("intent", "").lower()
    entities = msg_extracted_info.get("entities", {})

    # Step 1: Load last N messages from session
    history = await get_session_history(session_id, limit=5)
    print('history', history)
    print('intent', intent)

    # Step 2: Try to recover intent from last message if this one is unknown
    if intent == "unknown" and history:
        last_user_msg, last_bot_reply = history[-1]
        
        # Send only last interaction + current to Groq for intent suggestion
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a backend logic assistant. Given the previous chat and current user message, "
                    "determine if the new message is part of the previous intent. "
                    "Reply only with the intent label (e.g., cancel, wismo, faq) or 'unknown'."
                )
            },
            {"role": "user", "content": f"Previous user message: {last_user_msg}\nBot reply: {last_bot_reply}"},
            {"role": "user", "content": f"Current user message: {user_message}"}
        ]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": "Bearer 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",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                        "messages": messages,
                        "temperature": 0.0
                    }
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    recovered_intent = data['choices'][0]['message']['content'].strip().lower()
                    print('recovered_intent', recovered_intent)
                    # Use recovered intent if not unknown
                    if recovered_intent in ["cancel", "wismo", "faq", "reschedule"]:
                        intent = recovered_intent

        except Exception as e:
            print("Intent recovery failed:", e)

    # Step 3: Generate basic fallback
    basic_reply = None
    if intent in ["cancel", "wismo", "reschedule"]:
        if len(entities) == 0:
            basic_reply = "Missing required information order_id or awb"
        else:
            if intent == "cancel":
                basic_reply = order_cancel(entities)
            elif intent == "wismo":
                basic_reply = wismo(entities)
    elif intent == "faq":
        basic_reply = faq(entities)
    else:
        basic_reply = "Unknown intent. Please try again."

    # Step 4: Add chat history to system prompt for LLM
    messages = [{
        "role": "system",
        "content": "You are a backend system generating helpful, structured responses based on customer support intents and previous chat history. Be precise and data-driven, without friendly human phrasing."
    }]
    for past_user, past_bot in history:
        messages.append({"role": "user", "content": past_user})
        messages.append({"role": "assistant", "content": past_bot})
    messages.append({"role": "user", "content": f"User message: {user_message}\nDetected intent: {intent}\nEntities: {entities}"})

    # Step 5: Generate enhanced response
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": messages,
                    "temperature": 0.3
                }
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                improved_reply = data['choices'][0]['message']['content'].strip()
                return improved_reply

    except Exception as e:
        print(f"LLM fallback used due to error: {e}")
        return basic_reply
