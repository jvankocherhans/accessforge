document.addEventListener('DOMContentLoaded', () => {
  const confirmForms = document.querySelectorAll('form.confirm-form');
  const modal = document.getElementById('deleteModal');
  const confirmBtn = modal.querySelector('.confirm-btn');
  const cancelBtn = modal.querySelector('.cancel-btn');

  let targetForm = null;

  confirmForms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
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
