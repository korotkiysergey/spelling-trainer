// Начало тренировки
async function startTraining() {
    if (selectedSource === 'database') {
        // Работа с базой данных
        if (selectedCategories.length === 0) {
            alert('Пожалуйста, выберите хотя бы одну категорию!');
            return;
        }

        // Для режима "только русские" требуем выбор букв
        if (currentMode === 'ru_only' && selectedLetters.length === 0) {
            alert('Пожалуйста, выберите хотя бы одну букву!');
            return;
        }

        document.getElementById('loading').classList.add('active');

        try {
            const response = await fetch('/api/get_words_from_db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category_ids: selectedCategories,
                    letter_ids: currentMode === 'ru_only' ? selectedLetters : [],
                    mode: currentMode
                })
            });

            const data = await response.json();

            if (data.success) {
                updateModeHint();
                await loadCurrentWord();
                showSection('training-section');
            } else {
                alert('Ошибка: ' + data.error);
            }
        } catch (error) {
            alert('Ошибка при загрузке слов: ' + error);
        } finally {
            document.getElementById('loading').classList.remove('active');
        }
    } else {
        // Ручной ввод слов
        const wordsText = document.getElementById('words-textarea').value;

        if (!wordsText.trim()) {
            alert('Пожалуйста, введите слова!');
            return;
        }

        document.getElementById('loading').classList.add('active');

        try {
            const response = await fetch('/api/save_words', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    words: wordsText,
                    mode: currentMode
                })
            });

            const data = await response.json();

            if (data.success) {
                updateModeHint();
                await loadCurrentWord();
                showSection('training-section');
            } else {
                alert('Ошибка: ' + data.error);
            }
        } catch (error) {
            alert('Ошибка при сохранении слов: ' + error);
        } finally {
            document.getElementById('loading').classList.remove('active');
        }
    }
}

// Обновление подсказки в зависимости от режима
function updateModeHint() {
    const hintElement = document.getElementById('mode-hint');

    if (currentMode === 'ru_only') {
        hintElement.textContent = '📝 Прослушайте русское слово и напишите его';
    } else if (currentMode === 'ru_to_en') {
        hintElement.textContent = '🇷🇺→🇬🇧 Нажмите "Прослушать слово", чтобы услышать русское слово → напишите перевод на английском';
    } else {
        hintElement.textContent = '🇬🇧→🇷🇺 Нажмите "Прослушать слово", чтобы услышать английское слово → напишите перевод на русском';
    }
}

// Загрузка текущего слова
async function loadCurrentWord() {
    try {
        const response = await fetch('/api/get_current_word');
        const data = await response.json();

        if (data.finished) {
            showResults();
            return;
        }

        document.getElementById('progress-info').textContent =
            `Слово ${data.current_index + 1} из ${data.total_words}`;

        // Для режимов с переводом показываем слово, которое произносится
        // Для режима "только русские" - показываем ???
        if (currentMode === 'ru_only') {
            document.getElementById('word-display').textContent = '???';
        } else {
            // Показываем слово, которое будет произнесено
            document.getElementById('word-display').textContent = data.speak_word;
        }

        document.getElementById('answer-input').value = '';
        document.getElementById('result-message').textContent = '';
        document.getElementById('result-message').className = 'result-message';

        const nextBtn = document.getElementById('next-btn');
        if (data.current_index === data.total_words - 1) {
            nextBtn.textContent = '🏁 Завершить тестирование';
            nextBtn.className = 'btn btn-success';
        } else {
            nextBtn.textContent = '➡️ Следующее слово';
            nextBtn.className = 'btn btn-primary';
        }

        // Автоматически озвучиваем только в режиме "только русские"
        if (currentMode === 'ru_only') {
            await speakWord();
        }

    } catch (error) {
        alert('Ошибка загрузки слова: ' + error);
    }
}

// Озвучивание слова
async function speakWord() {
    if (isPlaying) return;

    try {
        isPlaying = true;
        const response = await fetch('/api/get_current_word');
        const data = await response.json();

        if (data.finished) return;

        const audioResponse = await fetch('/api/generate_audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                word: data.speak_word,
                lang: data.speak_lang
            })
        });

        const audioData = await audioResponse.json();

        if (audioData.success) {
            const audio = document.getElementById('audio-player');
            audio.src = audioData.audio_url;
            await audio.play();
            audio.onended = () => { isPlaying = false; };
        } else {
            console.error('Ошибка генерации аудио:', audioData.error);
            alert('Ошибка генерации аудио: ' + audioData.error);
            isPlaying = false;
        }
    } catch (error) {
        console.error('Ошибка воспроизведения:', error);
        alert('Ошибка воспроизведения: ' + error.message || error);
        isPlaying = false;
    }
}

// Проверка ответа
async function checkAnswer() {
    const answer = document.getElementById('answer-input').value.trim();

    if (!answer) {
        alert('Пожалуйста, введите слово!');
        return;
    }

    try {
        const response = await fetch('/api/check_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer: answer })
        });

        const data = await response.json();

        if (!data.success) {
            alert('Ошибка: ' + data.error);
            return;
        }

        const resultMsg = document.getElementById('result-message');
        const wordDisplay = document.getElementById('word-display');

        if (data.is_correct) {
            resultMsg.textContent = 'Правильно! ✅';
            resultMsg.className = 'result-message correct';
        } else {
            resultMsg.textContent = `Неправильно! ❌\nПравильное написание: ${data.correct_word}`;
            resultMsg.className = 'result-message incorrect';
        }

        // Обновляем отображение слова в зависимости от режима
        if (currentMode === 'ru_only') {
            // Для режима "только русские" показываем само слово
            wordDisplay.textContent = data.correct_word;
        } else if (currentMode === 'ru_to_en') {
            // Для ru→en показываем: русское → английское
            wordDisplay.textContent = `${data.heard_word} → ${data.correct_word}`;
        } else {
            // Для en→ru показываем: английское → русское
            wordDisplay.textContent = `${data.heard_word} → ${data.correct_word}`;
        }

        // Обновляем статистику
        document.getElementById('total-attempts').textContent = data.stats.total;
        document.getElementById('correct-answers').textContent = data.stats.correct;
        document.getElementById('percentage').textContent = data.stats.percentage.toFixed(1);

        // Переходим к следующему слову
        setTimeout(loadCurrentWord, 1500);

    } catch (error) {
        alert('Ошибка проверки ответа: ' + error);
    }
}

// Показать результаты
async function showResults() {
    try {
        const response = await fetch('/api/get_results');
        const data = await response.json();

        document.getElementById('grade-display').textContent = data.grade;

        const statsHtml = `
            <p><strong>Всего слов:</strong> ${data.total_words}</p>
            <p><strong>Правильно:</strong> ${data.correct_count}</p>
            <p><strong>Ошибок:</strong> ${data.errors_count}</p>
            <p><strong>Процент правильных ответов:</strong> ${data.percentage.toFixed(1)}%</p>
        `;
        document.getElementById('results-stats').innerHTML = statsHtml;

        const incorrectHtml = data.session_results
            .filter(r => !r.is_correct)
            .map(r => `
                <div class="word-item incorrect">
                    ${currentMode !== 'ru_only' ? `<div>Услышали: ${r.heard_word}</div>` : ''}
                    <div>Ваш ответ: <span class="user-answer">${r.user_answer}</span></div>
                    <div>Правильно: <span class="correct-answer">${r.correct_word}</span></div>
                </div>
            `).join('') || '<p>Все слова написаны правильно! 🎉</p>';

        document.getElementById('incorrect-words').innerHTML = incorrectHtml;

        const correctHtml = data.session_results
            .filter(r => r.is_correct)
            .map(r => `
                <div class="word-item correct">
                    ${currentMode === 'ru_only'
                        ? `• ${r.correct_word} ✓`
                        : `• ${r.heard_word} → ${r.correct_word} ✓`}
                </div>
            `).join('') || '<p>Нет правильно написанных слов.</p>';

        document.getElementById('correct-words').innerHTML = correctHtml;

        showSection('results-section');

    } catch (error) {
        alert('Ошибка загрузки результатов: ' + error);
    }
}

// Повторить тренировку
async function retryTraining() {
    try {
        await fetch('/api/reset_session', { method: 'POST' });
        await loadCurrentWord();
        showSection('training-section');
    } catch (error) {
        alert('Ошибка перезапуска: ' + error);
    }
}

// Вернуться к настройкам
function backToSetup() {
    showSection('setup-section');
}