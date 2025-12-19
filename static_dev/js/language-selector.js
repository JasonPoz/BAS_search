document.addEventListener('DOMContentLoaded', function() {
    const selectedLanguage = document.querySelector('.selected-language');
    const languageOptions = document.querySelector('.language-options');

    if (selectedLanguage && languageOptions) {
        selectedLanguage.addEventListener('click', function() {
            languageOptions.style.display = languageOptions.style.display === 'block' ? 'none' : 'block';
        });

        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', function() {
                selectedLanguage.textContent = this.textContent;
                languageOptions.style.display = 'none';
                // Здесь можно добавить AJAX запрос для смены языка
                console.log('Selected language:', this.dataset.value);
            });
        });

        // Закрывать при клике вне элемента
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.language-selector')) {
                languageOptions.style.display = 'none';
            }
        });
    }
});