document.addEventListener("DOMContentLoaded", function () {

    // -----------------------------
    // Date Filter
    // -----------------------------
    const datePicker = document.getElementById("sortDatePicker");
    const resetBtn = document.getElementById("resetBtn");

    if (datePicker) {

        datePicker.addEventListener("change", function () {

            const selectedDate = this.value;
            const rows = document.querySelectorAll(".worklog-table tbody tr");

            rows.forEach(function (row) {

                const rowDate = row.dataset.date;

                if (!selectedDate || rowDate === selectedDate) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    }

    // -----------------------------
    // Reset Filter
    // -----------------------------
    if (resetBtn) {

        resetBtn.addEventListener("click", function () {

            if (datePicker) {
                datePicker.value = "";
            }

            document.querySelectorAll(".worklog-table tbody tr").forEach(function (row) {
                row.style.display = "";
            });

        });

    }

    // -----------------------------
    // Delete Confirmation
    // -----------------------------
    document.querySelectorAll(".reject-btn").forEach(function (button) {

        button.addEventListener("click", function (e) {

            if (!confirm("Reject this timesheet?")) {
                e.preventDefault();
            }

        });

    });

    document.querySelectorAll(".approve-btn").forEach(function (button) {

        button.addEventListener("click", function (e) {

            if (!confirm("Approve this timesheet?")) {
                e.preventDefault();
            }

        });

    });

});