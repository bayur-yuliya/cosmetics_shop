document.addEventListener('DOMContentLoaded', function() {

    function setupTerms(checkboxId, buttonId) {
        const checkbox = document.getElementById(checkboxId);
        const button = document.getElementById(buttonId);

        if (checkbox && button) {
            checkbox.addEventListener('change', function() {
                button.disabled = !this.checked;
            });
        }
    }

    setupTerms('agreeTerms', 'registerButton');

    setupTerms('checkoutAgreeTerms', 'checkoutButton');
});