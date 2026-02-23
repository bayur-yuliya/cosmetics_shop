const imageInput = document.getElementById('{{ form.image.id_for_label }}');
const previewImage = document.getElementById('previewImage');

imageInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.addEventListener("load", function() {
            previewImage.setAttribute("src", this.result);
        });
        reader.readAsDataURL(file);
    } else {
        previewImage.setAttribute("src", "{% static 'staff/img/placeholder.png' %}");
    }
});