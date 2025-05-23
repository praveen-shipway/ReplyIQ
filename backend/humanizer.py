import httpx
import random

async def humanize_reply(processed_reply):
    """
    Use AI API to convert system-generated reply into a WhatsApp-style message:
    - Short and to the point.
    - Friendly and casual tone.
    - Add relevant emojis.
    - Never repeat the exact same phrasing unless absolutely required.
    """

    system_prompt = (
        "You are a cool, helpful WhatsApp-style customer support bot. "
        "Take a system-generated message and convert it into a short, friendly, emoji-filled message. "
        "Keep it casual and human — like how you'd text a friend. "
        "Avoid robotic tone. Always make the message slightly different on each request, unless the message is already perfect. "
        "Use emojis where appropriate to express emotions or actions. "
        "Length: 1–2 short sentences max."
    )

    # Add slight randomness to user prompt for variability
    personality_variants = [
        "Make it sound breezy and cool.",
        "Make it a bit witty and warm.",
        "Be polite and cheerful.",
        "Sound calm and confident.",
        "Use casual chat style.",
    ]
    variant_prompt = random.choice(personality_variants)

    user_prompt = f"{variant_prompt}\nSystem reply: {processed_reply}"

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
        "temperature": 0.85,  # Higher temperature for more creativity
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data['choices'][0]['message']['content'].strip()
