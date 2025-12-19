document.addEventListener('DOMContentLoaded', function () {
    const sourceSelector = document.getElementById('source-lang');
    const targetSelector = document.getElementById('target-lang');
    const swapBtn = document.querySelector('.swap-langs-btn');
    const searchBtn = document.querySelector('.search-btn');

    // ===== если блоков с языками нет на странице — НИЧЕГО не инициализируем =====
    const hasLangSelectors = !!(sourceSelector && targetSelector);

    // ------------ работа с селекторами языков (если они есть) ------------
    if (hasLangSelectors) {
        initLangSelector(sourceSelector);
        initLangSelector(targetSelector);

        if (swapBtn) {
            swapBtn.addEventListener('click', function (e) {
                e.preventDefault();
                swapLanguages();
            });
        }
    }

    // функция инициализации одного селектора
    function initLangSelector(selector) {
        if (!selector) return;

        const current = selector.querySelector('.dict-lang-current');
        const dropdown = selector.querySelector('.dict-lang-dropdown');
        const selected = selector.querySelector('.dict-lang-selected');
        const items = selector.querySelectorAll('.dict-lang-item');

        // если чего-то не хватает в верстке — выходим, чтобы не падать
        if (!current || !dropdown || !selected || !items.length) {
            return;
        }

        current.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.dict-lang-dropdown').forEach(d => {
                if (d !== dropdown) d.style.display = 'none';
            });
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });

        items.forEach(item => {
            item.addEventListener('click', function () {
                const lang = this.getAttribute('data-lang');
                let otherLangText = null;

                if (selector === sourceSelector && targetSelector) {
                    const otherSelected = targetSelector.querySelector('.dict-lang-selected');
                    if (otherSelected) otherLangText = otherSelected.textContent;
                } else if (selector === targetSelector && sourceSelector) {
                    const otherSelected = sourceSelector.querySelector('.dict-lang-selected');
                    if (otherSelected) otherLangText = otherSelected.textContent;
                }

                // если языки совпадают — меняем местами (если есть оба селектора)
                if (hasLangSelectors && otherLangText && this.textContent === otherLangText) {
                    swapLanguages();
                } else {
                    selected.textContent = this.textContent;
                    selected.setAttribute('data-lang', lang);
                    dropdown.style.display = 'none';
                }
            });
        });
    }

    // поменять языки местами
    function swapLanguages() {
        if (!hasLangSelectors) return;

        const sourceSelected = sourceSelector.querySelector('.dict-lang-selected');
        const targetSelected = targetSelector.querySelector('.dict-lang-selected');

        if (!sourceSelected || !targetSelected) return;

        const tempText = sourceSelected.textContent;
        const tempLang = sourceSelected.getAttribute('data-lang');

        sourceSelected.textContent = targetSelected.textContent;
        sourceSelected.setAttribute('data-lang', targetSelected.getAttribute('data-lang'));

        targetSelected.textContent = tempText;
        targetSelected.setAttribute('data-lang', tempLang);

        document.querySelectorAll('.dict-lang-dropdown').forEach(d => {
            d.style.display = 'none';
        });
    }

    // ------------ кнопка поиска ------------
    if (searchBtn) {
        searchBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const queryInput = document.querySelector('.search-input');
            if (!queryInput) return;

            const query = queryInput.value.trim();

            // по умолчанию
            let sourceLang = 'ru';
            let targetLang = 'en';

            // если есть селекторы — берём реальные значения
            if (hasLangSelectors) {
                const sourceSelected = document.querySelector('#source-lang .dict-lang-selected');
                const targetSelected = document.querySelector('#target-lang .dict-lang-selected');
                if (sourceSelected) sourceLang = sourceSelected.getAttribute('data-lang') || sourceLang;
                if (targetSelected) targetLang = targetSelected.getAttribute('data-lang') || targetLang;
            }

            if (query) {
                window.location.href =
                    `/search/?query=${encodeURIComponent(query)}&source_lang=${sourceLang}&target_lang=${targetLang}`;
            }
        });
    }

    // закрытие всех dropdown при клике вне
    document.addEventListener('click', function () {
        document.querySelectorAll('.dict-lang-dropdown').forEach(d => {
            d.style.display = 'none';
        });
    });
});
