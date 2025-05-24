import aiosqlite
from datetime import datetime

async def log_interaction(
    user_id,
    session_id,
    user_message,
    detected_intent,
    response_sent,
    was_successful=None,
    user_feedback=None,
    timestamp=None
):
    if timestamp is None:
        timestamp = datetime.now().timestamp()


    async with aiosqlite.connect("/home/puneet/Downloads/ReplyIQ/backend/mydatabase.db") as db:
        await db.execute(
            """
            INSERT INTO chat_logs (
                user_id, session_id, timestamp, user_message, 
                detected_intent, response_sent, was_successful, user_feedback
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session_id,
                timestamp,
                user_message,
                detected_intent,
                response_sent,
                was_successful,
                user_feedback
            )
        )
        await db.commit()

async def get_session_history(session_id, limit=6):
    async with aiosqlite.connect("mydatabase.db") as db:
        async with db.execute("""
            SELECT user_message, response_sent FROM chat_logs
            WHERE session_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (session_id, limit)) as cursor:
            return await cursor.fetchall()
        
async def create_chat_logs_table():
    async with aiosqlite.connect("/home/puneet/Downloads/ReplyIQ/backend/mydatabase.db") as db:  # Update this line
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                detected_intent TEXT,
                response_sent TEXT,
                was_successful BOOLEAN,
                user_feedback TEXT
            )
            """
        )
        await db.commit()


async def get_session_history(session_id: str, limit: int = 5):
    """
    Returns a list of (user_message, bot_response) pairs from the session history.
    """
    async with aiosqlite.connect("/home/puneet/Downloads/ReplyIQ/backend/mydatabase.db") as db:
        cursor = await db.execute(
            "SELECT user_message, response_sent FROM chat_logs WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = await cursor.fetchall()
        await cursor.close()
    return rows[::-1]  # reverse to chronological order

