document.addEventListener('DOMContentLoaded', function() {
  const passwordInput = document.getElementById('id_password1');
  const passwordConfirm = document.getElementById('id_password2');
  
  if (passwordInput && passwordConfirm) {
    // Обработчики ввода (без синхронизации)
    passwordInput.addEventListener('input', function() {
      validatePasswordRequirements(this);
      validatePasswordMatch();
    });
    
    passwordConfirm.addEventListener('input', function() {
      validatePasswordMatch();
    });
    
    // Инициализация при загрузке
    validatePasswordRequirements(passwordInput);
    validatePasswordMatch();
  }

  // Проверка требований к паролю
  function validatePasswordRequirements(inputElement) {
    const value = inputElement.value;
    const form = inputElement.closest('form');
    const requirements = form.querySelectorAll('.password-requirements .requirement');
    
    if (requirements.length >= 5) {
      const checks = {
        length: value.length >= 8,
        special: /[^A-Za-z0-9]/.test(value),
        numbers: /[0-9]/.test(value),
        upperLower: /[A-Z]/.test(value) && /[a-z]/.test(value)
      };
      
      // Обновляем иконки для первых 4 требований
      requirements[0].classList.toggle('valid', checks.length);
      requirements[1].classList.toggle('valid', checks.special);
      requirements[2].classList.toggle('valid', checks.numbers);
      requirements[3].classList.toggle('valid', checks.upperLower);
    }
  }

  // Проверка совпадения паролей
  function validatePasswordMatch() {
    const password1 = passwordInput.value;
    const password2 = passwordConfirm.value;
    const form = passwordInput.closest('form');
    const matchRequirement = form.querySelector('.password-requirements .requirement:nth-child(5)');
    
    if (matchRequirement) {
      const isValid = password1 && password2 && password1 === password2;
      matchRequirement.classList.toggle('valid', isValid);
    }
  }
});