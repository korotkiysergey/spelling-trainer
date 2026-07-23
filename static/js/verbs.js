// =============================================
// Модуль тренировки неправильных глаголов
// =============================================

let verbMode = 'translation_to_forms';
let selectedVerbGroups = [];
let allVerbGroups = [];
let verbAnswerSubmitted = false; // защита от двойного нажатия

// =============================================
// Инициализация вкладки глаголов
// =============================================

async function initVerbsTab() {
    await loadVerbGroups();
}

async function loadVerbGroups() {
    try {
        const response = await fetch('/api/verbs/get_groups');
        const data = await response.json();
        if (data.success) {
            allVerbGroups = data.groups;
            renderVerbGroups();
        }
    } catch (error) {
        console.error('Ошибка загрузки групп глаголов:', error);
    }
}

function renderVerbGroups() {
    const container = document.getElementById('verb-groups-container');
    if (!container) return;

    if (allVerbGroups.length === 0) {
        container.innerHTML = '<p class="no-data-msg">Нет групп глаголов. Запустите populate_irregular_verbs.py</p>';
        return;
    }

    container.innerHTML = allVerbGroups.map(group => `
        <div class="option-card verb-group-card" onclick="toggleVerbGroup(${group.id}, this)" data-id="${group.id}">
            <input type="checkbox" id="vg-${group.id}"
                   onchange="event.stopPropagation(); toggleVerbGroup(${group.id}, this.parentElement)">
            <label for="vg-${group.id}" onclick="event.stopPropagation()">
                <strong>${group.name}</strong>
                <span class="verb-count">${group.verb_count} глаголов</span>
            </label>
        </div>
    `).join('');
}

function toggleVerbGroup(groupId, element) {
    const checkbox = element.querySelector('input[type="checkbox"]');
    checkbox.checked = !checkbox.checked;
    element.classList.toggle('selected');
    selectedVerbGroups = checkbox.checked
        ? [...selectedVerbGroups, groupId]
        : selectedVerbGroups.filter(id => id !== groupId);
    updateVerbCount();
}

function selectAllVerbGroups() {
    selectedVerbGroups = [];
    document.querySelectorAll('.verb-group-card').forEach(card => {
        card.classList.add('selected');
        card.querySelector('input[type="checkbox"]').checked = true;
        selectedVerbGroups.push(parseInt(card.dataset.id));
    });
    updateVerbCount();
}

function deselectAllVerbGroups() {
    document.querySelectorAll('.verb-group-card').forEach(card => {
        card.classList.remove('selected');
        card.querySelector('input[type="checkbox"]').checked = false;
    });
    selectedVerbGroups = [];
    updateVerbCount();
}

function updateVerbCount() {
    const total = allVerbGroups
        .filter(g => selectedVerbGroups.includes(g.id))
        .reduce((sum, g) => sum + g.verb_count, 0);
    const el = document.getElementById('selected-verbs-count');
    if (el) el.textContent = total;
}

function selectVerbMode(mode, element) {
    verbMode = mode;
    document.querySelectorAll('.verb-mode-option').forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');
}

// =============================================
// Запуск тренировки
// =============================================

async function startVerbTraining() {
    if (selectedVerbGroups.length === 0) {
        alert('Пожалуйста, выберите хотя бы одну группу глаголов!');
        return;
    }

    document.getElementById('verb-loading').classList.add('active');

    try {
        const response = await fetch('/api/verbs/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ group_ids: selectedVerbGroups, verb_mode: verbMode })
        });

        const data = await response.json();
        if (data.success) {
            await loadCurrentVerb();
            showVerbSection('verb-training-section');
        } else {
            alert('Ошибка: ' + data.error);
        }
    } catch (error) {
        alert('Ошибка запуска тренировки: ' + error);
    } finally {
        document.getElementById('verb-loading').classList.remove('active');
    }
}

// =============================================
// Загрузка текущего глагола
// =============================================

async function loadCurrentVerb() {
    try {
        const response = await fetch('/api/verbs/get_current');
        const data = await response.json();

        if (data.finished) {
            await showVerbResults();
            return;
        }

        verbAnswerSubmitted = false;

        // Прогресс
        document.getElementById('verb-progress-info').textContent =
            `Глагол ${data.current_index + 1} из ${data.total_verbs}`;

        // Показываем слово/подсказку
        document.getElementById('verb-show-label').textContent = data.show_label + ':';
        document.getElementById('verb-show-value').textContent = data.show;
        document.getElementById('verb-group-badge').textContent = data.group_name || '';

        // Сбрасываем все поля ввода
        ['verb-input-form1', 'verb-input-form2', 'verb-input-form3', 'verb-input-translation'].forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = '';
            el.disabled = false;
            el.classList.remove('field-correct', 'field-incorrect', 'field-disabled');
        });

        // Скрываем все подсказки-хинты
        ['verb-hint-form1', 'verb-hint-form2', 'verb-hint-form3', 'verb-hint-translation'].forEach(id => {
            const el = document.getElementById(id);
            if (el) { el.textContent = ''; el.style.display = 'none'; }
        });

        // Сбрасываем сообщение результата
        const resultEl = document.getElementById('verb-result-message');
        resultEl.textContent = '';
        resultEl.className = 'verb-result-message';

        // Кнопки: показываем «Проверить», скрываем «Следующий»
        const checkBtn = document.getElementById('verb-check-btn');
        const nextBtn  = document.getElementById('verb-next-btn');
        checkBtn.disabled = false;
        checkBtn.style.display = 'inline-block';
        nextBtn.style.display  = 'none';

        // Настраиваем поля в зависимости от режима
        setupVerbInputFields(data);

        // Фокус на первое доступное поле
        setTimeout(() => {
            const first = document.querySelector('.verb-form-input:not([disabled])');
            if (first) first.focus();
        }, 80);

    } catch (error) {
        console.error('Ошибка loadCurrentVerb:', error);
        alert('Ошибка загрузки глагола: ' + error);
    }
}

function setupVerbInputFields(data) {
    const isFormToRest = data.verb_mode === 'form_to_rest';
    const shownIdx = data.shown_form_idx; // 0 | 1 | 2 | -1

    const rows  = ['verb-row-form1', 'verb-row-form2', 'verb-row-form3'];
    const inputs = ['verb-input-form1', 'verb-input-form2', 'verb-input-form3'];

    const trRow = document.getElementById('verb-row-translation');
    trRow.style.display = isFormToRest ? 'flex' : 'none';

    rows.forEach((rowId, idx) => {
        const row   = document.getElementById(rowId);
        const input = document.getElementById(inputs[idx]);

        if (isFormToRest && idx === shownIdx) {
            // Эта форма показывается — заполняем и блокируем
            input.value = data.show;
            input.disabled = true;
            input.classList.add('field-disabled');
        } else {
            input.disabled = false;
            input.classList.remove('field-disabled');
        }
    });
}

// =============================================
// Проверка ответа
// =============================================

async function checkVerbAnswer() {
    if (verbAnswerSubmitted) return; // не обрабатываем дважды

    const form1       = document.getElementById('verb-input-form1').value.trim();
    const form2       = document.getElementById('verb-input-form2').value.trim();
    const form3       = document.getElementById('verb-input-form3').value.trim();
    const translation = (document.getElementById('verb-input-translation').value || '').trim();

    // Проверяем, что все видимые незаблокированные поля заполнены
    const emptyInputs = Array.from(document.querySelectorAll('.verb-form-input:not([disabled])'))
        .filter(el => el.closest('.verb-input-row').style.display !== 'none' && !el.value.trim());
    if (emptyInputs.length > 0) {
        emptyInputs[0].focus();
        emptyInputs[0].classList.add('field-shake');
        setTimeout(() => emptyInputs[0].classList.remove('field-shake'), 500);
        return;
    }

    verbAnswerSubmitted = true;
    document.getElementById('verb-check-btn').disabled = true;

    try {
        const response = await fetch('/api/verbs/check_answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ form1, form2, form3, translation })
        });

        const data = await response.json();
        if (!data.success) {
            alert('Ошибка: ' + data.error);
            verbAnswerSubmitted = false;
            document.getElementById('verb-check-btn').disabled = false;
            return;
        }

        // Подсвечиваем поля
        [
            { id: 'verb-input-form1', ok: data.f1_ok },
            { id: 'verb-input-form2', ok: data.f2_ok },
            { id: 'verb-input-form3', ok: data.f3_ok },
            { id: 'verb-input-translation', ok: data.tr_ok },
        ].forEach(({ id, ok }) => {
            const el = document.getElementById(id);
            if (!el || el.disabled) return;
            el.classList.add(ok ? 'field-correct' : 'field-incorrect');
        });

        // Показываем подсказки с правильными ответами для ошибочных полей
        showVerbCorrectAnswers(data.correct, data.f1_ok, data.f2_ok, data.f3_ok, data.tr_ok);

        // Блокируем все поля
        document.querySelectorAll('.verb-form-input').forEach(el => el.disabled = true);

        // Сообщение результата
        const resultEl = document.getElementById('verb-result-message');
        resultEl.textContent = data.is_correct ? '✅ Верно!' : '❌ Есть ошибки — посмотрите подсказки';
        resultEl.className = 'verb-result-message ' + (data.is_correct ? 'correct' : 'incorrect');

        // Обновляем статистику
        document.getElementById('verb-total-attempts').textContent = data.stats.total;
        document.getElementById('verb-correct-answers').textContent = data.stats.correct;
        document.getElementById('verb-percentage').textContent = data.stats.percentage.toFixed(1);

        // Скрываем «Проверить», показываем «Следующий»
        const checkBtn = document.getElementById('verb-check-btn');
        const nextBtn  = document.getElementById('verb-next-btn');
        checkBtn.style.display = 'none';
        nextBtn.style.display  = 'inline-block';

        // Обновляем текст кнопки «Следующий»
        const isLast = data.stats.total >= document.getElementById('verb-progress-info').textContent.split(' из ')[1];
        nextBtn.textContent = isLast ? '🏁 Завершить тестирование' : '➡️ Следующий глагол';
        nextBtn.className   = isLast ? 'btn btn-success' : 'btn btn-primary';

        // При правильном ответе — автопереход через 1.5 сек
        if (data.is_correct) {
            setTimeout(() => {
                if (verbAnswerSubmitted) loadCurrentVerb();
            }, 1500);
        }
        // При ошибке — ждём, пока пользователь сам нажмёт «Следующий»

    } catch (error) {
        console.error('Ошибка checkVerbAnswer:', error);
        alert('Ошибка проверки: ' + error);
        verbAnswerSubmitted = false;
        document.getElementById('verb-check-btn').disabled = false;
    }
}

function showVerbCorrectAnswers(correct, f1ok, f2ok, f3ok, trok) {
    const hints = [
        { id: 'verb-hint-form1',        val: correct.form1,       ok: f1ok },
        { id: 'verb-hint-form2',        val: correct.form2,       ok: f2ok },
        { id: 'verb-hint-form3',        val: correct.form3,       ok: f3ok },
        { id: 'verb-hint-translation',  val: correct.translation, ok: trok },
    ];
    hints.forEach(({ id, val, ok }) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (!ok) {
            el.textContent = '✔ ' + val;
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
        }
    });
}

// =============================================
// Результаты
// =============================================

async function showVerbResults() {
    try {
        const response = await fetch('/api/verbs/get_results');
        const data = await response.json();

        document.getElementById('verb-grade-display').textContent = data.grade;

        document.getElementById('verb-results-stats').innerHTML = `
            <p><strong>Всего глаголов:</strong> ${data.total}</p>
            <p><strong>Правильно:</strong> ${data.correct_count}</p>
            <p><strong>Ошибок:</strong> ${data.errors_count}</p>
            <p><strong>Процент правильных:</strong> ${data.percentage.toFixed(1)}%</p>
        `;

        const incorrectHtml = data.session_results
            .filter(r => !r.is_correct)
            .map(r => `
                <div class="word-item incorrect">
                    <div class="verb-result-shown">📌 ${r.show_label}: <strong>${r.show}</strong></div>
                    <div class="verb-result-row ${r.f1_ok ? 'ok' : 'err'}">
                        Форма 1: <span class="user-answer">${r.user_form1 || '—'}</span>
                        ${!r.f1_ok ? `→ <span class="correct-answer">${r.form1}</span>` : '✓'}
                    </div>
                    <div class="verb-result-row ${r.f2_ok ? 'ok' : 'err'}">
                        Форма 2: <span class="user-answer">${r.user_form2 || '—'}</span>
                        ${!r.f2_ok ? `→ <span class="correct-answer">${r.form2}</span>` : '✓'}
                    </div>
                    <div class="verb-result-row ${r.f3_ok ? 'ok' : 'err'}">
                        Форма 3: <span class="user-answer">${r.user_form3 || '—'}</span>
                        ${!r.f3_ok ? `→ <span class="correct-answer">${r.form3}</span>` : '✓'}
                    </div>
                    ${r.shown_form_idx !== -1 && r.user_translation !== undefined ? `
                    <div class="verb-result-row ${r.tr_ok ? 'ok' : 'err'}">
                        Перевод: <span class="user-answer">${r.user_translation || '—'}</span>
                        ${!r.tr_ok ? `→ <span class="correct-answer">${r.translation}</span>` : '✓'}
                    </div>` : ''}
                </div>
            `).join('') || '<p>Все глаголы написаны верно! 🎉</p>';

        document.getElementById('verb-incorrect-list').innerHTML = incorrectHtml;

        const correctHtml = data.session_results
            .filter(r => r.is_correct)
            .map(r => `
                <div class="word-item correct">
                    <strong>${r.form1}</strong> – ${r.form2} – ${r.form3}
                    <span class="verb-translation-tag">${r.translation}</span>
                </div>
            `).join('') || '<p>Нет правильных ответов.</p>';

        document.getElementById('verb-correct-list').innerHTML = correctHtml;

        showVerbSection('verb-results-section');

    } catch (error) {
        console.error('Ошибка showVerbResults:', error);
        alert('Ошибка загрузки результатов: ' + error);
    }
}

async function retryVerbTraining() {
    try {
        await fetch('/api/verbs/reset_session', { method: 'POST' });
        await loadCurrentVerb();
        showVerbSection('verb-training-section');
    } catch (error) {
        alert('Ошибка: ' + error);
    }
}

function backToVerbSetup() {
    showVerbSection('verb-setup-section');
}

// =============================================
// Навигация по разделам глаголов
// =============================================

function showVerbSection(sectionId) {
    document.querySelectorAll('.verb-section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

// Enter в полях ввода глагола — переход вперёд или проверка
function handleVerbEnter(event) {
    if (event.key !== 'Enter') return;
    const inputs = Array.from(document.querySelectorAll('.verb-form-input:not([disabled])'))
        .filter(el => el.closest('.verb-input-row').style.display !== 'none');
    const idx = inputs.indexOf(event.target);
    if (idx >= 0 && idx < inputs.length - 1) {
        inputs[idx + 1].focus();
    } else {
        checkVerbAnswer();
    }
}
