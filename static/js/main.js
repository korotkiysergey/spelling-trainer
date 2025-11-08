// Глобальные переменные
let currentMode = 'ru_only';
let isPlaying = false;
let selectedSource = 'database';
let selectedCategories = [];
let selectedLetters = [];
let allCategories = [];
let currentWordsCount = 0;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    selectSource('database');
    loadAllCategories();
});

// Выбор источника слов (база данных или ручной ввод)
function selectSource(source) {
    selectedSource = source;

    const dbBtn = document.getElementById('db-source-btn');
    const manualBtn = document.getElementById('manual-source-btn');
    const dbSelection = document.getElementById('database-selection');
    const manualInput = document.getElementById('manual-input');

    if (source === 'database') {
        dbBtn.className = 'btn btn-primary';
        manualBtn.className = 'btn btn-secondary';
        dbSelection.style.display = 'block';
        manualInput.style.display = 'none';
    } else {
        dbBtn.className = 'btn btn-secondary';
        manualBtn.className = 'btn btn-primary';
        dbSelection.style.display = 'none';
        manualInput.style.display = 'block';
    }
}

// Загрузка всех категорий из БД
async function loadAllCategories() {
    try {
        const response = await fetch('/api/get_categories');
        const data = await response.json();

        if (data.success) {
            allCategories = data.categories;
            filterAndDisplayCategories();
        }
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
    }
}

// Фильтрация и отображение категорий в зависимости от режима
function filterAndDisplayCategories() {
    const container = document.getElementById('categories-container');

    let filteredCategories;
    if (currentMode === 'ru_only') {
        // Только словарные слова (классы)
        filteredCategories = allCategories.filter(cat => cat.type === 'class');
    } else {
        // Уроки и темы (с переводами)
        filteredCategories = allCategories.filter(cat => cat.type === 'lesson' || cat.type === 'topic');
    }

    if (filteredCategories.length === 0) {
        container.innerHTML = '<p style="padding: 20px; text-align: center; color: #6c757d;">Нет доступных категорий для выбранного режима</p>';
        return;
    }

    container.innerHTML = filteredCategories.map(cat => `
        <div class="option-card" onclick="toggleCategory(${cat.id}, this)">
            <input type="checkbox" id="cat-${cat.id}" onchange="event.stopPropagation(); toggleCategory(${cat.id}, this.parentElement)">
            <label for="cat-${cat.id}" onclick="event.stopPropagation()">
                ${cat.name}
                ${cat.description ? `<br><small>${cat.description}</small>` : ''}
            </label>
        </div>
    `).join('');

    // Сбрасываем выбранные категории
    selectedCategories = [];
    updateSelectedCount();
}

// Загрузка букв для выбранной категории
async function loadLetters(categoryId = null) {
    try {
        const url = categoryId ? `/api/get_letters?category_id=${categoryId}` : '/api/get_letters';
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            const container = document.getElementById('letters-container');
            const lettersWithWords = data.letters.filter(letter => letter.count > 0);

            if (lettersWithWords.length === 0) {
                container.innerHTML = '<p style="padding: 10px; text-align: center; color: #6c757d;">Нет слов в выбранных категориях</p>';
                return;
            }

            container.innerHTML = lettersWithWords.map(letter => `
                <div class="letter-card" onclick="toggleLetter(${letter.id}, this)" data-count="${letter.count}">
                    ${letter.letter}
                    <span class="count">(${letter.count})</span>
                </div>
            `).join('');

            // Сбрасываем выбранные буквы
            selectedLetters = [];
            updateSelectedCount();
        }
    } catch (error) {
        console.error('Ошибка загрузки букв:', error);
    }
}

// Переключение выбора категории
function toggleCategory(categoryId, element) {
    const checkbox = element.querySelector('input[type="checkbox"]');
    checkbox.checked = !checkbox.checked;
    element.classList.toggle('selected');

    if (checkbox.checked) {
        selectedCategories.push(categoryId);
    } else {
        selectedCategories = selectedCategories.filter(id => id !== categoryId);
    }

    // Показываем/скрываем секцию с буквами в зависимости от режима
    const lettersSection = document.getElementById('letters-section');
    if (currentMode === 'ru_only' && selectedCategories.length > 0) {
        lettersSection.style.display = 'block';
        loadLetters(selectedCategories[0]);
    } else {
        lettersSection.style.display = 'none';
        selectedLetters = [];
    }

    updateSelectedCount();
}

// Переключение выбора буквы
function toggleLetter(letterId, element) {
    element.classList.toggle('selected');

    if (element.classList.contains('selected')) {
        selectedLetters.push(letterId);
    } else {
        selectedLetters = selectedLetters.filter(id => id !== letterId);
    }

    updateSelectedCount();
}

// Выбрать все буквы
function selectAllLetters() {
    const letterCards = document.querySelectorAll('.letter-card');
    selectedLetters = [];
    letterCards.forEach(card => {
        card.classList.add('selected');
        const onClick = card.getAttribute('onclick');
        const letterId = parseInt(onClick.match(/\d+/)[0]);
        selectedLetters.push(letterId);
    });
    updateSelectedCount();
}

// Снять выбор всех букв
function deselectAllLetters() {
    const letterCards = document.querySelectorAll('.letter-card');
    letterCards.forEach(card => card.classList.remove('selected'));
    selectedLetters = [];
    updateSelectedCount();
}

// Обновление счетчика выбранных слов
async function updateSelectedCount() {
    try {
        if (selectedCategories.length === 0) {
            document.getElementById('selected-count').textContent = '0';
            return;
        }

        if (currentMode === 'ru_only') {
            if (selectedLetters.length === 0) {
                document.getElementById('selected-count').textContent = '0';
                return;
            }

            // Подсчитываем сумму слов из выбранных букв
            let total = 0;
            const letterCards = document.querySelectorAll('.letter-card.selected');
            letterCards.forEach(card => {
                const count = parseInt(card.getAttribute('data-count'));
                total += count;
            });
            document.getElementById('selected-count').textContent = total;
        } else {
            // Для режимов с переводом - запрашиваем количество
            const response = await fetch('/api/count_words', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category_ids: selectedCategories,
                    mode: currentMode
                })
            });

            const data = await response.json();
            if (data.success) {
                document.getElementById('selected-count').textContent = data.count;
                currentWordsCount = data.count;
            }
        }
    } catch (error) {
        console.error('Ошибка подсчета слов:', error);
        document.getElementById('selected-count').textContent = '?';
    }
}

// Выбор режима тренировки
function selectMode(mode, element) {
    currentMode = mode;
    document.querySelectorAll('.mode-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    element.classList.add('selected');

    const radioId = 'mode-' + mode.replace(/_/g, '-');
    const radioElement = document.getElementById(radioId);
    if (radioElement) {
        radioElement.checked = true;
    }

    // Обновляем инструкцию для ручного ввода
    const instruction = document.getElementById('instruction-text');
    const textarea = document.getElementById('words-textarea');

    if (mode === 'ru_only') {
        instruction.innerHTML = '<strong>Инструкция:</strong> Введите русские слова (по одному на строку). Система озвучит каждое слово, а вы должны правильно написать его.';
        textarea.placeholder = 'вокзал\nпарашют\nаккомпанемент\nбюллетень\nдеревня';
        if (!textarea.value.trim() || textarea.value.includes('-')) {
            textarea.value = 'вокзал\nпарашют\nаккомпанемент\nбюллетень\nдеревня\nинтеллигент\nпрофессия\nколлектив\nтерритория\nдискуссия';
        }
    } else if (mode === 'ru_to_en') {
        instruction.innerHTML = '<strong>Инструкция:</strong> Введите пары слов в формате: <code>русское слово - английское слово</code> (каждая пара на новой строке). Система озвучит русское слово, а вы должны написать его перевод на английском.';
        textarea.placeholder = 'вокзал - station\nпарашют - parachute\nаккомпанемент - accompaniment';
        if (!textarea.value.includes('-') || textarea.value.split('\n')[0].split('-').length === 1) {
            textarea.value = 'вокзал - station\nпарашют - parachute\nаккомпанемент - accompaniment\nбюллетень - bulletin\nдеревня - village\nинтеллигент - intellectual\nпрофессия - profession\nколлектив - collective\nтерритория - territory\nдискуссия - discussion';
        }
    } else {
        instruction.innerHTML = '<strong>Инструкция:</strong> Введите пары слов в формате: <code>русское слово - английское слово</code> (каждая пара на новой строке). Система озвучит английское слово, а вы должны написать его перевод на русском.';
        textarea.placeholder = 'вокзал - station\nпарашют - parachute\nаккомпанемент - accompaniment';
        if (!textarea.value.includes('-') || textarea.value.split('\n')[0].split('-').length === 1) {
            textarea.value = 'вокзал - station\nпарашют - parachute\nаккомпанемент - accompaniment\nбюллетень - bulletin\nдеревня - village\nинтеллигент - intellectual\nпрофессия - profession\nколлектив - collective\nтерритория - territory\nдискуссия - discussion';
        }
    }

    // Обновляем категории в зависимости от режима
    if (selectedSource === 'database') {
        filterAndDisplayCategories();

        const lettersSection = document.getElementById('letters-section');
        if (mode === 'ru_only') {
            lettersSection.style.display = selectedCategories.length > 0 ? 'block' : 'none';
        } else {
            lettersSection.style.display = 'none';
            selectedLetters = [];
        }

        updateSelectedCount();
    }
}

// Показать секцию
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
}

// Обработка Enter в поле ввода
function handleEnter(event) {
    if (event.key === 'Enter') {
        checkAnswer();
    }
}

// Фокус на поле ввода при показе секции тренировки
const observer = new MutationObserver(() => {
    if (document.getElementById('training-section').classList.contains('active')) {
        document.getElementById('answer-input').focus();
    }
});

observer.observe(document.getElementById('training-section'), {
    attributes: true,
    attributeFilter: ['class']
});