(function () {
    const config = window.APP_SETTINGS_CONFIG || {};
    const savedSettings = config.initialSettings || {};
    const historyRows = config.historyRows || [];
    const sessionsData = config.sessions || [];

    function getCookie(name) {
        const match = document.cookie.match(
            new RegExp("(^| )" + name + "=([^;]+)")
        );

        return match ? decodeURIComponent(match[2]) : "";
    }

    function showMessage(text, isError = false) {
        const messageBox = document.getElementById("settings-message");

        if (!messageBox) {
            return;
        }

        messageBox.textContent = text;
        messageBox.classList.toggle("error", isError);
        messageBox.classList.remove("hidden");

        window.setTimeout(function () {
            messageBox.classList.add("hidden");
        }, 3500);
    }

    async function saveSettings(payload) {
        const response = await fetch(config.saveUrl, {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },

            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Could not save settings.");
        }

        return data;
    }

    function applyGlobalAppearance(theme, fontSize, highContrast) {

        const selectedTheme = theme || "light";
        const selectedFontSize = Number(fontSize) || 16;


        // Apply theme immediately
        document.documentElement.setAttribute(
            "data-theme",
            selectedTheme
        );


        // Also apply class for CSS compatibility
        document.body.classList.remove(
            "light-theme",
            "dark-theme"
        );


        if (selectedTheme === "dark") {

            document.body.classList.add(
                "dark-theme"
            );

        } 
        else if (selectedTheme === "light") {

            document.body.classList.add(
                "light-theme"
            );

        }
        else {

            if (
                window.matchMedia(
                    "(prefers-color-scheme: dark)"
                ).matches
            ) {

                document.body.classList.add(
                    "dark-theme"
                );

            }
            else {

                document.body.classList.add(
                    "light-theme"
                );

            }

        }


        // Font size
        document.documentElement.style.fontSize =
            selectedFontSize + "px";


        // High contrast
        document.documentElement.classList.toggle(
            "high-contrast",
            Boolean(highContrast)
        );


        // Save immediately for instant reload
        localStorage.setItem(
            "selectedTheme",
            selectedTheme
        );
    }

    function renderHistory() {
        const historyBody = document.getElementById("history-body");

        if (!historyBody) {
            return;
        }

        historyBody.innerHTML = "";

        if (!historyRows.length) {
            historyBody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center;">
                        No login history found.
                    </td>
                </tr>
            `;

            return;
        }

        historyRows.forEach(function (history) {
            const row = document.createElement("tr");

            const dateTimeCell = document.createElement("td");
            dateTimeCell.textContent = history.datetime || "--";

            const deviceCell = document.createElement("td");
            deviceCell.textContent = history.device || "Unknown Device";

            const locationCell = document.createElement("td");
            locationCell.textContent = history.location || "Unknown";

            const ipCell = document.createElement("td");
            ipCell.textContent = history.ip || "--";

            row.appendChild(dateTimeCell);
            row.appendChild(deviceCell);
            row.appendChild(locationCell);
            row.appendChild(ipCell);

            historyBody.appendChild(row);
        });
    }

    function renderSessions() {
        const sessionsList = document.getElementById("sessions-list");

        if (!sessionsList) {
            return;
        }

        sessionsList.innerHTML = "";

        if (!sessionsData.length) {
            sessionsList.innerHTML = "<li>No active sessions found.</li>";
            return;
        }

        sessionsData.forEach(function (session) {
            const listItem = document.createElement("li");

            const device = session.device || "Unknown Device";
            const location = session.location || "Unknown";
            const time = session.time || "--";
            const ip = session.ip || "--";

            listItem.innerHTML = `
                <div>
                    <strong>${device}${session.current ? " (Current)" : ""}</strong>
                    <div class="muted">
                        ${location} • ${time}<br>
                        IP: ${ip}
                    </div>
                </div>
            `;

            sessionsList.appendChild(listItem);
        });
    }

    function applySavedSettings() {
        const theme = savedSettings.theme || "light";
        const fontSize = Number(savedSettings.font_size) || 16;
        const highContrast = Boolean(savedSettings.high_contrast);

        const twoFactorToggle = document.getElementById("2fa-toggle");
        const twoFactorMethod = document.getElementById("2fa-method");
        const twoFactorSetup = document.getElementById("2fa-setup");

        const biometricToggle = document.getElementById("biometric-toggle");
        const biometricOptions = document.getElementById("biometric-options");

        const fontRange = document.getElementById("font-size");
        const fontValue = document.getElementById("font-size-value");
        const contrastToggle = document.getElementById("high-contrast");

        if (twoFactorToggle) {
            twoFactorToggle.checked = Boolean(savedSettings.two_fa_enabled);
        }

        if (twoFactorMethod) {
            twoFactorMethod.value = savedSettings.two_fa_method || "auth-app";
        }

        if (twoFactorSetup) {
            twoFactorSetup.classList.toggle(
                "hidden",
                !savedSettings.two_fa_enabled
            );
        }

        if (biometricToggle) {
            biometricToggle.checked = Boolean(
                savedSettings.biometric_enabled
            );
        }

        if (biometricOptions) {
            biometricOptions.classList.toggle(
                "hidden",
                !savedSettings.biometric_enabled
            );
        }

        const selectedBiometric = document.querySelector(
            `input[name="biometric-type"][value="${savedSettings.biometric_type || "fingerprint"}"]`
        );

        if (selectedBiometric) {
            selectedBiometric.checked = true;
        }

        const recoveryEmail = document.getElementById("recovery-email");
        const recoveryPhone = document.getElementById("recovery-phone");
        const securityQuestion = document.getElementById("security-questions");

        if (recoveryEmail) {
            recoveryEmail.value = savedSettings.recovery_email || "";
        }

        if (recoveryPhone) {
            recoveryPhone.value = savedSettings.recovery_phone || "";
        }

        if (securityQuestion) {
            securityQuestion.value = savedSettings.security_question || "";
        }

        if (fontRange) {
            fontRange.value = fontSize;
        }

        if (fontValue) {
            fontValue.textContent = fontSize;
        }

        if (contrastToggle) {
            contrastToggle.checked = highContrast;
        }

        const languageSelect = document.getElementById("language-select");
        const dateFormat = document.getElementById("date-format");
        const timeFormat = document.getElementById("time-format");
        const timeZone = document.getElementById("time-zone");

        if (languageSelect) {
            languageSelect.value = savedSettings.language || "en";
        }

        if (dateFormat) {
            dateFormat.value = savedSettings.date_format || "dd-mm-yyyy";
        }

        if (timeFormat) {
            timeFormat.value = savedSettings.time_format || "12";
        }

        if (timeZone) {
            timeZone.value = savedSettings.timezone || "Asia/Kolkata";
        }

        const notifyEmail = document.getElementById("notify-email");
        const notifyPush = document.getElementById("notify-push");
        const notifyAttendance = document.getElementById("notify-attendance");
        const notifyAnnouncements = document.getElementById(
            "notify-announcements"
        );

        if (notifyEmail) {
            notifyEmail.checked = Boolean(savedSettings.notify_email);
        }

        if (notifyPush) {
            notifyPush.checked = Boolean(savedSettings.notify_push);
        }

        if (notifyAttendance) {
            notifyAttendance.checked = Boolean(
                savedSettings.notify_attendance
            );
        }

        if (notifyAnnouncements) {
            notifyAnnouncements.checked = Boolean(
                savedSettings.notify_announcements
            );
        }

        applyGlobalAppearance(theme, fontSize, highContrast);

        document.querySelectorAll(".theme-btn").forEach(function (button) {
            button.classList.toggle(
                "active",
                button.dataset.theme === theme
            );
        });

        document.querySelectorAll(".layout-btn").forEach(function (button) {
            button.classList.toggle(
                "active",
                button.dataset.layout === (
                    savedSettings.dashboard_layout || "compact"
                )
            );
        });

        document.querySelectorAll("[data-widget]").forEach(function (checkbox) {
            checkbox.checked = (
                savedSettings.dashboard_widgets || []
            ).includes(checkbox.dataset.widget);
        });
    }

    document.querySelectorAll(".nav-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            document.querySelectorAll(".nav-btn").forEach(function (item) {
                item.classList.remove("active");
            });

            document.querySelectorAll(".panel").forEach(function (panel) {
                panel.classList.remove("active-panel");
            });

            button.classList.add("active");

            const panel = document.getElementById(button.dataset.target);

            if (panel) {
                panel.classList.add("active-panel");
            }
        });
    });

    const twoFactorToggle = document.getElementById("2fa-toggle");

    if (twoFactorToggle) {
        twoFactorToggle.addEventListener("change", async function () {
            const setupBox = document.getElementById("2fa-setup");
            const method = document.getElementById("2fa-method");

            setupBox.classList.toggle("hidden", !twoFactorToggle.checked);

            try {
                await saveSettings({
                    two_fa_enabled: twoFactorToggle.checked,
                    two_fa_method: method.value,
                });

                showMessage("Two-factor settings updated.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const setupTwoFactorButton = document.getElementById("2fa-setup-btn");

    if (setupTwoFactorButton) {
        setupTwoFactorButton.addEventListener("click", async function () {
            try {
                await saveSettings({
                    two_fa_enabled: true,
                    two_fa_method: document.getElementById("2fa-method").value,
                });

                showMessage("Two-factor authentication method saved.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const cancelTwoFactorButton = document.getElementById("2fa-cancel-btn");

    if (cancelTwoFactorButton) {
        cancelTwoFactorButton.addEventListener("click", async function () {
            twoFactorToggle.checked = false;
            document.getElementById("2fa-setup").classList.add("hidden");

            try {
                await saveSettings({
                    two_fa_enabled: false,
                });

                showMessage("Two-factor authentication disabled.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const changePasswordButton = document.getElementById(
        "change-password-btn"
    );

    if (changePasswordButton) {
        changePasswordButton.addEventListener("click", async function () {
            const formData = new FormData();

            formData.append(
                "current_password",
                document.getElementById("current-password").value
            );

            formData.append(
                "new_password",
                document.getElementById("new-password").value
            );

            formData.append(
                "confirm_password",
                document.getElementById("confirm-password").value
            );

            const response = await fetch(config.changePasswordUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showMessage(
                    data.error || "Could not change password.",
                    true
                );

                return;
            }

            document.getElementById("current-password").value = "";
            document.getElementById("new-password").value = "";
            document.getElementById("confirm-password").value = "";

            showMessage(data.message);
        });
    }

    const biometricToggle = document.getElementById("biometric-toggle");

    if (biometricToggle) {
        biometricToggle.addEventListener("change", async function () {
            document.getElementById("biometric-options").classList.toggle(
                "hidden",
                !biometricToggle.checked
            );

            try {
                await saveSettings({
                    biometric_enabled: biometricToggle.checked,
                    biometric_type: document.querySelector(
                        'input[name="biometric-type"]:checked'
                    ).value,
                });

                showMessage("Biometric settings updated.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const saveRecoveryButton = document.getElementById("save-recovery");

    if (saveRecoveryButton) {
        saveRecoveryButton.addEventListener("click", async function () {
            try {
                await saveSettings({
                    recovery_email: document.getElementById(
                        "recovery-email"
                    ).value,

                    recovery_phone: document.getElementById(
                        "recovery-phone"
                    ).value,

                    security_question: document.getElementById(
                        "security-questions"
                    ).value,
                });

                showMessage("Recovery information saved.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const themeButtons = document.querySelectorAll(".theme-btn");
    const fontRange = document.getElementById("font-size");
    const fontValue = document.getElementById("font-size-value");
    const contrastToggle = document.getElementById("high-contrast");

    themeButtons.forEach(function (button) {
        button.addEventListener("click", async function () {
            const theme = button.dataset.theme;
            const fontSize = Number(fontRange.value);
            const highContrast = contrastToggle.checked;

            applyGlobalAppearance(theme, fontSize, highContrast);

            themeButtons.forEach(function (item) {
                item.classList.remove("active");
            });

            button.classList.add("active");

            try {
                await saveSettings({
                    theme: theme,
                });

                showMessage("Theme updated. It will apply across the project.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    });

    if (fontRange) {
        fontRange.addEventListener("input", function () {
            const theme =
                document.documentElement.dataset.theme || "light";

            applyGlobalAppearance(
                theme,
                Number(fontRange.value),
                contrastToggle.checked
            );

            fontValue.textContent = fontRange.value;
        });

        fontRange.addEventListener("change", async function () {
            try {
                await saveSettings({
                    font_size: Number(fontRange.value),
                    high_contrast: contrastToggle.checked,
                });

                showMessage(
                    "Font size saved. It will apply across the project."
                );
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    if (contrastToggle) {
        contrastToggle.addEventListener("change", async function () {
            const theme =
                document.documentElement.dataset.theme || "light";

            applyGlobalAppearance(
                theme,
                Number(fontRange.value),
                contrastToggle.checked
            );

            try {
                await saveSettings({
                    high_contrast: contrastToggle.checked,
                    font_size: Number(fontRange.value),
                });

                showMessage(
                    "High contrast setting saved across the project."
                );
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    const saveNotificationsButton = document.getElementById(
        "save-notifications"
    );

    if (saveNotificationsButton) {
        saveNotificationsButton.addEventListener(
            "click",
            async function () {
                try {
                    await saveSettings({
                        notify_email: document.getElementById(
                            "notify-email"
                        ).checked,

                        notify_push: document.getElementById(
                            "notify-push"
                        ).checked,

                        notify_attendance: document.getElementById(
                            "notify-attendance"
                        ).checked,

                        notify_announcements: document.getElementById(
                            "notify-announcements"
                        ).checked,
                    });

                    showMessage("Notification preferences saved.");
                } catch (error) {
                    showMessage(error.message, true);
                }
            }
        );
    }

    const saveTimeButton = document.getElementById("save-time");

    if (saveTimeButton) {
        saveTimeButton.addEventListener("click", async function () {
            try {
                await saveSettings({
                    language: document.getElementById(
                        "language-select"
                    ).value,

                    date_format: document.getElementById(
                        "date-format"
                    ).value,

                    time_format: document.getElementById(
                        "time-format"
                    ).value,

                    timezone: document.getElementById(
                        "time-zone"
                    ).value,
                });

                showMessage("Language and time settings saved.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    let selectedLayout = savedSettings.dashboard_layout || "compact";
    const previewGrid = document.getElementById("preview-grid");

    function applyLayout(layout) {
        if (!previewGrid) {
            return;
        }

        previewGrid.dataset.layout = layout;

        if (layout === "compact") {
            previewGrid.style.gridTemplateColumns =
                "repeat(auto-fill, minmax(140px, 1fr)";

            previewGrid.style.gap = "8px";
        } else if (layout === "comfortable") {
            previewGrid.style.gridTemplateColumns =
                "repeat(auto-fill, minmax(220px, 1fr)";

            previewGrid.style.gap = "12px";
        } else {
            previewGrid.style.gridTemplateColumns = "1fr";
            previewGrid.style.gap = "10px";
        }
    }

    document.querySelectorAll(".layout-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            document.querySelectorAll(".layout-btn").forEach(function (item) {
                item.classList.remove("active");
            });

            button.classList.add("active");
            selectedLayout = button.dataset.layout;

            applyLayout(selectedLayout);
        });
    });

    const previewDashboardButton = document.getElementById(
        "preview-dashboard"
    );

    if (previewDashboardButton) {
        previewDashboardButton.addEventListener("click", function () {
            const preview = document.getElementById("dashboard-preview");

            previewGrid.innerHTML = "";

            document.querySelectorAll("[data-widget]").forEach(
                function (checkbox) {
                    if (checkbox.checked) {
                        const widget = document.createElement("div");

                        widget.className = "widget demo";
                        widget.textContent =
                            checkbox.parentElement.textContent.trim();

                        previewGrid.appendChild(widget);
                    }
                }
            );

            applyLayout(selectedLayout);

            preview.classList.toggle(
                "hidden",
                previewGrid.children.length === 0
            );
        });
    }

    const saveDashboardButton = document.getElementById("save-dashboard");

    if (saveDashboardButton) {
        saveDashboardButton.addEventListener("click", async function () {
            const widgets = [];

            document.querySelectorAll("[data-widget]").forEach(
                function (checkbox) {
                    if (checkbox.checked) {
                        widgets.push(checkbox.dataset.widget);
                    }
                }
            );

            try {
                await saveSettings({
                    dashboard_layout: selectedLayout,
                    dashboard_widgets: widgets,
                });

                showMessage("Dashboard layout saved.");
            } catch (error) {
                showMessage(error.message, true);
            }
        });
    }

    applySavedSettings();
    renderHistory();
    renderSessions();
})();