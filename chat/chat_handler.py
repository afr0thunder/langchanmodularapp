# chat/chat_handler.py

from datetime import datetime
import sqlite3
import uuid
import os

class ChatHandler:
    def __init__(self, agent, db_path="chat_history.db"):
        self.agent = agent
        self.history = []  # In-memory cache
        self.db_path = db_path
        self.agent_id = agent.name  # Assumes each agent has a unique name
        self._init_db()
        self._load_history_from_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True) if os.path.dirname(self.db_path) else None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT
                )
            ''')
            conn.commit()

    def _load_history_from_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, role, content, timestamp FROM messages WHERE agent_id = ? ORDER BY timestamp ASC", (self.agent_id,))
            rows = cursor.fetchall()
            for msg_id, role, content, timestamp in rows:
                self.history.append({
                    "id": msg_id,
                    "role": role,
                    "content": content,
                    "timestamp": timestamp
                })

    def _save_message_to_db(self, role, content, timestamp):
        msg_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (id, agent_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (msg_id, self.agent_id, role, content, timestamp))
            conn.commit()
        return msg_id

    def send_message(self, user_input):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = self._save_message_to_db("user", user_input, timestamp)
        context = self._build_context()
        response = self.agent.respond(user_input, context=context)
        agent_id = self._save_message_to_db("agent", response, timestamp)

        self.history.append({"id": user_id, "role": "user", "content": user_input, "timestamp": timestamp})
        self.history.append({"id": agent_id, "role": "agent", "content": response, "timestamp": timestamp})

        return response

    def _build_context(self, window=3):
        context_window = self.history[-2*window:] if window else self.history
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in context_window])

    def get_history(self):
        return self.history

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE agent_id = ?", (self.agent_id,))
            conn.commit()
        self.history = []