import sqlite3
from typing import List, Dict, Tuple
import os

DB_PATH = "modular_chat_app.db"

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                name TEXT PRIMARY KEY,
                base_prompt TEXT,
                llm_choice TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                user_msg TEXT,
                agent_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                subject TEXT,
                questions TEXT,
                answers TEXT,
                score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    # Agent methods
    def save_agent(self, name: str, base_prompt: str, llm_choice: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'REPLACE INTO agents (name, base_prompt, llm_choice) VALUES (?, ?, ?)',
            (name, base_prompt, llm_choice)
        )
        self.conn.commit()

    def load_agent(self, name: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM agents WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return {"name": row[0], "base_prompt": row[1], "llm_choice": row[2]}
        else:
            raise ValueError(f"Agent '{name}' not found.")

    def list_agents(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM agents')
        return [row[0] for row in cursor.fetchall()]

    def delete_agent(self, name: str):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM agents WHERE name = ?', (name,))
        self.conn.commit()

    # Chat methods
    def save_chat(self, agent_name: str, user_msg: str, agent_response: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO chats (agent_name, user_msg, agent_response) VALUES (?, ?, ?)',
            (agent_name, user_msg, agent_response)
        )
        self.conn.commit()

    def load_chat_history(self, agent_name: str) -> List[Tuple[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT user_msg, agent_response FROM chats WHERE agent_name = ? ORDER BY timestamp ASC',
            (agent_name,)
        )
        return cursor.fetchall()

    # Test methods
    def save_test_result(self, agent_name: str, subject: str, questions: str, answers: str, score: float):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO tests (agent_name, subject, questions, answers, score) VALUES (?, ?, ?, ?, ?)',
            (agent_name, subject, questions, answers, score)
        )
        self.conn.commit()

    def update_agent_prompt(self, name: str, new_prompt: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE agents SET base_prompt = ? WHERE name = ?',
            (new_prompt, name)
        )
        self.conn.commit()
