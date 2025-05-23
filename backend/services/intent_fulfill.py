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

def fulfill_intent(msg_extracted_info):
    intent = msg_extracted_info.get("intent", "").lower()
    entities = msg_extracted_info.get("entities", {})

    if intent in ["cancel", "wismo", "reschedule"]:
        if len(entities) == 0:
            return f"Missing required information order_id or awb"
        else:
            if intent == "cancel":
                return order_cancel(entities)
            elif intent == "wismo":
                return wismo(entities)
            # elif intent == "reschedule":
            #     return reschedule(entities)
    else:
        if intent == "faq":
            return faq(entities)
        else:
            return "Unknown intent. Please try again."

# Example test
# if __name__ == "__main__":
#     test_cases = [
#         {"intent": "Order Cancelation", "entities": {"order_id": "ord1"}, "missing": []},
#         {"intent": "Order Cancelation", "entities": {"awb": "awb2"}, "missing": []},
#         {"intent": "WISMO", "entities": {"order_id": "ord2"}, "missing": []},
#         {"intent": "WISMO", "entities": {"awb": "awb1"}, "missing": []},
#         {"intent": "FAQ", "entities": {"question": "What is your shipping policy?"}, "missing": []},
#         {"intent": "FAQ", "entities": {"question": "How do I cancel an order?"}, "missing": []},
#         {"intent": "Order Cancelation", "entities": {}, "missing": ["order_id or awb"]}
#     ]

#     for case in test_cases:
#         print(f">>> Input: {case}")
#         print(fulfill_intent(case))
#         print("-" * 50)
