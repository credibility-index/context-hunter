import json
import random
import sqlite3
import os

class CurlyMemeGame:
    def __init__(self):
        self.db_path = 'users.db'
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users 
                           (user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0, 
                            level TEXT DEFAULT 'A2', found_words TEXT DEFAULT '[]')''')
        self.conn.commit()
        
        with open('data.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_text(self, level: str) -> dict:
        texts = self.data.get(level, self.data['A2'])['texts']
        return random.choice(texts)
    
    def update_score(self, user_id: int, points: int):
        self.conn.execute("UPDATE users SET score = score + ? WHERE user_id = ?", (points, user_id))
        self.conn.commit()
    
    def get_score(self, user_id: int) -> int:
        result = self.conn.execute("SELECT score FROM users WHERE user_id=?", (user_id,)).fetchone()
        return result[0] if result else 0
