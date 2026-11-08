import sqlite3
import os

# Определяем путь к базе данных (на уровень выше папки src, в папку data)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'notes.db')

def get_connection():
    """Вспомогательная функция для подключения к БД."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Инициализация базы данных и создание таблицы заметок."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- НОВЫЕ ФУНКЦИИ (CRUD) ---

def get_all_notes():
    """Возвращает список всех заметок (id и title)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Сортируем по дате обновления (сначала новые)
    cursor.execute("SELECT id, title FROM notes ORDER BY updated_at DESC")
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_id(note_id):
    """Возвращает полную информацию о заметке по её ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def create_note(title, content):
    """Создает новую заметку."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )
    conn.commit()
    new_id = cursor.lastrowid # Получаем ID только что созданной заметки
    conn.close()
    return new_id

def update_note(note_id, title, content):
    """Обновляет существующую заметку и время её изменения."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE notes 
           SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ?""",
        (title, content, note_id)
    )
    conn.commit()
    conn.close()

def delete_note(note_id):
    """Удаляет заметку по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()