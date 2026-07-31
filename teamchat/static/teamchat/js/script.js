// Basic chat functionality: send messages, toggle emoji picker, insert emoji, and member search

// Wrap initialization in a try/catch and add defensive checks so runtime errors don't break UX
document.addEventListener('DOMContentLoaded', function () {
  try {
    const sendBtn = document.getElementById('sendBtn');
    const messageInput = document.getElementById('messageInput');
    // fallback: try to find by class if id missing
    const chatWindow = document.getElementById('chatWindow') || document.querySelector('.chat-window');
    const emojiBtn = document.querySelector('.emojiBtn');
    const emojiPicker = document.querySelector('.emoji-picker');
    const memberSearch = document.getElementById('memberSearch');
    const chatHeaderTitle = document.querySelector('.chat-header .chat-user h3');
    const chatHeaderStatus = document.querySelector('.chat-header .chat-user .online-status');
    const chatHeaderImage = document.querySelector('.chat-header .chat-user img');
    let selectedRecipient = null;

    function setChatPlaceholder(message) {
      if (!chatWindow) return;
      chatWindow.innerHTML = '';
      const placeholder = document.createElement('div');
      placeholder.className = 'message info';
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      const sender = document.createElement('span');
      sender.className = 'sender';
      sender.textContent = 'FlowDesk';
      const p = document.createElement('p');
      p.textContent = message;
      const small = document.createElement('small');
      small.textContent = 'Now';
      bubble.appendChild(sender);
      bubble.appendChild(p);
      bubble.appendChild(small);
      placeholder.appendChild(bubble);
      chatWindow.appendChild(placeholder);
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function updateChatHeader(name, status, imageSrc) {
      if (chatHeaderTitle) chatHeaderTitle.textContent = name || 'Select a contact';
      if (chatHeaderStatus) chatHeaderStatus.textContent = status || '⏳ Waiting for selection';
      if (chatHeaderImage && imageSrc) chatHeaderImage.src = imageSrc;
    }

    function createMessageBubble(text, type = 'sent') {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${type}`;

      if (type === 'received') {
        const img = document.createElement('img');
        img.src = 'images/emp1.svg';
        img.alt = 'Sachin Gond';
        messageDiv.appendChild(img);
      }

      const bubble = document.createElement('div');
      bubble.className = 'bubble';

      const sender = document.createElement('span');
      sender.className = 'sender';
      sender.textContent = type === 'sent' ? 'You' : 'Sachin Gond';

      const p = document.createElement('p');
      p.textContent = text;

      const small = document.createElement('small');
      const now = new Date();
      const hours = now.getHours();
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const displayHour = ((hours + 11) % 12) + 1; // 12-hour format
      small.textContent = `${displayHour}:${minutes} ${ampm}`;

      bubble.appendChild(sender);
      bubble.appendChild(p);
      bubble.appendChild(small);

      messageDiv.appendChild(bubble);

      return messageDiv;
    }

    let screenSharingActive = false;
    let screenShareInitiator = '';

    const CURRENT_USER_ID = document.querySelector('meta[name="current-user-id"]')?.content || null;

    function loadMessages() {
      if (!selectedRecipient) {
        setChatPlaceholder('Select a team member or group to start chatting.');
        return;
      }

      const url = '/teamchat/messages/?recipient_id=' + encodeURIComponent(selectedRecipient.id);
      fetch(url)
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Failed to load messages');
          }
          return response.json();
        })
        .then(function (data) {
          if (!chatWindow) return;
          chatWindow.innerHTML = '';
          (data.messages || []).forEach(function (message) {
            const type = String(message.sender) === String(CURRENT_USER_ID) ? 'sent' : 'received';
            const bubble = createMessageBubble(message.content, type);
            chatWindow.appendChild(bubble);
          });
          chatWindow.scrollTop = chatWindow.scrollHeight;
        })
        .catch(function (error) {
          console.error(error);
        });
    }

    function updateScreenShareBanner() {
      const banner = document.getElementById('screenShareBanner');
      const textEl = document.getElementById('screenShareText');
      const stopBtn = document.getElementById('stopScreenShareBtn');
      if (!banner || !textEl || !stopBtn) return;
      if (screenSharingActive) {
        textEl.textContent = screenShareInitiator
          ? `You are sharing your screen with ${screenShareInitiator}.`
          : 'You are sharing your screen.';
        banner.style.display = 'flex';
      } else {
        banner.style.display = 'none';
      }
    }
 
    function toggleScreenShare(active, initiatorName) {
      screenSharingActive = active;
      screenShareInitiator = initiatorName || '';
      updateScreenShareBanner();
      if (active) {
        alert('Screen sharing started.');
      } else {
        alert('Screen sharing stopped.');
      }
    }
 
    function sendMessage() {
      if (!messageInput) return;
      if (!selectedRecipient) {
        alert('Select a team member or group first.');
        return;
      }
      const text = messageInput.value.trim();
      if (!text) return;

      fetch('/teamchat/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        body: JSON.stringify({ content: text, recipient_id: selectedRecipient.id })
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Failed to send message');
          }
          return response.json();
        })
        .then(function (data) {
          const msg = createMessageBubble(data.content, 'sent');
          if (chatWindow) {
            chatWindow.appendChild(msg);
            chatWindow.scrollTop = chatWindow.scrollHeight;
          }
          messageInput.value = '';
          messageInput.focus();
        })
        .catch(function (error) {
          console.error(error);
          alert('Unable to send message right now.');
        });
    }

    // Send button
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);

    // Enter key sends message
    if (messageInput) {
      messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
    }

    // Ensure emoji picker is attached to body to avoid z-index/overflow issues
    if (emojiPicker && emojiPicker.parentElement !== document.body) {
      document.body.appendChild(emojiPicker);
    }

    // Click handler for the whole member list item (not just the image)
    const memberListItems = document.querySelectorAll('.members .member');
    memberListItems.forEach(function (li) {
      li.addEventListener('click', function (e) {
        // ignore if clicking on selection controls
        if (e.target.closest && (e.target.closest('.member-select') || e.target.closest('.add-member-btn'))) return;
        selectedRecipient = {
          id: li.getAttribute('data-id') || li.dataset.id,
          name: li.querySelector('h4')?.textContent || 'Selected member',
          status: li.querySelector('p')?.textContent || 'Online',
          image: li.querySelector('img')?.src || ''
        };
        updateChatHeader(selectedRecipient.name, selectedRecipient.status, selectedRecipient.image);
        loadMessages();
      });
    });

    // --- GROUP MANAGEMENT ---
    const groupSelect = document.getElementById('groupSelect');
    const newGroupInput = document.getElementById('newGroupName');
    const createGroupBtn = document.getElementById('createGroupBtn');
    const deleteGroupBtn = document.getElementById('deleteGroupBtn');
    const addToGroupBtn = document.getElementById('addToGroupBtn');
    const confirmAddBtn = document.getElementById('confirmAddBtn');
    const groupMembersList = document.getElementById('groupMembersList');
    const startGroupChatBtn = document.getElementById('startGroupChatBtn');

    let groupsCache = [];
    async function fetchGroups() {
      try {
        const res = await fetch('/teamchat/groups/');
        if (!res.ok) throw new Error('Failed to load groups');
        const json = await res.json();
        groupsCache = json.groups || [];
        renderGroupSelect();
        return groupsCache;
      } catch (err) {
        console.error('fetchGroups error', err);
        // fallback: try client-side storage if server not available
        try {
          const local = JSON.parse(localStorage.getItem('flowdesk_groups') || '[]');
          if (Array.isArray(local)) {
            groupsCache = local;
          } else {
            groupsCache = [];
          }
        } catch (e) {
          groupsCache = [];
        }
        renderGroupSelect();
        return groupsCache;
      }
    }

    function renderGroupSelect() {
      if (!groupSelect) return;
      const placeholder = document.createElement('option');
      placeholder.value = '';
      placeholder.textContent = '-- Select group --';
      groupSelect.innerHTML = '';
      groupSelect.appendChild(placeholder);
      groupsCache.forEach(function (g) {
        const opt = document.createElement('option');
        opt.value = String(g.id);
        opt.textContent = g.name + ' (' + (g.members ? g.members.length : 0) + ')';
        groupSelect.appendChild(opt);
      });
      renderGroupMembers();
    }

    function renderGroupMembers() {
      if (!groupMembersList) return;
      const sel = groupSelect ? groupSelect.value : '';
      groupMembersList.innerHTML = '';
      if (!sel) return;
      const g = groupsCache.find(x => String(x.id) === String(sel));
      if (!g || !g.members) return;
      g.members.forEach(function (id) {
        const el = document.querySelector('.members .member[data-id="' + id + '"]');
        if (el) groupMembersList.appendChild(el.cloneNode(true));
      });
    }

    // Ensure each member element has a hidden checkbox for selection when adding to groups
    function ensureMemberCheckboxes() {
      const members = document.querySelectorAll('.members .member');
      members.forEach(function (m) {
        if (m.querySelector('.member-select')) return;
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'member-select';
        cb.setAttribute('data-id', m.getAttribute('data-id') || m.dataset.id || '');
        cb.style.display = 'none';
        cb.style.marginRight = '6px';
        m.insertBefore(cb, m.firstChild);
      });
    }

    if (createGroupBtn) {
      createGroupBtn.addEventListener('click', async function () {
        const name = (newGroupInput && newGroupInput.value || '').trim();
        if (!name) { alert('Enter a group name'); return; }
        try {
          const res = await fetch('/teamchat/groups/create/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({ name: name })
          });
          if (!res.ok) throw new Error('Create failed');
          const json = await res.json();
          // update cache and UI even if server later becomes unavailable
          await fetchGroups();
          if (groupSelect) { groupSelect.value = String(json.id); renderGroupMembers(); }
          newGroupInput.value = '';
          // save a lightweight local copy for fallback
          try { localStorage.setItem('flowdesk_groups', JSON.stringify(groupsCache)); } catch (e) { /* ignore */ }
          alert('Group "' + json.name + '" created.');
          console.log('Group created:', json);
        } catch (err) {
          console.error(err);
          // optimistic local fallback: add to local cache so user can continue
          const fakeId = Date.now();
          groupsCache.push({ id: fakeId, name: name, members: [] });
          renderGroupSelect();
          if (groupSelect) { groupSelect.value = String(fakeId); renderGroupMembers(); }
          try { localStorage.setItem('flowdesk_groups', JSON.stringify(groupsCache)); } catch (e) {}
          alert('Group created locally (offline): ' + name);
        }
      });
    }

    // Quick-create feature button (top of sidebar)
    const createGroupFeatureBtn = document.getElementById('createGroupFeatureBtn');
    if (createGroupFeatureBtn) {
      createGroupFeatureBtn.addEventListener('click', async function () {
        const name = prompt('Enter new group name:');
        if (!name) return;
        try {
          const res = await fetch('/teamchat/groups/create/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({ name: name })
          });
          if (!res.ok) throw new Error('Create failed');
          const json = await res.json();
          await fetchGroups();
          if (groupSelect) { groupSelect.value = String(json.id); renderGroupMembers(); }
          alert('Group "' + name + '" created. Use Add selected to group to add members.');
        } catch (err) {
          console.error(err);
          // fallback - add local fake group
          const fakeId = Date.now();
          groupsCache.push({ id: fakeId, name: name, members: [] });
          renderGroupSelect();
          if (groupSelect) { groupSelect.value = String(fakeId); renderGroupMembers(); }
          alert('Group created locally (offline): ' + name);
        }
      });
    }

    // create hidden checkboxes for members on load
    ensureMemberCheckboxes();

    if (deleteGroupBtn) {
      deleteGroupBtn.addEventListener('click', async function () {
        const sel = groupSelect ? groupSelect.value : '';
        if (!sel) { alert('Select a group to delete'); return; }
        if (!confirm('Delete this group?')) return;
        try {
          const res = await fetch('/teamchat/groups/delete/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({ group_id: sel })
          });
          if (!res.ok) throw new Error('Delete failed');
          await fetchGroups();
        } catch (err) {
          console.error(err);
          alert('Unable to delete group');
        }
      });
    }

    if (addToGroupBtn) {
      addToGroupBtn.addEventListener('click', function () {
        // show checkboxes for members
        document.querySelectorAll('.member-select').forEach(function (cb) { cb.style.display = 'inline-block'; });
        if (confirmAddBtn) confirmAddBtn.style.display = 'inline-block';
      });
    }

    if (confirmAddBtn) {
      confirmAddBtn.addEventListener('click', async function () {
        const sel = groupSelect ? groupSelect.value : '';
        if (!sel) { alert('Select a group first'); return; }
        const checked = Array.from(document.querySelectorAll('.member-select:checked')).map(function (cb) { return cb.getAttribute('data-id') || cb.dataset.id; });
        try {
          const res = await fetch('/teamchat/groups/add-members/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({ group_id: sel, member_ids: checked })
          });
          if (!res.ok) throw new Error('Add members failed');
          const json = await res.json();
          await fetchGroups();
          document.querySelectorAll('.member-select').forEach(function (cb) { cb.checked = false; cb.style.display = 'none'; });
          if (confirmAddBtn) confirmAddBtn.style.display = 'none';
        } catch (err) {
          console.error(err);
          alert('Unable to add members');
        }
      });
    }

    if (groupSelect) {
      groupSelect.addEventListener('change', function () { renderGroupMembers(); });
      // allow double-click on select to delete the highlighted group (quick UX)
      groupSelect.addEventListener('dblclick', function () {
        const sel = groupSelect.value;
        if (!sel) return;
        if (!confirm('Delete group "' + sel + '"?')) return;
        const groups = loadGroups();
        delete groups[sel];
        saveGroups(groups);
        renderGroupSelect();
      });
    }

    if (startGroupChatBtn) {
      startGroupChatBtn.addEventListener('click', function () {
        const sel = groupSelect ? groupSelect.value : '';
        if (!sel) { alert('Select a group to start chat'); return; }
        const g = groupsCache.find(x => String(x.id) === String(sel));
        selectedRecipient = { id: 'group:' + sel, name: g ? g.name : 'Group', status: 'Group', image: '' };
        updateChatHeader(selectedRecipient.name, selectedRecipient.status, selectedRecipient.image);
        loadMessages();
      });
    }

    // initialize groups (load from server)
    fetchGroups();

    // Single delegated click handler to manage emoji toggle/selection and member image clicks
    document.addEventListener('click', function (e) {
      const target = e.target;

      // Emoji toggle (button)
      if (target.closest && target.closest('.emojiBtn')) {
        e.preventDefault();
        if (emojiPicker) {
          emojiPicker.classList.toggle('visible');
        }
        return;
      }

      // Emoji selection
      const emojiButton = target.closest ? target.closest('.emoji-picker button') : null;
      if (emojiButton && emojiPicker && emojiPicker.classList.contains('visible')) {
        const emoji = emojiButton.textContent || '';
        if (messageInput) {
          const start = (typeof messageInput.selectionStart === 'number') ? messageInput.selectionStart : messageInput.value.length;
          const end = (typeof messageInput.selectionEnd === 'number') ? messageInput.selectionEnd : start;
          messageInput.value = messageInput.value.slice(0, start) + emoji + messageInput.value.slice(end);
          const pos = start + emoji.length;
          try { messageInput.setSelectionRange(pos, pos); } catch (err) { /* ignore */ }
          messageInput.focus();
        }
        emojiPicker.classList.remove('visible');
        return;
      }

      // Click on member image — either open profile or toggle selection when in add/selection mode
      const memberImg = target.closest ? target.closest('.members .member img') : null;
      if (memberImg) {
        const memberEl = memberImg.closest('.member');
        if (!memberEl) return;
        // determine if selection controls are active: visible checkboxes or any member-select in DOM shown
        const anyCheckboxVisible = Array.from(document.querySelectorAll('.member-select')).some(cb => cb && cb.style && cb.style.display !== 'none');
        if (anyCheckboxVisible) {
          // toggle selection via checkbox if present
          const cb = memberEl.querySelector('.member-select');
          if (cb) {
            cb.style.display = 'inline-block';
            cb.checked = !cb.checked;
            cb.dispatchEvent(new Event('change', { bubbles: true }));
          } else {
            // fallback: toggle selected class on li and show confirm button if needed
            memberEl.classList.toggle('selected');
            const anySelected = document.querySelectorAll('.member.selected').length > 0 || document.querySelectorAll('.member-select:checked').length > 0;
            const confirmBtn = document.getElementById('confirmAddBtn');
            if (confirmBtn) confirmBtn.style.display = anySelected ? 'inline-block' : 'none';
          }
        } else {
          selectedRecipient = {
            id: memberEl.getAttribute('data-id') || memberEl.dataset.id,
            name: memberEl.querySelector('h4')?.textContent || 'Selected member',
            status: memberEl.querySelector('p')?.textContent || 'Online',
            image: memberEl.querySelector('img')?.getAttribute('src') || ''
          };
          updateChatHeader(selectedRecipient.name, selectedRecipient.status, selectedRecipient.image);
          loadMessages();
        }
        return;
      }

      // Click outside emoji picker should close it
      if (emojiPicker && !emojiPicker.contains(target) && !target.closest('.emojiBtn')) {
        emojiPicker.classList.remove('visible');
      }
    });

    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const deleteConfirmBackdrop = document.getElementById('deleteConfirmBackdrop');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    let pendingDeleteMessage = null;

    function showDeleteConfirm(messageEl) {
      pendingDeleteMessage = messageEl;
      if (deleteConfirmModal) {
        deleteConfirmModal.classList.add('open');
        deleteConfirmModal.setAttribute('aria-hidden', 'false');
      }
    }

    function hideDeleteConfirm() {
      pendingDeleteMessage = null;
      if (deleteConfirmModal) {
        deleteConfirmModal.classList.remove('open');
        deleteConfirmModal.setAttribute('aria-hidden', 'true');
      }
    }

    if (chatWindow) {
      chatWindow.addEventListener('dblclick', function (e) {
        const messageEl = e.target.closest('.message');
        if (!messageEl) return;
        showDeleteConfirm(messageEl);
      });
    }

    if (cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', hideDeleteConfirm);
    if (deleteConfirmBackdrop) deleteConfirmBackdrop.addEventListener('click', hideDeleteConfirm);
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener('click', function () {
        if (pendingDeleteMessage) {
          pendingDeleteMessage.remove();
          pendingDeleteMessage = null;
        }
        hideDeleteConfirm();
      });
    }

    // Member search
    if (memberSearch) {
      memberSearch.addEventListener('input', function () {
        const query = memberSearch.value.trim().toLowerCase();
        const members = document.querySelectorAll('.members .member');
        members.forEach(function (m) {
          const nameEl = m.querySelector('h4');
          const name = nameEl ? nameEl.textContent.toLowerCase() : '';
          m.style.display = name.includes(query) ? '' : 'none';
        });
      });
    }

    // Search icon focuses the search input
    const searchIcon = document.querySelector('.search-icon');
    if (searchIcon && memberSearch) {
      searchIcon.addEventListener('click', function () {
        memberSearch.focus();
      });
    }

    loadMessages();

    // Header action buttons
    const chatActionButtons = document.querySelectorAll('.chat-actions button');
    chatActionButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        const icon = button.querySelector('i');
        if (!icon) return;

        if (icon.classList.contains('fa-phone')) {
          const chatUser = document.querySelector('.chat-header .chat-user h3');
          const name = chatUser ? chatUser.textContent : 'user';
          startAudioCall(name);
          return;
        }
        if (icon.classList.contains('fa-video')) {
          const chatUser = document.querySelector('.chat-header .chat-user h3');
          const name = chatUser ? chatUser.textContent : 'user';
          startVideoCall(name);
          return;
        }
        if (icon.classList.contains('fa-desktop')) {
          const chatUser = document.querySelector('.chat-header .chat-user h3');
          const userName = chatUser ? chatUser.textContent : 'your contact';
          startScreenShare(userName);
          return;
        }
        if (icon.classList.contains('fa-magnifying-glass')) {
          if (memberSearch) memberSearch.focus();
          return;
        }
        if (icon.classList.contains('fa-star')) {
          // toggle favorite visual state
          if (icon.classList.contains('fa-regular')) {
            icon.classList.remove('fa-regular');
            icon.classList.add('fa-solid');
            button.setAttribute('aria-pressed', 'true');
          } else {
            icon.classList.remove('fa-solid');
            icon.classList.add('fa-regular');
            button.setAttribute('aria-pressed', 'false');
          }
          return;
        }
        if (icon.classList.contains('fa-ellipsis-vertical')) {
          alert('More chat actions clicked.');
          return;
        }
      });
    });

    const attachFileInput = document.getElementById('attachFileInput');
    const attachImageInput = document.getElementById('attachImageInput');
    const attachDocInput = document.getElementById('attachDocInput');

    function handleSelectedFiles(files, label) {
      if (!files || files.length === 0) return;
      const names = Array.from(files).map(function (file) {
        return file.name;
      });
      const text = `Attached ${files.length} ${label}: ${names.join(', ')}`;
      const attachmentMessage = createMessageBubble(text, 'sent');
      if (chatWindow) {
        chatWindow.appendChild(attachmentMessage);
        chatWindow.scrollTop = chatWindow.scrollHeight;
      }
    }

    if (attachFileInput) {
      attachFileInput.addEventListener('change', function () {
        handleSelectedFiles(attachFileInput.files, 'file(s)');
        attachFileInput.value = '';
      });
    }

    if (attachImageInput) {
      attachImageInput.addEventListener('change', function () {
        handleSelectedFiles(attachImageInput.files, 'image(s)');
        attachImageInput.value = '';
      });
    }

    if (attachDocInput) {
      attachDocInput.addEventListener('change', function () {
        handleSelectedFiles(attachDocInput.files, 'document(s)');
        attachDocInput.value = '';
      });
    }

    // Attachments and file buttons
    const attachmentButtons = document.querySelectorAll('.message-tools button:not(.emojiBtn)');
    attachmentButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        const icon = button.querySelector('i');
        if (!icon) return;

        if (icon.classList.contains('fa-paperclip')) {
          if (attachFileInput) attachFileInput.click();
          return;
        }
        if (icon.classList.contains('fa-image')) {
          if (attachImageInput) attachImageInput.click();
          return;
        }
        if (icon.classList.contains('fa-file')) {
          if (attachDocInput) attachDocInput.click();
          return;
        }
      });
    });

    // Click entire member item to open the profile drawer
    const memberEls = document.querySelectorAll('.members .member');
    memberEls.forEach(function (memberEl) {
      memberEl.addEventListener('click', function (e) {
        // Ignore clicks originating from selection controls (checkboxes) or inline add buttons
        // Also ignore clicks on any buttons or links inside the member row to avoid accidental profile opens
        if (e.target && e.target.closest && (e.target.closest('.member-select') || e.target.closest('.add-member-btn') || e.target.closest('button') || e.target.closest('a'))) {
          return;
        }
        openProfile(memberEl);
      });
    });

    // --- PROFILE DRAWER INTEGRATION ---
    const profileDrawer = document.getElementById('profileDrawer');
    const drawerClose = document.getElementById('drawerClose');
    const drawerBackdrop = document.getElementById('drawerBackdrop');

    function statusText(s) {
      switch (s) {
        case 'online': return '🟢 Online';
        case 'offline': return '⚫ Offline';
        case 'away': return '🟡 Away';
        case 'dnd': return '⛔ Do Not Disturb';
        default: return '—';
      }
    }

    function openProfile(memberEl) {
      if (!memberEl || !profileDrawer) return;
      const imgEl = document.getElementById('drawerImage');
      const nameEl = document.getElementById('drawerName');
      const statusEl = document.getElementById('drawerStatus');
      const idEl = document.getElementById('drawerId');
      const emailEl = document.getElementById('drawerEmail');
      const phoneEl = document.getElementById('drawerPhone');
      const deptEl = document.getElementById('drawerDept');
      const designationEl = document.getElementById('drawerDesignation');

      const imgQuery = memberEl.querySelector('img');
      const imgSrc = imgQuery ? imgQuery.getAttribute('src') : (memberEl.dataset.img || '');
      if (imgEl && imgSrc) imgEl.src = imgSrc || 'images/emp1.svg';
      if (imgEl) imgEl.alt = memberEl.querySelector('h4') ? memberEl.querySelector('h4').textContent : 'Employee photo';

      if (nameEl) nameEl.textContent = memberEl.querySelector('h4') ? memberEl.querySelector('h4').textContent : (memberEl.dataset.name || 'Name');
      if (statusEl) statusEl.textContent = statusText(memberEl.dataset.status);
      if (idEl) idEl.textContent = `ID: ${memberEl.dataset.id || 'N/A'}`;
      if (emailEl) emailEl.textContent = memberEl.dataset.email || '—';
      if (phoneEl) phoneEl.textContent = memberEl.dataset.phone || '—';
      if (deptEl) deptEl.textContent = memberEl.dataset.dept || '—';
      if (designationEl) designationEl.textContent = memberEl.dataset.designation || '—';

      profileDrawer.classList.add('open');
      profileDrawer.setAttribute('aria-hidden', 'false');
    }

    function closeProfile() {
      if (!profileDrawer) return;
      profileDrawer.classList.remove('open');
      profileDrawer.setAttribute('aria-hidden', 'true');
    }

    if (drawerClose) drawerClose.addEventListener('click', closeProfile);
    if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeProfile);

    const editBtn = document.getElementById('editProfileBtn');
    const messageBtn = document.getElementById('messageProfileBtn');
    const audioBtn = document.getElementById('audioCallBtn');
    const videoBtn = document.getElementById('videoCallBtn');
    const shareScreenBtn = document.getElementById('shareScreenBtn');
    const stopScreenShareBtn = document.getElementById('stopScreenShareBtn');
 
    if (editBtn) {
      editBtn.addEventListener('click', function () {
        alert('Edit Profile — open edit UI here (not implemented).');
      });
    }
 
    if (messageBtn) {
      messageBtn.addEventListener('click', function () {
        const name = document.getElementById('drawerName') ? document.getElementById('drawerName').textContent : '';
        const imageSrc = document.getElementById('drawerImage') ? document.getElementById('drawerImage').getAttribute('src') : '';
        const statusTextVal = document.getElementById('drawerStatus') ? document.getElementById('drawerStatus').textContent : '';
        const chatUserName = document.querySelector('.chat-header .chat-user h3');
        const chatUserImg = document.querySelector('.chat-header .chat-user img');
        const chatStatusSpan = document.querySelector('.chat-header .chat-user .online-status');
        if (chatUserName) chatUserName.textContent = name;
        if (chatUserImg && imageSrc) chatUserImg.src = imageSrc;
        if (chatStatusSpan) chatStatusSpan.textContent = statusTextVal;
        closeProfile();
        if (messageInput) messageInput.focus();
      });
    }
 
    // Call UI / media handling (demo)
    let currentCallStream = null;
    let screenShareStream = null;

    function makeCallOverlay(title, videoStream, showVideo) {
      const overlay = document.createElement('div');
      overlay.className = 'call-overlay';
      overlay.style = 'position:fixed;inset:0;background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;z-index:2000;';
      const box = document.createElement('div');
      box.style = 'background:#fff;padding:12px;border-radius:8px;max-width:90%;width:640px;box-shadow:0 10px 40px rgba(0,0,0,0.4);';
      const h = document.createElement('h3'); h.textContent = title; box.appendChild(h);
      if (showVideo) {
        const v = document.createElement('video');
        v.autoplay = true; v.muted = true; v.style = 'width:100%;border-radius:6px;background:#000;';
        v.srcObject = videoStream || null;
        box.appendChild(v);
      }
      const hang = document.createElement('button'); hang.textContent = 'Hang up'; hang.className = 'btn primary'; hang.style = 'margin-top:8px;';
      hang.addEventListener('click', function () {
        if (videoStream) { videoStream.getTracks().forEach(t => t.stop()); }
        overlay.remove();
      });
      box.appendChild(hang);
      overlay.appendChild(box);
      document.body.appendChild(overlay);
      return overlay;
    }

    async function startAudioCall(name) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        currentCallStream = stream;
        makeCallOverlay('Audio call — ' + name, null, false);
      } catch (err) {
        alert('Unable to start audio call: ' + err.message);
      }
    }

    async function startVideoCall(name) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        currentCallStream = stream;
        makeCallOverlay('Video call — ' + name, stream, true);
      } catch (err) {
        alert('Unable to start video call: ' + err.message);
      }
    }

    async function startScreenShare(name) {
      try {
        const s = await navigator.mediaDevices.getDisplayMedia({ video: true });
        screenShareStream = s;
        // show share in banner area
        const banner = document.getElementById('screenShareBanner');
        if (!banner) return;
        banner.innerHTML = '';
        const video = document.createElement('video');
        video.autoplay = true; video.muted = true; video.style = 'width:100%;max-height:240px;';
        video.srcObject = s;
        const stopBtn = document.createElement('button'); stopBtn.className = 'btn primary'; stopBtn.textContent = 'Stop sharing';
        stopBtn.addEventListener('click', function () { stopScreenShare(); });
        banner.appendChild(document.createTextNode('Sharing your screen: ' + name));
        banner.appendChild(video);
        banner.appendChild(stopBtn);
        banner.style.display = 'flex';
        s.getVideoTracks()[0].addEventListener('ended', stopScreenShare);
      } catch (err) {
        alert('Screen share failed: ' + err.message);
      }
    }

    function stopScreenShare() {
      if (screenShareStream) {
        screenShareStream.getTracks().forEach(t => t.stop());
        screenShareStream = null;
      }
      const banner = document.getElementById('screenShareBanner');
      if (banner) { banner.style.display = 'none'; banner.innerHTML = '';} 
    }

    if (audioBtn) {
      audioBtn.addEventListener('click', function () {
        const drawerNameEl = document.getElementById('drawerName');
        const drawerName = drawerNameEl ? drawerNameEl.textContent : 'user';
        startAudioCall(drawerName);
      });
    }

    if (videoBtn) {
      videoBtn.addEventListener('click', function () {
        const drawerNameEl = document.getElementById('drawerName');
        const drawerName = drawerNameEl ? drawerNameEl.textContent : 'user';
        startVideoCall(drawerName);
      });
    }

    if (shareScreenBtn) {
      shareScreenBtn.addEventListener('click', function () {
        const drawerNameEl = document.getElementById('drawerName');
        const drawerName = drawerNameEl ? drawerNameEl.textContent : 'your contact';
        startScreenShare(drawerName);
      });
    }
 
    if (stopScreenShareBtn) {
      stopScreenShareBtn.addEventListener('click', function () {
        stopScreenShare();
      });
    }

  } catch (err) {
    // Log initialization errors without breaking the rest of the page
    console.error('Initialization error in script.js:', err);
  }
});

// Small helper to ensure emoji picker is hidden by default via class
(function ensureStyles() {
  // If CSS does not control .emoji-picker.visible, add minimal inline style rules to avoid broken UI
  const styleId = 'teamchat-inline-fix';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .emoji-picker { display: none; position: absolute; bottom: 70px; right: 20px; background: #fff; border: 1px solid #ddd; padding: 8px; border-radius: 8px; box-shadow: 0 6px 18px rgba(0,0,0,0.08); max-width: 320px; z-index: 1000; }
      .emoji-picker.visible { display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; }
      .emoji-picker button { background: transparent; border: none; font-size: 18px; cursor: pointer; }
      .message-box { position: relative; }
    `;
    document.head.appendChild(style);
  }
})();