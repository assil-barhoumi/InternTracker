(function () {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        const saveBtn = form.querySelector('.btn-save');
        if (!saveBtn) return;
        saveBtn.disabled = true;
        const fields = Array.from(form.querySelectorAll('input, select, textarea'));

        fields.forEach(field => {
            field.addEventListener('input', () => {
                const changed = fields.some(f => f.defaultValue !== f.value);
                saveBtn.disabled = !changed;
            });
        });
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();