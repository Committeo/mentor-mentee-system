// ============================
// MESSENGER MODULE
// ============================
const Messenger = (() => {
    let currentUser = null;
    let selectedContact = null;
    let pollInterval = null;

    const API = "http://127.0.0.1:8000";

    function init(user) {
        currentUser = user;
        loadContacts();
        startPolling();
    }

    async function loadContacts() {
        const list = document.getElementById("contact-list-items");
        if (!list) return;
        try {
            const res = await fetch(`${API}/messages/contacts/${currentUser.id}`);
            const contacts = await res.json();
            list.innerHTML = "";
            if (contacts.length === 0) {
                list.innerHTML = `<div class="empty-contacts">No contacts yet.<br>Ask admin to assign a ${currentUser.role === 'mentor' ? 'mentee' : 'mentor'}.</div>`;
                return;
            }
            contacts.forEach(c => {
                const initial = c.name.charAt(0).toUpperCase();
                const div = document.createElement("div");
                div.className = "contact-item" + (selectedContact?.id === c.id ? " active" : "");
                div.innerHTML = `
                    <div class="contact-avatar ${c.role}">${initial}</div>
                    <div class="contact-info">
                        <div class="contact-name">${c.name}</div>
                        <div class="contact-role">${c.role} · ${c.dep || ""}</div>
                    </div>
                    ${c.unread > 0 ? `<div class="unread-badge">${c.unread}</div>` : ""}
                `;
                div.onclick = () => openChat(c, div);
                list.appendChild(div);
            });
        } catch (e) {
            console.error("Failed to load contacts:", e);
        }
    }

    function openChat(contact, el) {
        selectedContact = contact;
        document.querySelectorAll(".contact-item").forEach(i => i.classList.remove("active"));
        el.classList.add("active");

        const header = document.getElementById("chat-header-name");
        const sub = document.getElementById("chat-header-role");
        if (header) header.textContent = contact.name;
        if (sub) sub.textContent = `${contact.role} · ${contact.dep || ""}`;

        const noChat = document.getElementById("no-chat-selected");
        const chatContent = document.getElementById("chat-content");
        if (noChat) noChat.style.display = "none";
        if (chatContent) chatContent.style.display = "flex";

        loadMessages();
    }

    async function loadMessages() {
        if (!selectedContact) return;
        const msgs = document.getElementById("chat-messages");
        if (!msgs) return;
        try {
            const res = await fetch(`${API}/messages/conversation/${currentUser.id}/${selectedContact.id}`);
            const data = await res.json();
            msgs.innerHTML = "";
            data.forEach(m => {
                const isSent = m.sender_id === currentUser.id;
                const time = new Date(m.created_at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"});
                const div = document.createElement("div");
                div.className = `message-bubble ${isSent ? "sent" : "received"}`;
                div.innerHTML = `${m.message}<div class="message-time">${time}</div>`;
                msgs.appendChild(div);
            });
            msgs.scrollTop = msgs.scrollHeight;
            // Refresh contact list to clear unread badge
            loadContacts();
        } catch (e) {
            console.error("Failed to load messages:", e);
        }
    }

    async function sendMessage() {
        const input = document.getElementById("msg-input");
        if (!input || !selectedContact) return;
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        try {
            await fetch(`${API}/messages/send`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    sender_id: currentUser.id,
                    receiver_id: selectedContact.id,
                    message: text
                })
            });
            loadMessages();
        } catch (e) {
            console.error("Send failed:", e);
        }
    }

    function startPolling() {
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(() => {
            loadContacts();
            if (selectedContact) loadMessages();
        }, 4000);
    }

    // Enter key to send
    document.addEventListener("keydown", e => {
        if (e.key === "Enter" && document.activeElement?.id === "msg-input") {
            sendMessage();
        }
    });

    return { init, sendMessage, loadContacts };
})();
