document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // ELEMENTS
    // =========================================

    const currentMonthLabel =
        document.getElementById("currentMonth");

    const dayHeaderRow =
        document.getElementById("dayHeaderRow");

    const calendarBody =
        document.getElementById("calendarBody");

    const previousBtn =
        document.getElementById("previousBtn");

    const nextBtn =
        document.getElementById("nextBtn");

    const todayBtn =
        document.getElementById("todayBtn");

    const newMeetingBtn =
        document.getElementById("newMeetingBtn");

    const meetingModal =
        document.getElementById("meetingModal");

    const closeModalBtn =
        document.getElementById("closeModalBtn");

    const cancelMeetingBtn =
        document.getElementById("cancelMeetingBtn");

    const meetingForm =
        document.getElementById("meetingForm");

    const calendarView =
        document.getElementById("calendarView");


    // =========================================
    // CURRENT DATE
    // =========================================

    let currentDate = new Date();

    let currentView = "week";


    // =========================================
    // CONSTANTS
    // =========================================

    const START_HOUR = 9;

    const END_HOUR = 18;

    const HOUR_HEIGHT = 91;


    // =========================================
    // HELPERS
    // =========================================

    function getMonday(date) {

        const d = new Date(date);

        const day = d.getDay();

        const difference =
            day === 0 ? -6 : 1 - day;

        d.setDate(
            d.getDate() + difference
        );

        d.setHours(0, 0, 0, 0);

        return d;
    }


    function formatMonth(date) {

        return date.toLocaleDateString(
            "en-US",
            {
                month: "long",
                year: "numeric"
            }
        );

    }


    function formatTime(date) {

        return date.toLocaleTimeString(
            "en-US",
            {
                hour: "numeric",
                minute: "2-digit"
            }
        );

    }


    function sameDate(date1, date2) {

        return (
            date1.getFullYear() === date2.getFullYear() &&
            date1.getMonth() === date2.getMonth() &&
            date1.getDate() === date2.getDate()
        );

    }


    // =========================================
    // RENDER CALENDAR
    // =========================================

    function renderCalendar() {

        if (currentView === "day") {

            renderDay();

        } else {

            renderWeek();

        }

    }


    // =========================================
    // WEEK VIEW
    // =========================================

    function renderWeek() {

        const monday =
            getMonday(currentDate);

        currentMonthLabel.textContent =
            formatMonth(monday);


        dayHeaderRow.innerHTML = "";

        calendarBody.innerHTML = "";


        dayHeaderRow.style.gridTemplateColumns =
            "repeat(5, 1fr)";

        calendarBody.style.gridTemplateColumns =
            "repeat(5, 1fr)";


        for (let i = 0; i < 5; i++) {

            const date =
                new Date(monday);

            date.setDate(
                monday.getDate() + i
            );


            // HEADER

            const header =
                document.createElement("div");

            header.className =
                "day-header";


            const dayNumber =
                document.createElement("div");

            dayNumber.className =
                "day-number";

            dayNumber.textContent =
                String(date.getDate()).padStart(2, "0");


            const dayName =
                document.createElement("div");

            dayName.className =
                "day-name";

            dayName.textContent =
                date.toLocaleDateString(
                    "en-US",
                    {
                        weekday: "long"
                    }
                );


            header.appendChild(dayNumber);

            header.appendChild(dayName);

            dayHeaderRow.appendChild(header);


            // DAY COLUMN

            const column =
                document.createElement("div");

            column.className =
                "day-column";


            for (
                let hour = START_HOUR;
                hour < END_HOUR;
                hour++
            ) {

                const cell =
                    document.createElement("div");

                cell.className =
                    "hour-cell";

                column.appendChild(cell);

            }


            calendarBody.appendChild(column);


            renderEvents(
                column,
                date
            );

        }

    }


    // =========================================
    // DAY VIEW
    // =========================================

    function renderDay() {

        currentMonthLabel.textContent =
            formatMonth(currentDate);


        dayHeaderRow.innerHTML = "";

        calendarBody.innerHTML = "";


        dayHeaderRow.style.gridTemplateColumns =
            "1fr";

        calendarBody.style.gridTemplateColumns =
            "1fr";


        const header =
            document.createElement("div");

        header.className =
            "day-header";


        header.innerHTML = `
            <div class="day-number">
                ${String(currentDate.getDate()).padStart(2, "0")}
            </div>

            <div class="day-name">
                ${currentDate.toLocaleDateString(
                    "en-US",
                    { weekday: "long" }
                )}
            </div>
        `;


        dayHeaderRow.appendChild(header);


        const column =
            document.createElement("div");

        column.className =
            "day-column";


        for (
            let hour = START_HOUR;
            hour < END_HOUR;
            hour++
        ) {

            const cell =
                document.createElement("div");

            cell.className =
                "hour-cell";

            column.appendChild(cell);

        }


        calendarBody.appendChild(column);


        renderEvents(
            column,
            currentDate
        );

    }


    // =========================================
    // EVENTS
    // =========================================

    function renderEvents(
        column,
        date
    ) {

        meetings.forEach(function (meeting) {

            const start =
                new Date(meeting.start);

            const end =
                new Date(meeting.end);


            if (!sameDate(start, date)) {
                return;
            }


            const startMinutes =
                start.getHours() * 60 +
                start.getMinutes();


            const endMinutes =
                end.getHours() * 60 +
                end.getMinutes();


            const calendarStart =
                START_HOUR * 60;


            const top =
                (
                    startMinutes -
                    calendarStart
                ) / 60 * HOUR_HEIGHT;


            const duration =
                Math.max(
                    30,
                    endMinutes - startMinutes
                );


            const height =
                duration / 60 * HOUR_HEIGHT;


            const event =
                document.createElement("div");

            event.className =
                "calendar-event";


            event.style.top =
                `${top}px`;

            event.style.height =
                `${height}px`;


            event.innerHTML = `
                <div class="event-title">
                    ${escapeHtml(meeting.title)}
                </div>

                <div class="event-time">
                    ${formatTime(start)}
                    -
                    ${formatTime(end)}
                </div>
            `;


            event.addEventListener(
                "click",
                function () {

                    openMeeting(meeting);

                }
            );


            column.appendChild(event);

        });

    }


    // =========================================
    // OPEN MEETING
    // =========================================

    function openMeeting(meeting) {

        const message =
            `
Meeting: ${meeting.title}

Group: ${meeting.group}

Venue: ${meeting.venue}

Start:
${new Date(meeting.start).toLocaleString()}

End:
${new Date(meeting.end).toLocaleString()}
            `;


        const openChat =
            confirm(
                message +
                "\n\nOpen meeting chat?"
            );


        if (openChat) {

            window.location.href =
                `/teamchat/meeting/${meeting.id}/`;

        }

    }


    // =========================================
    // ESCAPE HTML
    // =========================================

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent =
            value;

        return div.innerHTML;

    }


    // =========================================
    // NAVIGATION
    // =========================================

    previousBtn.addEventListener(
        "click",
        function () {

            if (currentView === "day") {

                currentDate.setDate(
                    currentDate.getDate() - 1
                );

            } else {

                currentDate.setDate(
                    currentDate.getDate() - 7
                );

            }

            renderCalendar();

        }
    );


    nextBtn.addEventListener(
        "click",
        function () {

            if (currentView === "day") {

                currentDate.setDate(
                    currentDate.getDate() + 1
                );

            } else {

                currentDate.setDate(
                    currentDate.getDate() + 7
                );

            }

            renderCalendar();

        }
    );


    todayBtn.addEventListener(
        "click",
        function () {

            currentDate =
                new Date();

            renderCalendar();

        }
    );


    // =========================================
    // VIEW CHANGE
    // =========================================

    calendarView.addEventListener(
        "change",
        function () {

            currentView =
                this.value;

            renderCalendar();

        }
    );


    // =========================================
    // MODAL
    // =========================================

    function openModal() {

        meetingModal.hidden =
            false;

    }


    function closeModal() {

        meetingModal.hidden =
            true;

    }


    newMeetingBtn.addEventListener(
        "click",
        openModal
    );


    closeModalBtn.addEventListener(
        "click",
        closeModal
    );


    cancelMeetingBtn.addEventListener(
        "click",
        closeModal
    );


    meetingModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                meetingModal
            ) {

                closeModal();

            }

        }
    );


    // =========================================
    // CREATE MEETING
    // =========================================

    meetingForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const formData =
                new FormData(meetingForm);


            try {

                const response =
                    await fetch(
                        "{% url 'teamchat:create_meeting' %}",
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCookie("csrftoken")
                            },

                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!data.success) {

                    alert(
                        data.error ||
                        "Unable to create meeting."
                    );

                    return;

                }


                closeModal();


                window.location.reload();

            }

            catch (error) {

                console.error(error);

                alert(
                    "Something went wrong."
                );

            }

        }
    );


    // =========================================
    // CSRF
    // =========================================

    function getCookie(name) {

        let cookieValue = null;


        if (document.cookie) {

            const cookies =
                document.cookie.split(";");


            for (
                let cookie of cookies
            ) {

                cookie =
                    cookie.trim();


                if (
                    cookie.startsWith(
                        name + "="
                    )
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }


        return cookieValue;

    }


    // =========================================
    // INITIALIZE
    // =========================================

    renderCalendar();

});