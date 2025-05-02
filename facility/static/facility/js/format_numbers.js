document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type="text"]:not(.vTextField)').forEach(function (input) {
        input.addEventListener('input', function (e) {
            let raw = input.value.replace(/[^0-9]/g, '');  // remove non-numeric
            if (raw !== '') {
                input.value = Number(raw).toLocaleString();
            } else {
                input.value = '';
            }
        });

        // Optional: on submit, remove commas so Django can parse the number
        input.form?.addEventListener('submit', function () {
            input.value = input.value.replace(/,/g, '');
        });
    });
});