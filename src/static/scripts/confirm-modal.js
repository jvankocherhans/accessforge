document.addEventListener('DOMContentLoaded', () => {
  const confirmForms = document.querySelectorAll('form.confirm-form');
  const modal = document.getElementById('confirmModal');
  const titleEl = modal.querySelector('#modal-title');
  const textEl = modal.querySelector('#modal-text');
  const confirmBtn = modal.querySelector('.confirm-btn');
  const cancelBtn = modal.querySelector('.cancel-btn');

  let targetForm = null;

  confirmForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      // Titel und Text dynamisch auslesen
      const title = form.dataset.title || 'Are you sure?';
      const text = form.dataset.text || 'Do you want to proceed?';
      titleEl.textContent = title;
      textEl.textContent = text;

      targetForm = form;
      modal.classList.remove('hidden');
    });
  });

  confirmBtn.addEventListener('click', () => {
    if (targetForm) {
      modal.classList.add('hidden');
      targetForm.submit();
    }
  });

  cancelBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    targetForm = null;
  });
});
