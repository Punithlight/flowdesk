document.addEventListener("DOMContentLoaded", () => {

  // ==========================================================
  // CONFIG / HELPERS
  // ==========================================================
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const currentUserId = document.querySelector('meta[name="current-user-id"]').content;

  function apiGet(url) {
    return fetch(url).then(r => r.json());
  }

  function apiPost(url, data) {
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify(data)
    }).then(r => r.json());
  }

  // ==========================================================
  // ELEMENTS
  // ==========================================================
  const membersContainer   = document.querySelector(".members");
  const memberSearch       = document.getElementById("memberSearch");

  const chatWindow      = document.getElementById("chatWindow");
  const chatUserName    = document.getElementById("chatUserName");
  const chatUserStatus  = document.getElementById("chatUserStatus");
  const chatUserImage   = document.getElementById("chatUserImage");

  const messageInput = document.getElementById("messageInput");
  const sendBtn       = document.getElementById("sendBtn");

  const groupSelect       = document.getElementById("groupSelect");
  const newGroupName      = document.getElementById("newGroupName");
  const createGroupBtn    = document.getElementById("createGroupBtn");
  const deleteGroupBtn    = document.getElementById("deleteGroupBtn");
  const addToGroupBtn     = document.getElementById("addToGroupBtn");
  const confirmAddBtn     = document.getElementById("confirmAddBtn");
  const groupMembersList  = document.getElementById("groupMembersList");
  const startGroupChatBtn = document.getElementById("startGroupChatBtn");
  const createGroupFeatureBtn = document.getElementById("createGroupFeatureBtn");

  const emojiBtn    = document.querySelector(".emojiBtn");
  const emojiPicker = document.querySelector(".emoji-picker");

  const attachFileBtn   = document.getElementById("attachFileBtn");
  const attachImageBtn  = document.getElementById("attachImageBtn");
  const attachDocBtn    = document.getElementById("attachDocBtn");
  const attachFileInput  = document.getElementById("attachFileInput");
  const attachImageInput = document.getElementById("attachImageInput");
  const attachDocInput   = document.getElementById("attachDocInput");

  const profileDrawer   = document.getElementById("profileDrawer");
  const drawerClose     = document.getElementById("drawerClose");
  const drawerBackdrop  = document.getElementById("drawerBackdrop");
  const drawerImage     = document.getElementById("drawerImage");
  const drawerName      = document.getElementById("drawerName");
  const drawerStatus    = document.getElementById("drawerStatus");
  const drawerId        = document.getElementById("drawerId");
  const drawerEmail     = document.getElementById("drawerEmail");
  const drawerPhone     = document.getElementById("drawerPhone");
  const drawerDept      = document.getElementById("drawerDept");
  const drawerDesignation = document.getElementById("drawerDesignation");

  const [phoneBtn, videoBtn, , searchBtn, starBtn, ellipsisBtn] =
    document.querySelectorAll(".chat-actions button");
  const screenShareHeaderBtn = document.getElementById("screenShareHeaderBtn");
  const screenShareBanner    = document.getElementById("screenShareBanner");
  const stopScreenShareBtn   = document.getElementById("stopScreenShareBtn");

  const chatsTabBtn       = document.getElementById("chatsTabBtn");
  const recordingsTabBtn  = document.getElementById("recordingsTabBtn");
  const chatsTabContent   = document.getElementById("chatsTabContent");
  const recordingsPanel   = document.getElementById("recordingsPanel");
  const recordingsList    = document.getElementById("recordingsList");

  const deleteConfirmModal   = document.getElementById("deleteConfirmModal");
  const deleteConfirmBackdrop= document.getElementById("deleteConfirmBackdrop");
  const cancelDeleteBtn      = document.getElementById("cancelDeleteBtn");
  const confirmDeleteBtn     = document.getElementById("confirmDeleteBtn");

  // ==========================================================
  // STATE
  // ==========================================================
  let currentRecipientId = null;   // number or "group:<id>"
  let currentContact = null;       // {name, email, phone, dept, designation, id}
  let addMemberMode = false;
  let pendingDeleteEl = null;
  let pollTimer = null;
  let localStream = null;          // for call/screen-share demo

  // ==========================================================
  // MEMBER LIST: select + search
  // ==========================================================
  membersContainer.addEventListener("click", (e) => {
    const li = e.target.closest(".member[data-id]");
    if (!li) return;
    selectContact(li);
  });

  function selectContact(li) {
    document.querySelectorAll(".member").forEach(m => m.classList.remove("active"));
    li.classList.add("active");

    currentRecipientId = li.dataset.id;
    currentContact = {
      id: li.dataset.id,
      name: li.dataset.name,
      email: li.dataset.email,
      phone: li.dataset.phone,
      dept: li.dataset.dept,
      designation: li.dataset.designation
    };

    chatUserName.textContent = currentContact.name;
    chatUserStatus.textContent = "🟢 Online";
    chatUserImage.src = li.querySelector("img").src;

    loadMessages();
    startPolling();
  }

  memberSearch.addEventListener("input", () => {
    const q = memberSearch.value.trim().toLowerCase();
    document.querySelectorAll(".member[data-id]").forEach(li => {
      const name = li.dataset.name.toLowerCase();
      li.style.display = name.includes(q) ? "" : "none";
    });
  });

  // ==========================================================
  // MESSAGES
  // ==========================================================
  function loadMessages() {
    if (!currentRecipientId) return;
    apiGet(`/teamchat/messages/?recipient_id=${currentRecipientId}`)
      .then(data => renderMessages(data.messages || []));
  }

  function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(loadMessages, 4000);
  }

  function renderMessages(messages) {
    chatWindow.innerHTML = "";

    if (!messages.length) {
      chatWindow.innerHTML = `
        <div class="message info">
            <div class="bubble">
                <span class="sender">FlowDesk</span>
                <p>No messages yet. Say hi!</p>
            </div>
        </div>`;
      return;
    }

    messages.forEach(msg => {
      const isMine = String(msg.sender) === String(currentUserId);

      const wrap = document.createElement("div");
      wrap.className = "message " + (isMine ? "sent" : "received");
      wrap.dataset.messageId = msg.id;

      const bubble = document.createElement("div");
      bubble.className = "bubble";

      bubble.innerHTML = `
        <span class="sender">
            ${escapeHtml(msg.sender_name)}
        </span>
        <p>
            ${escapeHtml(msg.content || "")}
        </p>
        <small>
            ${msg.created_at}
        </small>
      `;

      // SHOW ATTACHMENTS (SAFELY DETECT & DISPLAY IMAGES)
      if (msg.attachments && msg.attachments.length) {
        msg.attachments.forEach(file => {
          const url = file.url || "";
          const filename = file.filename || "";
          const isImage = (file.file_type && file.file_type.startsWith("image")) ||
                          /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url) ||
                          /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(filename);

          if (isImage) {
            const img = document.createElement("img");
            img.src = url;
            img.className = "chat-image";
            img.alt = filename || "Attachment";
            img.style.maxWidth = "100%";
            img.style.maxHeight = "250px";
            img.style.borderRadius = "8px";
            img.style.marginTop = "8px";
            img.style.display = "block";
            img.style.cursor = "pointer";
            img.onclick = () => {
              window.open(url, "_blank");
            };
            bubble.appendChild(img);
          } else {
            const link = document.createElement("a");
            link.href = url;
            link.target = "_blank";
            link.textContent = "📎 " + (filename || "Attachment");
            link.style.display = "block";
            link.style.marginTop = "4px";
            bubble.appendChild(link);
          }
        });
      }

      wrap.appendChild(bubble);
      chatWindow.appendChild(wrap);
    });

    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  }

  function escapeAttr(str) {
    return escapeHtml(str).replace(/"/g, "&quot;");
  }

  function parseRecordingMarker(content) {
    if (!content) return null;
    const match = /^\[\[recording:(.+?)\|(.+?)\|(.+?)\]\]$/.exec(content.trim());
    if (!match) return null;
    return { url: match[1], filename: match[2], duration: match[3] };
  }

  function sendMessage(content) {
    if (!currentRecipientId) {
      alert("Select a contact or group first.");
      return;
    }
    if (!content.trim()) return;

    apiPost("/teamchat/send/", {
      recipient_id: currentRecipientId,
      content: content.trim()
    }).then(res => {
      if (res.error) {
        alert(res.error);
        return;
      }
      messageInput.value = "";
      loadMessages();
    });
  }

  window.loadMessages = loadMessages;

  sendBtn.addEventListener("click", () => sendMessage(messageInput.value));
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(messageInput.value);
  });

  // Open delete confirmation modal on right-clicking sent messages
  chatWindow.addEventListener("contextmenu", (e) => {
    const sentMessageEl = e.target.closest(".message.sent");
    if (!sentMessageEl) return;

    e.preventDefault();
    pendingDeleteEl = sentMessageEl;
    deleteConfirmModal.setAttribute("aria-hidden", "false");
    deleteConfirmModal.classList.add("open");
  });

  function closeDeleteModal() {
    deleteConfirmModal.setAttribute("aria-hidden", "true");
    deleteConfirmModal.classList.remove("open");
    pendingDeleteEl = null;
  }

  cancelDeleteBtn.addEventListener("click", closeDeleteModal);
  deleteConfirmBackdrop.addEventListener("click", closeDeleteModal);

  // Calls Django backend to delete from DB
  confirmDeleteBtn.addEventListener("click", () => {
    if (!pendingDeleteEl) return;

    const messageId = pendingDeleteEl.dataset.messageId;

    if (!messageId) {
      pendingDeleteEl.remove();
      closeDeleteModal();
      return;
    }

    apiPost(`/teamchat/delete-message/${messageId}/`, {})
      .then(res => {
        if (res.error) {
          alert(res.error);
        } else {
          pendingDeleteEl.remove();
        }
        closeDeleteModal();
      })
      .catch(err => {
        console.error("Error deleting message:", err);
        alert("An error occurred while deleting the message.");
        closeDeleteModal();
      });
  });

  // ==========================================================
  // GROUPS
  // ==========================================================
  function loadGroups(selectId) {
    apiGet("/teamchat/groups/").then(data => {
      groupSelect.innerHTML = '<option value="">-- Select Group --</option>';
      (data.groups || []).forEach(g => {
        const opt = document.createElement("option");
        opt.value = g.id;
        opt.textContent = g.name;
        groupSelect.appendChild(opt);
      });
      if (selectId) groupSelect.value = selectId;
    });
  }
  loadGroups();

  createGroupFeatureBtn.addEventListener("click", () => newGroupName.focus());

  createGroupBtn.addEventListener("click", () => {
    const name = newGroupName.value.trim();
    if (!name) return alert("Enter a group name.");
    apiPost("/teamchat/groups/create/", { name }).then(res => {
      if (res.error) return alert(res.error);
      newGroupName.value = "";
      loadGroups(res.id);
    });
  });

  deleteGroupBtn.addEventListener("click", () => {
    const groupId = groupSelect.value;
    if (!groupId) return alert("Select a group to delete.");
    if (!confirm("Delete this group?")) return;
    apiPost("/teamchat/groups/delete/", { group_id: groupId }).then(res => {
      if (res.error) return alert(res.error);
      loadGroups();
      groupMembersList.innerHTML = "";
    });
  });

  addToGroupBtn.addEventListener("click", () => {
    if (!groupSelect.value) return alert("Select a group first.");
    addMemberMode = true;
    addToGroupBtn.style.display = "none";
    confirmAddBtn.style.display = "";

    document.querySelectorAll(".member[data-id]").forEach(li => {
      if (li.querySelector(".addMemberCheckbox")) return;
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.className = "addMemberCheckbox";
      cb.value = li.dataset.id;
      li.prepend(cb);
    });
  });

  confirmAddBtn.addEventListener("click", () => {
    const groupId = groupSelect.value;
    const ids = Array.from(document.querySelectorAll(".addMemberCheckbox:checked"))
      .map(cb => cb.value);

    apiPost("/teamchat/groups/add-members/", {
      group_id: groupId,
      member_ids: ids
    }).then(res => {
      if (res.error) return alert(res.error);
      alert(`${res.added} member(s) added.`);
      exitAddMemberMode();
      loadGroups(groupId);
    });
  });

  function exitAddMemberMode() {
    addMemberMode = false;
    addToGroupBtn.style.display = "";
    confirmAddBtn.style.display = "none";
    document.querySelectorAll(".addMemberCheckbox").forEach(cb => cb.remove());
  }

  startGroupChatBtn.addEventListener("click", () => {
    const groupId = groupSelect.value;
    if (!groupId) return alert("Select a group first.");

    document.querySelectorAll(".member").forEach(m => m.classList.remove("active"));

    currentRecipientId = "group:" + groupId;
    currentContact = null;
    chatUserName.textContent = groupSelect.options[groupSelect.selectedIndex].textContent;
    chatUserStatus.textContent = "👥 Group chat";
    chatUserImage.src = chatUserImage.getAttribute("src");

    loadMessages();
    startPolling();
  });

  // ==========================================================
  // EMOJI PICKER
  // ==========================================================
  emojiBtn.addEventListener("click", () => {
    emojiPicker.classList.toggle("open");
  });

  emojiPicker.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    messageInput.value += btn.textContent;
    messageInput.focus();
  });

  // ==========================================================
  // FILE & IMAGE UPLOAD
  // ==========================================================
  attachFileBtn.addEventListener("click", () => attachFileInput.click());
  attachImageBtn.addEventListener("click", () => attachImageInput.click());
  attachDocBtn.addEventListener("click", () => attachDocInput.click());

  function uploadAttachments(e) {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    if (!currentRecipientId) {
      alert("Select a recipient or group first.");
      e.target.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("recipient_id", currentRecipientId);
    formData.append("content", messageInput.value.trim() || "");

    files.forEach(file => {
      formData.append("attachments", file);
    });

    fetch("/teamchat/send/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken
      },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }
      messageInput.value = "";
      loadMessages();
    })
    .catch(err => {
      console.error("Upload failed:", err);
      alert("Failed to send image.");
    })
    .finally(() => {
      e.target.value = "";
    });
  }

  attachFileInput.addEventListener("change", uploadAttachments);
  attachImageInput.addEventListener("change", uploadAttachments);
  attachDocInput.addEventListener("change", uploadAttachments);

  // ==========================================================
  // PROFILE DRAWER
  // ==========================================================
  ellipsisBtn.addEventListener("click", () => {
    if (!currentContact) return alert("Select a contact first.");
    drawerImage.src = chatUserImage.src;
    drawerName.textContent = currentContact.name;
    drawerStatus.textContent = "🟢 Online";
    drawerId.textContent = "ID: " + currentContact.id;
    drawerEmail.textContent = currentContact.email || "-";
    drawerPhone.textContent = currentContact.phone || "-";
    drawerDept.textContent = currentContact.dept || "-";
    drawerDesignation.textContent = currentContact.designation || "-";

    profileDrawer.setAttribute("aria-hidden", "false");
    profileDrawer.classList.add("open");
  });

  function closeDrawer() {
    profileDrawer.setAttribute("aria-hidden", "true");
    profileDrawer.classList.remove("open");
  }
  drawerClose.addEventListener("click", closeDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  document.getElementById("messageProfileBtn").addEventListener("click", closeDrawer);

  // ==========================================================
  // CALLS + SCREEN SHARE
  // ==========================================================
  window.getCurrentRecipientId = () => currentRecipientId;

  document.getElementById("audioCallBtn").addEventListener("click", closeDrawer);
  document.getElementById("videoCallBtn").addEventListener("click", closeDrawer);
  document.getElementById("shareScreenBtn").addEventListener("click", closeDrawer);

  searchBtn.addEventListener("click", () => {});
  starBtn.addEventListener("click", () => {});

  // ==========================================================
  // RECORDINGS TAB
  // ==========================================================
  function loadRecordings() {
    apiGet("/teamchat/recordings/").then(data => {
      const recordings = data.recordings || [];

      if (!recordings.length) {
        recordingsList.innerHTML = '<li class="recordings-empty">No recordings yet.</li>';
        return;
      }

      recordingsList.innerHTML = recordings.map(rec => `
        <li>
          <a class="recording-item" href="${rec.url}" target="_blank" rel="noopener">
            <span class="rec-icon"><i class="fa-solid fa-video"></i></span>
            <span class="rec-meta">
              <h4>${escapeHtml(rec.target)}</h4>
              <p>${escapeHtml(rec.started_by)} &middot; ${escapeHtml(rec.duration)} &middot; ${escapeHtml(rec.created_at)}</p>
            </span>
          </a>
        </li>
      `).join("");
    });
  }
  window.loadRecordings = loadRecordings;

  chatsTabBtn.addEventListener("click", () => {
    chatsTabBtn.classList.add("active");
    recordingsTabBtn.classList.remove("active");
    chatsTabContent.style.display = "";
    recordingsPanel.style.display = "none";
  });

  recordingsTabBtn.addEventListener("click", () => {
    recordingsTabBtn.classList.add("active");
    chatsTabBtn.classList.remove("active");
    chatsTabContent.style.display = "none";
    recordingsPanel.style.display = "block";
    loadRecordings();
  });


const joinBtn = document.getElementById("joinMeetingBtn");

    if (!joinBtn) return;

    joinBtn.addEventListener("click", function () {

        document.getElementById("callOverlay").style.display = "flex";

        document.getElementById("chatUserName").textContent =
            window.meetingData.title;

        document.getElementById("chatUserStatus").textContent =
            "Meeting";

        if (typeof joinMeeting === "function") {
            joinMeeting(window.meetingData.room);
        }

    });

});