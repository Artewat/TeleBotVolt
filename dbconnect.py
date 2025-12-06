import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/volunteer_bot.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица для анкет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица для результатов игр
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            volunteer_type TEXT NOT NULL,
            scores TEXT,
            game_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица для объединенных данных (если не существует)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            volunteer_type TEXT NOT NULL,
            scores TEXT,
            game_duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

async def save_survey(user_id: int, username: str, name: str, age: int, gender: str):
    """Сохраняет данные анкеты в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Обновляем или вставляем анкету
    cursor.execute('''
        INSERT OR REPLACE INTO surveys (user_id, username, name, age, gender)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, name, age, gender))
    
    conn.commit()
    conn.close()

async def save_results(user_id: int, volunteer_type: str, scores: dict, game_duration: int = None, username: str = None, first_name: str = None, last_name: str = None):
    """Сохраняет результаты игры в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    scores_str = str(scores)
    
    # Сохраняем результаты игры
    cursor.execute('''
        INSERT INTO game_results 
        (user_id, username, first_name, last_name, volunteer_type, scores, game_duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, volunteer_type, scores_str, game_duration))
    
    # Получаем данные анкеты пользователя
    cursor.execute('SELECT name, age, gender FROM surveys WHERE user_id = ?', (user_id,))
    survey_data = cursor.fetchone()
    
    # Сохраняем объединенные данные
    if survey_data:
        name, age, gender = survey_data
        cursor.execute('''
            INSERT INTO combined_results 
            (user_id, username, name, age, gender, volunteer_type, scores, game_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, name, age, gender, volunteer_type, scores_str, game_duration))
    else:
        # Если анкеты нет, сохраняем только игровые данные
        cursor.execute('''
            INSERT INTO combined_results 
            (user_id, username, volunteer_type, scores, game_duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, volunteer_type, scores_str, game_duration))
    
    conn.commit()
    conn.close()

def get_user_stats(user_id: int):
    """Получает статистику пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) as games_played, 
               volunteer_type,
               game_duration,
               created_at
        FROM game_results 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

# Инициализируем базу данных при импорте
init_db()