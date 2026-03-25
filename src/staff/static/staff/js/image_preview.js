const imageInput = document.getElementById(imagePreviewConfig.inputId);
const previewImage = document.getElementById(imagePreviewConfig.previewId);

if (imageInput) {
    imageInput.addEventListener('change', function () {
        const file = this.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = function () {
                previewImage.src = this.result;
            };

            reader.readAsDataURL(file);
        } else {
            previewImage.src = imagePreviewConfig.placeholder;
        }
    });
}