document.addEventListener('DOMContentLoaded', function() {
    var accountTypeSelect = document.getElementById('type');
    var percentageBlock = document.getElementById('percentage_block');
    var dueDateBlock = document.getElementById('due_date_block');

    accountTypeSelect.addEventListener('change', function() {
        var selectedValue = accountTypeSelect.value;

        if (selectedValue === 'Savings Account') {
            percentageBlock.style.display = 'block';
            dueDateBlock.style.display = 'none';
        } else if (selectedValue === 'Credit Card') {
            dueDateBlock.style.display = 'block';
            percentageBlock.style.display = 'block';
        } else {
            percentageBlock.style.display = 'none';
            dueDateBlock.style.display = 'none';
        }
    });
});