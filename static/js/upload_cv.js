document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('id_cv');
    const fileInfo = document.getElementById('file-info');
    const uploadArea = document.getElementById('uploadArea');
    const cvForm = document.getElementById('cvForm');
    const errorMessage = document.getElementById('error-message');
    let fileSelected = false;

    if (fileInput) {
        uploadArea.onclick = () => fileInput.click();

        fileInput.onchange = () => {
            if (fileInput.files.length > 0) {
                fileSelected = true;
                fileInfo.innerHTML = `<i class="fas fa-file-alt me-1"></i> ${fileInput.files[0].name}`;
                errorMessage.style.display = 'none';
            } else {
                fileSelected = false;
                fileInfo.innerHTML = '';
            }
        };

        cvForm.onsubmit = (e) => {
            if (!fileSelected && !fileInput.value) {
                e.preventDefault();
                errorMessage.style.display = 'block';
                return false;
            }
            return true;
        };

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt =>
            uploadArea.addEventListener(evt, e => e.preventDefault())
        );

        uploadArea.ondragover = () => uploadArea.style.borderColor = '#4e73df';
        uploadArea.ondragleave = () => uploadArea.style.borderColor = '#a0c4ff';

        uploadArea.ondrop = e => {
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                fileSelected = true;
                fileInfo.innerHTML = `<i class="fas fa-file-alt me-1"></i> ${e.dataTransfer.files[0].name}`;
                errorMessage.style.display = 'none';
                uploadArea.style.borderColor = '#a0c4ff';
            }
        };
    }
});