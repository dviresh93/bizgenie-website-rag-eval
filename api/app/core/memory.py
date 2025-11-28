import sqlite3
import json
import os
from typing import List, Dict
from datetime import datetime

class ChatMemory:
    """
    Simple SQLite-based chat memory.
    Stores messages by session_id.
    """

    def __init__(self, db_path: str = "api/app/data/chat_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database table"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get recent chat history for a session.
        Returns list of {"role": ..., "content": ...}
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get last N messages ordered by time
        cursor.execute(
            """
            SELECT role, content 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (session_id, limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        # Reverse to return in chronological order (oldest -> newest)
        history = [{"role": row["role"], "content": row["content"]} for row in rows]
        return history[::-1]

    def clear_session(self, session_id: str):
        """Clear history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
