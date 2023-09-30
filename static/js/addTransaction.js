const radioButtons = document.getElementsByName("option");
const forms = document.querySelectorAll(".form");

for (let i = 0; i < radioButtons.length; i++) {
    radioButtons[i].addEventListener("change", function() {
        for (let j = 0; j < forms.length; j++) {
            if (forms[j].id === "form" + (i + 1)) {
                forms[j].style.display = "block";
            } else {
                forms[j].style.display = "none";
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var giftCardCheckbox = document.getElementById('giftCardCheckbox');
    var paymentMethodWrapper = document.getElementById('payment_method_wrapper');
    var paymentMethodSelect = document.getElementById('payment_method');
    var gcPaymentMethodWrapper = document.getElementById('gc_payment_method_wrapper');
    var gcPaymentMethodSelect = document.getElementById('gc_payment_method');

    // Find the option with the value 'Gift Card Used'
    var selectedOption = [...paymentMethodSelect.options].find(option => option.value === '');


    giftCardCheckbox.addEventListener('change', function() {
        if (this.checked) {
            // Checkbox is checked
            paymentMethodSelect.value = 'Gift Card Used'; // Set Payment Method to 'Gift Card Used'
            paymentMethodWrapper.style.display = 'none'; // Hide Payment Method field
            gcPaymentMethodWrapper.style.display = 'block'; // Unhide Gift Card Payment Method field
            gcPaymentMethodSelect.required = true; // Make Gift Card Payment Method required
            paymentMethodSelect.required = false; // Make Payment Method not required
        } else {
            // Checkbox is not checked
            paymentMethodSelect.value = 'Payment Method'; // Set Payment Method to 'Gift Card Used'
            paymentMethodWrapper.style.display = 'block'; // Show Payment Method field
            gcPaymentMethodWrapper.style.display = 'none'; // Hide Gift Card Payment Method field
            gcPaymentMethodSelect.required = false; // Make Gift Card Payment Method not required
            paymentMethodSelect.required = true; // Make Payment Method required
        }
    });
});