# db_manager/db.py
import sqlite3
import os

    
class Database:
    def __init__(self, path_to_database='database/database.db'):
        # Создаём директорию, если её нет
        os.makedirs(os.path.dirname(path_to_database), exist_ok=True)
        
        self.connection = sqlite3.connect(path_to_database)
        self.cursor = self.connection.cursor()

        with self.connection:
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id TEXT)''')

        with self.connection:
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    description TEXT,
                    status BOOL
                )''')

        # ⚡ Новая таблица для администраторов
        with self.connection:
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    alias TEXT
                )'''
            )

    # --- USERS ---
    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchmany(1)
        return bool(len(result))

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    def get_all_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT user_id FROM users").fetchall()
        return [row[0] for row in result]
        
    # --- FEEDBACK ---
    def add_feedback(self, user_id, description, status=0):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO feedback (user_id, description, status) VALUES (?, ?, ?)",
                (user_id, description, status)
            )
    
    def count_feedback_with_status_zero(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT COUNT(*) FROM feedback WHERE status = 0"
            ).fetchone()
        return result[0] if result else 0
        
    def get_open_feedbacks(self):
        """
        Возвращает список кортежей (id, user_id, description) для всех записей со status = 0
        """
        with self.connection:
            rows = self.cursor.execute(
                "SELECT id, user_id, description FROM feedback WHERE status = 0"
            ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]
        
    def get_feedback_status(self, feedback_id):
        with self.connection:
            row = self.cursor.execute("SELECT status FROM feedback WHERE id = ?", (feedback_id,)).fetchone()
        return row[0] if row else None

    def set_feedback_status(self, feedback_id, status):
        with self.connection:
            self.cursor.execute("UPDATE feedback SET status = ? WHERE id = ?", (status, feedback_id))
            self.connection.commit()

    def get_feedback_user_id(self, feedback_id):
        with self.connection:
            row = self.cursor.execute("SELECT user_id FROM feedback WHERE id = ?", (feedback_id,)).fetchone()
        return row[0] if row else None 
        
    def get_all_feedbacks(self):
        with self.connection:
            rows = self.cursor.execute("SELECT id, user_id, description, status FROM feedback").fetchall()
            return [(r[0], r[1], r[2], r[3]) for r in rows]

    def delete_feedback(self, feedback_id):
        with self.connection:
            self.cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))

    # --- ADMIN METHODS ---
    def add_admin(self, user_id, alias=None):
        """Добавляет администратора."""
        with self.connection:
            self.cursor.execute(
                "INSERT OR IGNORE INTO admins (user_id, alias) VALUES (?, ?)",
                (user_id, alias)
            )
            self.connection.commit()

    def get_all_admins(self):
        with self.connection:
            rows = self.cursor.execute("SELECT user_id, alias FROM admins").fetchall()
        return [(r[0], r[1]) for r in rows]

    def delete_admin(self, user_id):
        with self.connection:
            self.cursor.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            self.connection.commit()

    def admin_exists(self, user_id):
        with self.connection:
            row = self.cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)).fetchone()
        return bool(row)

    def count_admins(self):
        with self.connection:
            result = self.cursor.execute("SELECT COUNT(*) FROM admins").fetchone()
        return result[0] if result else 0
    
    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        self.cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None