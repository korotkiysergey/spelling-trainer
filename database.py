import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = 'words_database.db'


@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Инициализация базы данных"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Таблица категорий (классы, уроки и т.д.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                type TEXT NOT NULL CHECK(type IN ('class', 'lesson', 'topic')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица букв (для словарных слов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                letter TEXT NOT NULL UNIQUE,
                sort_order INTEGER
            )
        ''')

        # Таблица слов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                russian_word TEXT NOT NULL,
                english_word TEXT,
                category_id INTEGER,
                letter_id INTEGER,
                difficulty INTEGER DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (letter_id) REFERENCES letters(id)
            )
        ''')

        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_category ON words(category_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_letter ON words(letter_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_words_russian ON words(russian_word)')

        # =============================================
        # Таблица групп неправильных глаголов
        # =============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irregular_verb_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                sort_order INTEGER DEFAULT 0
            )
        ''')

        # =============================================
        # Таблица неправильных глаголов
        # =============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irregular_verbs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form1 TEXT NOT NULL,
                form2 TEXT NOT NULL,
                form3 TEXT NOT NULL,
                translation TEXT NOT NULL,
                group_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES irregular_verb_groups(id)
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_verbs_group ON irregular_verbs(group_id)')

        conn.commit()
        print("✅ База данных успешно инициализирована!")


# =============================================
# Функции для неправильных глаголов
# =============================================

def add_irregular_verb_group(name, description='', sort_order=0):
    """Добавление группы неправильных глаголов"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO irregular_verb_groups (name, description, sort_order) VALUES (?, ?, ?)',
                (name, description, sort_order)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM irregular_verb_groups WHERE name = ?', (name,))
            return cursor.fetchone()[0]


def add_irregular_verb(form1, form2, form3, translation, group_name=None):
    """Добавление неправильного глагола"""
    with get_db() as conn:
        cursor = conn.cursor()

        group_id = None
        if group_name:
            cursor.execute('SELECT id FROM irregular_verb_groups WHERE name = ?', (group_name,))
            result = cursor.fetchone()
            if result:
                group_id = result[0]

        cursor.execute('''
            INSERT INTO irregular_verbs (form1, form2, form3, translation, group_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (form1, form2, form3, translation, group_id))

        conn.commit()
        return cursor.lastrowid


def get_irregular_verb_groups():
    """Получение всех групп неправильных глаголов с количеством глаголов"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.*, COUNT(v.id) as verb_count
            FROM irregular_verb_groups g
            LEFT JOIN irregular_verbs v ON g.id = v.group_id
            GROUP BY g.id
            ORDER BY g.sort_order, g.name
        ''')
        return [dict(row) for row in cursor.fetchall()]


def get_irregular_verbs_by_groups(group_ids=None):
    """Получение неправильных глаголов по группам"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT v.*, g.name as group_name
            FROM irregular_verbs v
            LEFT JOIN irregular_verb_groups g ON v.group_id = g.id
            WHERE 1=1
        '''
        params = []

        if group_ids:
            placeholders = ','.join('?' * len(group_ids))
            query += f' AND v.group_id IN ({placeholders})'
            params.extend(group_ids)

        query += ' ORDER BY g.sort_order, v.form1'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def delete_all_irregular_verbs():
    """Удаление всех неправильных глаголов"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM irregular_verbs')
        cursor.execute('DELETE FROM irregular_verb_groups')
        conn.commit()
        print("✅ Все неправильные глаголы удалены")


# =============================================
# Оригинальные функции
# =============================================

def add_category(name, description='', category_type='class'):
    """Добавление категории"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categories (name, description, type) VALUES (?, ?, ?)',
                (name, description, category_type)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"⚠️ Категория '{name}' уже существует")
            cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
            return cursor.fetchone()[0]


def add_letter(letter, sort_order=None):
    """Добавление буквы"""
    with get_db() as conn:
        cursor = conn.cursor()
        if sort_order is None:
            sort_order = ord(letter.upper())
        try:
            cursor.execute(
                'INSERT INTO letters (letter, sort_order) VALUES (?, ?)',
                (letter.upper(), sort_order)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM letters WHERE letter = ?', (letter.upper(),))
            return cursor.fetchone()[0]


def add_word(russian_word, english_word=None, category_name=None, difficulty=1):
    """Добавление слова"""
    with get_db() as conn:
        cursor = conn.cursor()

        first_letter = russian_word[0].upper()
        letter_id = add_letter(first_letter)

        category_id = None
        if category_name:
            cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
            result = cursor.fetchone()
            if result:
                category_id = result[0]

        cursor.execute('''
            INSERT INTO words (russian_word, english_word, category_id, letter_id, difficulty)
            VALUES (?, ?, ?, ?, ?)
        ''', (russian_word, english_word, category_id, letter_id, difficulty))

        conn.commit()
        return cursor.lastrowid


def get_categories(category_type=None):
    """Получение списка категорий"""
    with get_db() as conn:
        cursor = conn.cursor()
        if category_type:
            cursor.execute(
                'SELECT * FROM categories WHERE type = ? ORDER BY name',
                (category_type,)
            )
        else:
            cursor.execute('SELECT * FROM categories ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]


def get_letters():
    """Получение списка букв"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM letters ORDER BY sort_order')
        return [dict(row) for row in cursor.fetchall()]


def get_words_by_filters(category_ids=None, letter_ids=None, limit=None):
    """Получение слов по фильтрам"""
    with get_db() as conn:
        cursor = conn.cursor()

        query = '''
            SELECT w.*, c.name as category_name, l.letter
            FROM words w
            LEFT JOIN categories c ON w.category_id = c.id
            LEFT JOIN letters l ON w.letter_id = l.id
            WHERE 1=1
        '''
        params = []

        if category_ids:
            placeholders = ','.join('?' * len(category_ids))
            query += f' AND w.category_id IN ({placeholders})'
            params.extend(category_ids)

        if letter_ids:
            placeholders = ','.join('?' * len(letter_ids))
            query += f' AND w.letter_id IN ({placeholders})'
            params.extend(letter_ids)

        query += ' ORDER BY w.russian_word'

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_words_count_by_letter(category_id=None):
    """Получение количества слов по буквам"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT l.letter, l.id, COUNT(w.id) as count
            FROM letters l
            LEFT JOIN words w ON l.id = w.letter_id
        '''
        params = []

        if category_id:
            query += ' AND w.category_id = ?'
            params.append(category_id)

        query += ' GROUP BY l.id, l.letter ORDER BY l.sort_order'

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def delete_all_words():
    """Удаление всех слов (для переинициализации)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM words')
        conn.commit()
        print("✅ Все слова удалены")


def get_database_stats():
    """Получение статистики БД"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM categories')
        categories_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM letters')
        letters_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM words')
        words_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM words WHERE english_word IS NOT NULL')
        translations_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM irregular_verbs')
        verbs_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM irregular_verb_groups')
        verb_groups_count = cursor.fetchone()[0]

        return {
            'categories': categories_count,
            'letters': letters_count,
            'total_words': words_count,
            'with_translation': translations_count,
            'irregular_verbs': verbs_count,
            'irregular_verb_groups': verb_groups_count,
        }


if __name__ == '__main__':
    init_database()
    stats = get_database_stats()
    print(f"\n📊 Статистика базы данных:")
    print(f"Категорий: {stats['categories']}")
    print(f"Букв: {stats['letters']}")
    print(f"Всего слов: {stats['total_words']}")
    print(f"С переводом: {stats['with_translation']}")
    print(f"Неправильных глаголов: {stats['irregular_verbs']}")
    print(f"Групп глаголов: {stats['irregular_verb_groups']}")
