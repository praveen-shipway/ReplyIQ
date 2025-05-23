# Sample dummy data for simulation
dummy_orders = {
    "ord1": {"status": "processing", "can_cancel": True},
    "ord2": {"status": "shipped", "can_cancel": False}
}

dummy_tracking = {
    "awb1": {"status": "Out for delivery"},
    "awb2": {"status": "Delivered"}
}

dummy_faqs = {
    "shipping policy": "Standard shipping takes 3–5 business days.",
    "cancel order": "You can cancel an order before it is shipped by providing the order ID."
}

def order_cancel(entities):
    order_id = entities.get("ORDER_ID")
    if not order_id:
        return "Missing order_id for cancellation."

    order = dummy_orders.get(order_id)
    if not order:
        return f"No order found with ID #{order_id}."

    if order["can_cancel"]:
        return f"Order #{order_id} has been successfully canceled."
    else:
        return f"Order #{order_id} has already shipped and cannot be canceled."

def wismo(entities):
    order_id = entities.get("ORDER_ID")
    awb = entities.get("TRACKING_NUMBER")

    if not order_id and not awb:
        return "Please provide either order ID or AWB to track your order."

    tracking_info = dummy_tracking.get(order_id or awb)
    if tracking_info:
        return f"Tracking info: {tracking_info['status']}"
    else:
        return "No tracking information found for the given ID."

def faq(entities):
    question = entities.get("question", "").lower()
    if not question:
        return "Please provide a question for FAQ lookup."

    for key, answer in dummy_faqs.items():
        if key in question:
            return answer

    return "Sorry, I couldn't find an answer to that question."

def fulfill_intent(msg_extracted_info):
    intent = msg_extracted_info.get("intent")
    entities = msg_extracted_info.get("entities", {})
    missing = msg_extracted_info.get("missing", [])

    if missing:
        return f"Missing required information: {', '.join(missing)}"
    intent_upper = intent.upper()
    if intent_upper == "CANCEL":
        return order_cancel(entities)
    elif intent_upper == "WISMO":
        return wismo(entities)
    elif intent_upper == "FAQ":
        return faq(entities)
    else:
        return "Unknown intent. Please try again."

# # Example test
# if __name__ == "__main__":
#     test_cases = [
#         {"intent": "Order Cancelation", "entities": {"order_id": "12345"}, "missing": []},
#         {"intent": "Order Cancelation", "entities": {"order_id": "54321"}, "missing": []},
#         {"intent": "WISMO", "entities": {"order_id": "12345"}, "missing": []},
#         {"intent": "WISMO", "entities": {"awb": "AWB123"}, "missing": []},
#         {"intent": "FAQ", "entities": {"question": "What is your shipping policy?"}, "missing": []},
#         {"intent": "FAQ", "entities": {"question": "How do I cancel an order?"}, "missing": []}
#     ]

#     for case in test_cases:
#         print(f">>> Input: {case}")
#         print(fulfill_intent(case))
#         print("-" * 50)
