from flask import Flask, render_template, request, jsonify, session, send_file
from gtts import gTTS
import os
import json
import random
from datetime import datetime
import secrets
from database import (
    init_database, get_categories, get_letters,
    get_words_by_filters, get_words_count_by_letter
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'audio_cache'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Создаем папку для аудио, если её нет
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Инициализируем базу данных при старте
init_database()


def init_session():
    """Инициализация сессии пользователя"""
    if 'stats' not in session:
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }
    if 'word_pairs' not in session:
        session['word_pairs'] = []
    if 'current_index' not in session:
        session['current_index'] = 0


@app.route('/')
def index():
    """Главная страница"""
    init_session()
    return render_template('index.html')


@app.route('/api/get_categories', methods=['GET'])
def api_get_categories():
    """Получение списка категорий"""
    try:
        category_type = request.args.get('type', None)
        categories = get_categories(category_type)
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_letters', methods=['GET'])
def api_get_letters():
    """Получение списка букв с количеством слов"""
    try:
        category_id = request.args.get('category_id', None, type=int)
        letters = get_words_count_by_letter(category_id)
        return jsonify({'success': True, 'letters': letters})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_words_from_db', methods=['POST'])
def get_words_from_db():
    """Получение слов из БД по фильтрам"""
    try:
        data = request.json
        category_ids = data.get('category_ids', [])
        letter_ids = data.get('letter_ids', [])
        mode = data.get('mode', 'ru_only')

        # Получаем слова из БД
        words = get_words_by_filters(category_ids, letter_ids)

        if not words:
            return jsonify({'success': False, 'error': 'Нет слов по выбранным фильтрам'})

        # Формируем пары слов в зависимости от режима
        word_pairs = []
        for word in words:
            if mode == 'ru_only':
                word_pairs.append((word['russian_word'], None))
            else:
                if word['english_word']:
                    word_pairs.append((word['russian_word'], word['english_word']))

        if not word_pairs:
            return jsonify({'success': False, 'error': 'Нет подходящих слов для выбранного режима'})

        # Перемешиваем слова
        random.shuffle(word_pairs)

        session['word_pairs'] = word_pairs
        session['current_index'] = 0
        session['mode'] = mode
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        return jsonify({
            'success': True,
            'total_words': len(word_pairs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/save_words', methods=['POST'])
def save_words():
    """Сохранение списка слов"""
    try:
        data = request.json
        words_text = data.get('words', '')
        mode = data.get('mode', 'ru_only')

        word_pairs = parse_word_pairs(words_text, mode)

        if not word_pairs:
            return jsonify({'success': False, 'error': 'Нет валидных слов'})

        # Перемешиваем слова
        random.shuffle(word_pairs)

        session['word_pairs'] = word_pairs
        session['current_index'] = 0
        session['mode'] = mode
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        return jsonify({
            'success': True,
            'total_words': len(word_pairs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/generate_audio', methods=['POST'])
def generate_audio():
    """Генерация аудиофайла для слова"""
    try:
        data = request.json
        word = data.get('word', '')
        lang = data.get('lang', 'ru')

        if not word:
            return jsonify({'success': False, 'error': 'Слово не указано'})

        # Создаем безопасное имя файла
        safe_filename = make_safe_filename(word)
        filename = f"{safe_filename}_{lang}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Если файл уже существует, возвращаем его
        if os.path.exists(filepath):
            return jsonify({
                'success': True,
                'audio_url': f'/audio/{filename}'
            })

        # Генерируем аудио
        tts = gTTS(text=word, lang=lang)
        tts.save(filepath)

        return jsonify({
            'success': True,
            'audio_url': f'/audio/{filename}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/audio/<filename>')
def serve_audio(filename):
    """Отдача аудиофайлов"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='audio/mpeg')
    return "File not found", 404


@app.route('/api/get_current_word', methods=['GET'])
def get_current_word():
    """Получение текущего слова"""
    try:
        init_session()

        word_pairs = session.get('word_pairs', [])
        current_index = session.get('current_index', 0)
        mode = session.get('mode', 'ru_only')

        if current_index >= len(word_pairs):
            return jsonify({
                'finished': True,
                'stats': session.get('stats')
            })

        russian_word, english_word = word_pairs[current_index]

        # Определяем, какое слово озвучивать и какое ожидать
        if mode == 'ru_only':
            speak_word = russian_word
            speak_lang = 'ru'
            expected_word = russian_word
        elif mode == 'ru_to_en':
            speak_word = russian_word
            speak_lang = 'ru'
            expected_word = english_word
        else:  # en_to_ru
            speak_word = english_word
            speak_lang = 'en'
            expected_word = russian_word

        return jsonify({
            'finished': False,
            'current_index': current_index,
            'total_words': len(word_pairs),
            'speak_word': speak_word,
            'speak_lang': speak_lang,
            'mode': mode
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    """Проверка ответа пользователя"""
    try:
        init_session()

        data = request.json
        user_answer = data.get('answer', '').strip()

        word_pairs = session.get('word_pairs', [])
        current_index = session.get('current_index', 0)
        mode = session.get('mode', 'ru_only')

        if current_index >= len(word_pairs):
            return jsonify({'success': False, 'error': 'Нет текущего слова'})

        russian_word, english_word = word_pairs[current_index]

        # Определяем правильный ответ
        if mode == 'ru_only':
            correct_word = russian_word
            heard_word = russian_word
        elif mode == 'ru_to_en':
            correct_word = english_word
            heard_word = russian_word
        else:  # en_to_ru
            correct_word = russian_word
            heard_word = english_word

        is_correct = user_answer.lower() == correct_word.lower()

        # Обновляем статистику
        stats = session['stats']
        stats['total_attempts'] += 1
        if is_correct:
            stats['correct_attempts'] += 1

        stats['session_results'].append({
            'heard_word': heard_word,
            'correct_word': correct_word,
            'user_answer': user_answer,
            'is_correct': is_correct
        })

        session['stats'] = stats

        # Переходим к следующему слову
        session['current_index'] = current_index + 1

        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'correct_word': correct_word,
            'heard_word': heard_word,
            'stats': {
                'total': stats['total_attempts'],
                'correct': stats['correct_attempts'],
                'percentage': (stats['correct_attempts'] / stats['total_attempts'] * 100) if stats[
                                                                                                 'total_attempts'] > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_results', methods=['GET'])
def get_results():
    """Получение результатов сессии"""
    try:
        init_session()

        stats = session.get('stats', {})
        word_pairs = session.get('word_pairs', [])

        total_words = len(word_pairs)
        correct_count = stats.get('correct_attempts', 0)
        percentage = (correct_count / total_words * 100) if total_words > 0 else 0

        # Вычисляем оценку
        if percentage >= 95:
            grade = 5
        elif percentage >= 85:
            grade = 4
        elif percentage >= 75:
            grade = 3
        elif percentage >= 60:
            grade = 2
        else:
            grade = 1

        return jsonify({
            'grade': grade,
            'total_words': total_words,
            'correct_count': correct_count,
            'errors_count': total_words - correct_count,
            'percentage': percentage,
            'session_results': stats.get('session_results', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """Сброс текущей сессии"""
    try:
        session['current_index'] = 0
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        # Перемешиваем слова заново
        word_pairs = session.get('word_pairs', [])
        random.shuffle(word_pairs)
        session['word_pairs'] = word_pairs

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def parse_word_pairs(text, mode):
    """Парсинг пар слов из текста"""
    pairs = []

    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if mode == 'ru_only':
            pairs.append((line, None))
        else:
            if '-' not in line:
                continue
            parts = line.split('-', 1)
            if len(parts) == 2:
                russian = parts[0].strip()
                english = parts[1].strip()
                if russian and english:
                    pairs.append((russian, english))

    return pairs


def make_safe_filename(word):
    """Создание безопасного имени файла"""
    safe_chars = "абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    safe_filename = "".join(c if c in safe_chars else "_" for c in word)
    return safe_filename[:50]  # Ограничиваем длину


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)