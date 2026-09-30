document.querySelectorAll('[data-captcha]').forEach((widget) => {
  const button = widget.querySelector('[data-captcha-refresh]');
  const image = widget.querySelector('[data-captcha-image]');
  const key = widget.querySelector('input[type="hidden"]');
  const answer = widget.querySelector('input[type="text"]');
  const status = widget.querySelector('[data-captcha-status]');
  button.addEventListener('click', async () => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    button.disabled = true;
    widget.setAttribute('aria-busy', 'true');
    status.textContent = 'Обновляем код…';
    status.classList.remove('is-error');
    try {
      const response = await fetch(widget.dataset.refreshUrl, {
        credentials: 'same-origin', cache: 'no-store', signal: controller.signal,
        headers: {'X-Requested-With': 'XMLHttpRequest'},
      });
      if (!response.ok) throw new Error('Unable to refresh CAPTCHA');
      const challenge = await response.json();
      const imageUrl = new URL(challenge.image_url, location.origin);
      if (imageUrl.origin !== location.origin || !challenge.key) throw new Error('Invalid CAPTCHA response');
      const nextImage = new Image();
      await new Promise((resolve, reject) => {
        nextImage.onload = resolve;
        nextImage.onerror = reject;
        controller.signal.addEventListener('abort', reject, {once: true});
        nextImage.src = imageUrl.href;
      });
      key.value = challenge.key;
      image.src = imageUrl.href;
      answer.value = '';
      answer.focus();
      status.textContent = 'Новый код готов. Данные заявки сохранены.';
    } catch (error) {
      status.textContent = 'Не удалось обновить код. Проверьте соединение и попробуйте ещё раз.';
      status.classList.add('is-error');
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
      widget.removeAttribute('aria-busy');
    }
  });
});

document.querySelectorAll('[data-password-toggle]').forEach((button) => {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.passwordToggle);
    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';
    button.textContent = visible ? 'Скрыть' : 'Показать';
    button.setAttribute('aria-pressed', String(visible));
  });
});

if (window.jQuery) {
  jQuery(() => {
    if (jQuery.fn.autocomplete) jQuery('#id_school').autocomplete({source: '/autocomplete/', minLength: 2});
    if (jQuery.fn.mask) {
      jQuery('#id_SNILS').mask('000-000-000 00');
      jQuery('#id_INN').mask('000000000000');
      jQuery('#id_passport_number').mask('00 00 000000');
      jQuery('#id_phone, #id_mother_phone, #id_father_phone').mask('+7(000)000-00-00');
    }
  });
}
