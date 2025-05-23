import requests

def humanize_reply(processed_reply, user_message=None, intent=None):
    """
    Use AI API to convert system-generated reply into a human-friendly message.
    """

    system_prompt = (
        "You are a helpful, empathetic customer support assistant for an e-commerce company. "
        "Given a plain system-generated response, rewrite it to sound more human, friendly, and brand-aligned. "
        "Keep the meaning the same, but improve tone and naturalness. "
        "Avoid sounding robotic. Use simple, clear, polite language."
    )

    user_prompt = f"System reply: {processed_reply}"
    if intent:
        user_prompt += f"\nIntent: {intent}"
    if user_message:
        user_prompt += f"\nUser's original message: {user_message}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": messages,
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    return data['choices'][0]['message']['content'].strip()