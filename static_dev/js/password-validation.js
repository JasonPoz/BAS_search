document.addEventListener('DOMContentLoaded', function() {
  // Находим поля паролей
  const passwordInput = document.querySelector('input[type="password"][name="new_password1"]');
  const passwordConfirm = document.querySelector('input[type="password"][name="new_password2"]');
  
  if (passwordInput && passwordConfirm) {
    // Флаг для предотвращения бесконечного цикла
    let isSyncing = false;
    
    // Обработчик для первого поля
    passwordInput.addEventListener('input', function() {
      if (isSyncing) return;
      
      isSyncing = true;
      validatePassword.call(this);
      validatePasswordMatch();
      isSyncing = false;
    });
    
    // Обработчик для второго поля
    passwordConfirm.addEventListener('input', function() {
      if (isSyncing) return;
      
      isSyncing = true;
      validatePasswordMatch();
      isSyncing = false;
    });
    
    // Инициализация при загрузке
    validatePassword.call(passwordInput);
    validatePasswordMatch();
  }

  // Проверка требований к паролю
  function validatePassword() {
    const value = this.value;
    const form = this.closest('form');
    const requirements = form.querySelectorAll('.requirement');
    
    if (requirements.length >= 4) {
      const checks = {
        length: value.length >= 8,
        special: /[^A-Za-z0-9]/.test(value),
        numbers: /[0-9]/.test(value),
        upperLower: /[A-Z]/.test(value) && /[a-z]/.test(value)
      };
      
      requirements[0].classList.toggle('valid', checks.length);
      requirements[0].classList.toggle('invalid', !checks.length);
      
      requirements[1].classList.toggle('valid', checks.special);
      requirements[1].classList.toggle('invalid', !checks.special);
      
      requirements[2].classList.toggle('valid', checks.numbers);
      requirements[2].classList.toggle('invalid', !checks.numbers);
      
      requirements[3].classList.toggle('valid', checks.upperLower);
      requirements[3].classList.toggle('invalid', !checks.upperLower);
    }
  }

  // Проверка совпадения паролей
  function validatePasswordMatch() {
    if (!passwordInput || !passwordConfirm) return;
    
    const password1 = passwordInput.value;
    const password2 = passwordConfirm.value;
    const form = passwordInput.closest('form');
    const matchIndicator = form.querySelector('.requirement:nth-child(5)') || 
                          form.querySelector('.password-match');
    
    if (matchIndicator) {
      const isValid = password1 && password2 && password1 === password2;
      matchIndicator.classList.toggle('valid', isValid);
      matchIndicator.classList.toggle('invalid', !isValid);
    }
  }
});