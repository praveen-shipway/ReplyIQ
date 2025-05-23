async def fulfill_intent(intent: str,entities: dict, missing, message: str,phone_no:str, session: dict):
    if intent == 'wismo':
        return await handle_wismo(session,entities,missing)
    elif intent == 'reschedule':
        return await handle_reschedule(message, session,entities,missing)
    elif intent == 'cancel':
        return await handle_cancel(message, session,entities,missing)
    elif intent == 'faq':
        return await handle_faq(message,entities,missing)
    else:
        return await handle_general(message, session,entities,missing)

async def handle_wismo(session,phone_no):
    order = session.get('order_context')
    if not order:
        return "I don’t have your order details yet. Please provide your Order ID or Tracking Number."
    return f"Your order {order['order_id']} is currently {order['status']}."

async def handle_reschedule(message, session):
    # Parse new date from message (you can use NLP here)
    # Check current delivery date from order_context
    # Validate new date > old date
    # Update DB if valid
    # Return confirmation or error message
    return "Reschedule feature is under construction."

async def handle_cancel(message, session):
    # Similar: validate and update DB for cancellation
    return "Cancel feature is under construction."

async def handle_faq(message):
    # Can call an FAQ system or AI here
    return "Here's a helpful answer to your question."

async def handle_general(message, session):
    # Use AI to generate general responses
    return "Let me check on that for you."
