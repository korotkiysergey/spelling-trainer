# https://spelling-trainer.onrender.com/

from flask import Flask, render_template, request, jsonify, session, send_file
from gtts import gTTS
import os
import random
import secrets
from database import (
    init_database, get_categories, get_letters,
    get_words_by_filters, get_words_count_by_letter,
    get_irregular_verb_groups, get_irregular_verbs_by_groups
)

import time
from functools import wraps

def retry_on_429(max_retries=3, base_delay=1):
    """Декоратор для повторных попыток при ошибке 429"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise
        return wrapper
    return decorator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'audio_cache'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
    try:
        category_type = request.args.get('type', None)
        categories = get_categories(category_type)
        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_letters', methods=['GET'])
def api_get_letters():
    try:
        category_id = request.args.get('category_id', None, type=int)
        letters = get_words_count_by_letter(category_id)
        return jsonify({'success': True, 'letters': letters})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/count_words', methods=['POST'])
def count_words():
    try:
        data = request.json
        category_ids = data.get('category_ids', [])
        mode = data.get('mode', 'ru_only')
        words = get_words_by_filters(category_ids, None)
        if mode != 'ru_only':
            words = [w for w in words if w['english_word']]
        return jsonify({'success': True, 'count': len(words)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_words_from_db', methods=['POST'])
def get_words_from_db():
    try:
        data = request.json
        category_ids = data.get('category_ids', [])
        letter_ids = data.get('letter_ids', [])
        mode = data.get('mode', 'ru_only')

        words = get_words_by_filters(category_ids, letter_ids)

        if not words:
            return jsonify({'success': False, 'error': 'Нет слов по выбранным фильтрам'})

        word_pairs = []
        for word in words:
            if mode == 'ru_only':
                word_pairs.append((word['russian_word'], None))
            else:
                if word['english_word']:
                    word_pairs.append((word['russian_word'], word['english_word']))

        if not word_pairs:
            return jsonify({'success': False, 'error': 'Нет подходящих слов для выбранного режима'})

        random.shuffle(word_pairs)

        session['word_pairs'] = word_pairs
        session['current_index'] = 0
        session['mode'] = mode
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        return jsonify({'success': True, 'total_words': len(word_pairs)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/save_words', methods=['POST'])
def save_words():
    try:
        data = request.json
        words_text = data.get('words', '')
        mode = data.get('mode', 'ru_only')

        word_pairs = parse_word_pairs(words_text, mode)

        if not word_pairs:
            return jsonify({'success': False, 'error': 'Нет валидных слов'})

        random.shuffle(word_pairs)

        session['word_pairs'] = word_pairs
        session['current_index'] = 0
        session['mode'] = mode
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        return jsonify({'success': True, 'total_words': len(word_pairs)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@retry_on_429()
def generate_audio_file(word, lang, filepath):
    tts = gTTS(text=word, lang=lang)
    tts.save(filepath)


@app.route('/api/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        word = data.get('word', '')
        lang = data.get('lang', 'ru')

        if not word:
            return jsonify({'success': False, 'error': 'Слово не указано'})

        safe_filename = make_safe_filename(word)
        filename = f"{safe_filename}_{lang}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(filepath):
            return jsonify({'success': True, 'audio_url': f'/audio/{filename}'})

        time.sleep(0.5)
        generate_audio_file(word, lang, filepath)

        return jsonify({'success': True, 'audio_url': f'/audio/{filename}'})

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return jsonify({
                'success': False,
                'error': 'Превышен лимит запросов к TTS. Попробуйте позже.'
            })
        return jsonify({'success': False, 'error': error_msg})


@app.route('/audio/<filename>')
def serve_audio(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='audio/mpeg')
    return "File not found", 404


@app.route('/api/get_current_word', methods=['GET'])
def get_current_word():
    try:
        init_session()

        word_pairs = session.get('word_pairs', [])
        current_index = session.get('current_index', 0)
        mode = session.get('mode', 'ru_only')

        if current_index >= len(word_pairs):
            return jsonify({'finished': True, 'stats': session.get('stats')})

        russian_word, english_word = word_pairs[current_index]

        if mode == 'ru_only':
            speak_word = russian_word
            speak_lang = 'ru'
            expected_word = russian_word
        elif mode == 'ru_to_en':
            speak_word = russian_word
            speak_lang = 'ru'
            expected_word = english_word
        else:
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

        if mode == 'ru_only':
            correct_word = russian_word
            heard_word = russian_word
        elif mode == 'ru_to_en':
            correct_word = english_word
            heard_word = russian_word
        else:
            correct_word = russian_word
            heard_word = english_word

        is_correct = user_answer == correct_word

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
        session['current_index'] = current_index + 1

        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'correct_word': correct_word,
            'heard_word': heard_word,
            'stats': {
                'total': stats['total_attempts'],
                'correct': stats['correct_attempts'],
                'percentage': (stats['correct_attempts'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/get_results', methods=['GET'])
def get_results():
    try:
        init_session()

        stats = session.get('stats', {})
        word_pairs = session.get('word_pairs', [])

        total_words = len(word_pairs)
        correct_count = stats.get('correct_attempts', 0)
        percentage = (correct_count / total_words * 100) if total_words > 0 else 0

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
    try:
        session['current_index'] = 0
        session['stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        word_pairs = session.get('word_pairs', [])
        random.shuffle(word_pairs)
        session['word_pairs'] = word_pairs

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# =============================================
# API для неправильных глаголов
# =============================================

@app.route('/api/verbs/get_groups', methods=['GET'])
def api_get_verb_groups():
    """Получение групп неправильных глаголов"""
    try:
        groups = get_irregular_verb_groups()
        return jsonify({'success': True, 'groups': groups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verbs/start_session', methods=['POST'])
def api_verbs_start_session():
    """Запуск сессии тренировки неправильных глаголов"""
    try:
        data = request.json
        group_ids = data.get('group_ids', [])
        verb_mode = data.get('verb_mode', 'translation_to_forms')
        # verb_mode:
        #   'translation_to_forms' — видим перевод, пишем 3 формы
        #   'form_to_rest'         — видим одну форму, пишем остальные + перевод

        verbs = get_irregular_verbs_by_groups(group_ids if group_ids else None)

        if not verbs:
            return jsonify({'success': False, 'error': 'Нет глаголов в выбранных группах'})

        random.shuffle(verbs)

        # Если режим "форма → остальные", для каждого глагола выбираем случайную показываемую форму
        verb_tasks = []
        for verb in verbs:
            if verb_mode == 'translation_to_forms':
                verb_tasks.append({
                    'id': verb['id'],
                    'show': verb['translation'],
                    'show_label': 'Перевод',
                    'form1': verb['form1'],
                    'form2': verb['form2'],
                    'form3': verb['form3'],
                    'translation': verb['translation'],
                    'group_name': verb.get('group_name', ''),
                    'ask_translation': False,
                })
            else:  # form_to_rest
                # Случайно выбираем одну из 3 форм для показа
                shown_form_idx = random.choice([0, 1, 2])
                forms = [verb['form1'], verb['form2'], verb['form3']]
                labels = ['Форма 1 (Infinitive)', 'Форма 2 (Past Simple)', 'Форма 3 (Past Participle)']
                shown_value = forms[shown_form_idx]
                verb_tasks.append({
                    'id': verb['id'],
                    'show': shown_value,
                    'show_label': labels[shown_form_idx],
                    'shown_form_idx': shown_form_idx,
                    'form1': verb['form1'],
                    'form2': verb['form2'],
                    'form3': verb['form3'],
                    'translation': verb['translation'],
                    'group_name': verb.get('group_name', ''),
                    'ask_translation': True,
                })

        session['verb_tasks'] = verb_tasks
        session['verb_current_index'] = 0
        session['verb_mode'] = verb_mode
        session['verb_stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }

        return jsonify({'success': True, 'total_verbs': len(verb_tasks)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verbs/get_current', methods=['GET'])
def api_verbs_get_current():
    """Получение текущего задания по глаголу"""
    try:
        verb_tasks = session.get('verb_tasks', [])
        current_index = session.get('verb_current_index', 0)

        if current_index >= len(verb_tasks):
            return jsonify({'finished': True, 'stats': session.get('verb_stats')})

        task = verb_tasks[current_index]
        return jsonify({
            'finished': False,
            'current_index': current_index,
            'total_verbs': len(verb_tasks),
            'show': task['show'],
            'show_label': task['show_label'],
            'shown_form_idx': task.get('shown_form_idx', -1),
            'group_name': task.get('group_name', ''),
            'ask_translation': task.get('ask_translation', False),
            'verb_mode': session.get('verb_mode'),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verbs/check_answer', methods=['POST'])
def api_verbs_check_answer():
    """Проверка ответа при тренировке глаголов"""
    try:
        data = request.json
        user_form1 = data.get('form1', '').strip().lower()
        user_form2 = data.get('form2', '').strip().lower()
        user_form3 = data.get('form3', '').strip().lower()
        user_translation = data.get('translation', '').strip().lower()

        verb_tasks = session.get('verb_tasks', [])
        current_index = session.get('verb_current_index', 0)
        verb_mode = session.get('verb_mode', 'translation_to_forms')

        if current_index >= len(verb_tasks):
            return jsonify({'success': False, 'error': 'Нет текущего задания'})

        task = verb_tasks[current_index]

        # Нормализация правильных форм (убираем пробелы, нижний регистр)
        # Учитываем варианты написания через /
        def normalize(s):
            return s.strip().lower()

        def check_form(user_val, correct_val):
            """Проверяем форму, учитывая варианты через /"""
            correct_variants = [normalize(v) for v in correct_val.split('/')]
            user_normalized = normalize(user_val)
            return user_normalized in correct_variants or user_normalized == normalize(correct_val)

        shown_form_idx = task.get('shown_form_idx', -1)

        if verb_mode == 'translation_to_forms':
            # Пользователь пишет все 3 формы
            f1_ok = check_form(user_form1, task['form1'])
            f2_ok = check_form(user_form2, task['form2'])
            f3_ok = check_form(user_form3, task['form3'])
            tr_ok = True  # перевод мы показываем, не спрашиваем
            is_correct = f1_ok and f2_ok and f3_ok
        else:
            # Пользователь пишет остальные формы + перевод
            # Не проверяем ту форму, которую показывали
            f1_ok = True if shown_form_idx == 0 else check_form(user_form1, task['form1'])
            f2_ok = True if shown_form_idx == 1 else check_form(user_form2, task['form2'])
            f3_ok = True if shown_form_idx == 2 else check_form(user_form3, task['form3'])
            # Перевод: проверяем по ключевым словам (упрощённая проверка)
            correct_tr = normalize(task['translation'])
            tr_ok = normalize(user_translation) in correct_tr or correct_tr in normalize(user_translation) or normalize(user_translation) == correct_tr
            is_correct = f1_ok and f2_ok and f3_ok and tr_ok

        stats = session['verb_stats']
        stats['total_attempts'] += 1
        if is_correct:
            stats['correct_attempts'] += 1

        stats['session_results'].append({
            'show': task['show'],
            'show_label': task['show_label'],
            'form1': task['form1'],
            'form2': task['form2'],
            'form3': task['form3'],
            'translation': task['translation'],
            'user_form1': user_form1,
            'user_form2': user_form2,
            'user_form3': user_form3,
            'user_translation': user_translation,
            'f1_ok': f1_ok,
            'f2_ok': f2_ok,
            'f3_ok': f3_ok,
            'tr_ok': tr_ok,
            'is_correct': is_correct,
            'shown_form_idx': shown_form_idx,
        })

        session['verb_stats'] = stats
        session['verb_current_index'] = current_index + 1

        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'f1_ok': f1_ok,
            'f2_ok': f2_ok,
            'f3_ok': f3_ok,
            'tr_ok': tr_ok,
            'correct': {
                'form1': task['form1'],
                'form2': task['form2'],
                'form3': task['form3'],
                'translation': task['translation'],
            },
            'stats': {
                'total': stats['total_attempts'],
                'correct': stats['correct_attempts'],
                'percentage': (stats['correct_attempts'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verbs/get_results', methods=['GET'])
def api_verbs_get_results():
    """Итоги тренировки глаголов"""
    try:
        stats = session.get('verb_stats', {})
        verb_tasks = session.get('verb_tasks', [])

        total = len(verb_tasks)
        correct_count = stats.get('correct_attempts', 0)
        percentage = (correct_count / total * 100) if total > 0 else 0

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
            'total': total,
            'correct_count': correct_count,
            'errors_count': total - correct_count,
            'percentage': percentage,
            'session_results': stats.get('session_results', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/verbs/reset_session', methods=['POST'])
def api_verbs_reset_session():
    """Сброс сессии тренировки глаголов"""
    try:
        verb_tasks = session.get('verb_tasks', [])
        random.shuffle(verb_tasks)
        session['verb_tasks'] = verb_tasks
        session['verb_current_index'] = 0
        session['verb_stats'] = {
            'total_attempts': 0,
            'correct_attempts': 0,
            'session_results': []
        }
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# =============================================
# Вспомогательные функции
# =============================================

def parse_word_pairs(text, mode):
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
    safe_chars = "абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    safe_filename = "".join(c if c in safe_chars else "_" for c in word)
    return safe_filename[:50]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
