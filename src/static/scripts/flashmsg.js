document.addEventListener('DOMContentLoaded', function () {
  const closeButtons = document.querySelectorAll('.btn-close');

  closeButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      const alertContainer = button.closest('.alert-container');
      alertContainer.style.display = 'none';
    });
  });
});
