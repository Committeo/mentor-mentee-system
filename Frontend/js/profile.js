// ============================
// PROFILE MODULE
// Shared across mentor / mentee / admin dashboards
// ============================
const Profile = (() => {
    const API = "http://127.0.0.1:8000";
    let currentUser = null;

    function init(user) {
        currentUser = user;
        _injectStyles();
        _buildModal();
        _buildCornerBtn();
    }

    function _buildCornerBtn() {
        const btn = document.createElement("div");
        btn.id = "profile-corner-btn";
        btn.title = "My Profile";
        const initial = (currentUser?.name || "U").charAt(0).toUpperCase();
        btn.innerHTML = `<span>${initial}</span>`;
        btn.onclick = () => openProfile();
        // Append to header-controls if it exists, else body
        const hc = document.querySelector(".header-controls");
        if (hc) hc.appendChild(btn);
        else document.body.appendChild(btn);
    }

    async function openProfile() {
        const res = await fetch(`${API}/profile/${currentUser.id}`);
        const data = await res.json();
        if (!data.success) { alert("Failed to load profile"); return; }
        const u = data.user;

        let extraHtml = "";
        if (u.assigned_mentors?.length) {
            extraHtml = `<div class="pf-info-row"><span class="pf-label"><i class="fas fa-chalkboard-teacher"></i> Mentor(s)</span>
                <span class="pf-val">${u.assigned_mentors.map(m => m.name).join(", ")}</span></div>`;
        }
        if (u.assigned_mentees?.length) {
            extraHtml = `<div class="pf-info-row"><span class="pf-label"><i class="fas fa-user-graduate"></i> Mentees</span>
                <span class="pf-val">${u.assigned_mentees.map(m => m.name).join(", ")}</span></div>`;
        }

        document.getElementById("pf-avatar-letter").textContent = u.name.charAt(0).toUpperCase();
        document.getElementById("pf-name").textContent = u.name;
        document.getElementById("pf-role-badge").textContent = u.role.charAt(0).toUpperCase() + u.role.slice(1);
        document.getElementById("pf-role-badge").className = "pf-role-badge pf-role-" + u.role;
        document.getElementById("pf-info-rows").innerHTML = `
            <div class="pf-info-row"><span class="pf-label"><i class="fas fa-envelope"></i> Email</span><span class="pf-val">${u.email}</span></div>
            <div class="pf-info-row"><span class="pf-label"><i class="fas fa-building"></i> Department</span><span class="pf-val">${u.dep || "—"}</span></div>
            <div class="pf-info-row"><span class="pf-label"><i class="fas fa-id-badge"></i> User ID</span><span class="pf-val">#${u.id}</span></div>
            ${extraHtml}`;

        _showTab("view");
        document.getElementById("pf-overlay").style.display = "flex";
    }

    function _showTab(tab) {
        document.querySelectorAll(".pf-tab-content").forEach(t => t.style.display = "none");
        document.querySelectorAll(".pf-tab-btn").forEach(b => b.classList.remove("active"));
        document.getElementById("pf-tab-" + tab).style.display = "block";
        document.querySelector(`.pf-tab-btn[data-tab="${tab}"]`)?.classList.add("active");
    }

    async function saveProfile() {
        const name = document.getElementById("pf-edit-name").value.trim();
        const dep  = document.getElementById("pf-edit-dep").value.trim();
        const pass = document.getElementById("pf-edit-pass").value.trim();
        const msg  = document.getElementById("pf-edit-msg");
        if (!name) { msg.textContent = "Name cannot be empty"; msg.style.color = "#e74c3c"; return; }
        const res = await fetch(`${API}/profile/${currentUser.id}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({name, dep, password: pass || undefined})
        });
        const data = await res.json();
        if (data.success) {
            msg.textContent = "Profile updated!"; msg.style.color = "#27ae60";
            currentUser.name = data.user.name; currentUser.dep = data.user.dep;
            localStorage.setItem("user", JSON.stringify(currentUser));
            const wt = document.getElementById("welcome-text");
            if (wt) wt.textContent = "Welcome, " + currentUser.name;
            document.getElementById("profile-corner-btn").querySelector("span").textContent = currentUser.name.charAt(0).toUpperCase();
            setTimeout(() => openProfile(), 800);
        } else {
            msg.textContent = data.message; msg.style.color = "#e74c3c";
        }
    }

    async function deleteAccount() {
        if (!confirm("Are you sure you want to permanently delete your account? This cannot be undone.")) return;
        const res = await fetch(`${API}/profile/${currentUser.id}`, { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
            alert("Account deleted.");
            localStorage.clear();
            window.location.href = "login.html";
        } else {
            alert(data.message || "Delete failed");
        }
    }

    function _buildModal() {
        const overlay = document.createElement("div");
        overlay.id = "pf-overlay";
        overlay.innerHTML = `
        <div class="pf-modal">
            <button class="pf-close" onclick="document.getElementById('pf-overlay').style.display='none'">
                <i class="fas fa-times"></i>
            </button>
            <div class="pf-header">
                <div class="pf-avatar" id="pf-avatar-letter">U</div>
                <div>
                    <div class="pf-name" id="pf-name">User</div>
                    <span class="pf-role-badge" id="pf-role-badge">User</span>
                </div>
            </div>
            <div class="pf-tabs">
                <button class="pf-tab-btn active" data-tab="view" onclick="Profile._showTab('view')"><i class="fas fa-user"></i> Profile</button>
                <button class="pf-tab-btn" data-tab="edit" onclick="Profile._showTab('edit');Profile._fillEditForm()"><i class="fas fa-edit"></i> Edit</button>
                <button class="pf-tab-btn" data-tab="settings" onclick="Profile._showTab('settings')"><i class="fas fa-cog"></i> Settings</button>
            </div>

            <!-- VIEW TAB -->
            <div id="pf-tab-view" class="pf-tab-content">
                <div id="pf-info-rows"></div>
            </div>

            <!-- EDIT TAB -->
            <div id="pf-tab-edit" class="pf-tab-content" style="display:none;">
                <div class="pf-form-group">
                    <label>Full Name</label>
                    <input type="text" id="pf-edit-name" placeholder="Your name">
                </div>
                <div class="pf-form-group">
                    <label>Department</label>
                    <input type="text" id="pf-edit-dep" placeholder="Your department">
                </div>
                <div class="pf-form-group">
                    <label>New Password <small>(leave blank to keep current)</small></label>
                    <input type="password" id="pf-edit-pass" placeholder="New password">
                </div>
                <p id="pf-edit-msg" style="font-size:0.85rem; margin-top:0.5rem;"></p>
                <button class="pf-btn pf-btn-save" onclick="Profile.saveProfile()"><i class="fas fa-save"></i> Save Changes</button>
            </div>

            <!-- SETTINGS TAB -->
            <div id="pf-tab-settings" class="pf-tab-content" style="display:none;">
                <div class="pf-settings-section">
                    <div class="pf-settings-title"><i class="fas fa-bell"></i> Notifications</div>
                    <label class="pf-toggle-row">
                        <span>Message notifications</span>
                        <input type="checkbox" id="s-notif-msg" checked onchange="Profile._saveSetting('notif_msg', this.checked)">
                    </label>
                    <label class="pf-toggle-row">
                        <span>Task reminders</span>
                        <input type="checkbox" id="s-notif-task" checked onchange="Profile._saveSetting('notif_task', this.checked)">
                    </label>
                </div>
                <div class="pf-settings-section">
                    <div class="pf-settings-title"><i class="fas fa-palette"></i> Appearance</div>
                    <label class="pf-toggle-row">
                        <span>Compact sidebar</span>
                        <input type="checkbox" id="s-compact" onchange="Profile._toggleCompact(this.checked)">
                    </label>
                </div>
                <div class="pf-settings-section">
                    <div class="pf-settings-title"><i class="fas fa-shield-alt"></i> Account</div>
                    <button class="pf-btn pf-btn-danger" onclick="Profile.deleteAccount()">
                        <i class="fas fa-trash-alt"></i> Delete My Account
                    </button>
                    <button class="pf-btn pf-btn-secondary" onclick="localStorage.clear(); window.location.href='login.html';" style="margin-top:0.5rem;">
                        <i class="fas fa-sign-out-alt"></i> Log Out
                    </button>
                </div>
            </div>
        </div>`;
        document.body.appendChild(overlay);
        overlay.addEventListener("click", e => { if (e.target === overlay) overlay.style.display = "none"; });
        _loadSettings();
    }

    function _fillEditForm() {
        document.getElementById("pf-edit-name").value = currentUser.name || "";
        document.getElementById("pf-edit-dep").value  = currentUser.dep  || "";
        document.getElementById("pf-edit-pass").value = "";
        document.getElementById("pf-edit-msg").textContent = "";
    }

    function _saveSetting(key, value) {
        const settings = JSON.parse(localStorage.getItem("pf_settings") || "{}");
        settings[key] = value;
        localStorage.setItem("pf_settings", JSON.stringify(settings));
    }

    function _loadSettings() {
        const settings = JSON.parse(localStorage.getItem("pf_settings") || "{}");
        if (document.getElementById("s-notif-msg")) document.getElementById("s-notif-msg").checked = settings.notif_msg !== false;
        if (document.getElementById("s-notif-task")) document.getElementById("s-notif-task").checked = settings.notif_task !== false;
        if (settings.compact) _toggleCompact(true);
    }

    function _toggleCompact(on) {
        _saveSetting("compact", on);
        document.querySelector(".sidebar")?.classList.toggle("compact-sidebar", on);
        if (document.getElementById("s-compact")) document.getElementById("s-compact").checked = on;
    }

    function _injectStyles() {
        if (document.getElementById("pf-styles")) return;
        const style = document.createElement("style");
        style.id = "pf-styles";
        style.textContent = `
        #profile-corner-btn {
            width:40px; height:40px; border-radius:50%; background:linear-gradient(135deg,#1abc9c,#3498db);
            display:flex; align-items:center; justify-content:center; cursor:pointer;
            color:#fff; font-weight:700; font-size:1.1rem; flex-shrink:0;
            box-shadow:0 2px 8px rgba(0,0,0,0.3); transition:transform 0.2s;
            border:2px solid rgba(255,255,255,0.3);
        }
        #profile-corner-btn:hover { transform:scale(1.1); }
        #pf-overlay {
            display:none; position:fixed; inset:0; background:rgba(0,0,0,0.55);
            z-index:9999; align-items:center; justify-content:center; padding:1rem;
        }
        .pf-modal {
            background:#fff; border-radius:16px; width:100%; max-width:440px;
            max-height:90vh; overflow-y:auto; padding:2rem; position:relative;
            box-shadow:0 20px 60px rgba(0,0,0,0.25);
        }
        .pf-close {
            position:absolute; top:1rem; right:1rem; background:none; border:none;
            cursor:pointer; color:#999; font-size:1.2rem; padding:0.3rem;
        }
        .pf-close:hover { color:#e74c3c; }
        .pf-header { display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem; }
        .pf-avatar {
            width:60px; height:60px; border-radius:50%;
            background:linear-gradient(135deg,#1abc9c,#3498db);
            display:flex; align-items:center; justify-content:center;
            color:#fff; font-size:1.6rem; font-weight:700; flex-shrink:0;
        }
        .pf-name { font-size:1.25rem; font-weight:700; color:#2c3e50; }
        .pf-role-badge {
            display:inline-block; padding:0.2rem 0.8rem; border-radius:20px;
            font-size:0.8rem; font-weight:600; margin-top:0.3rem;
        }
        .pf-role-mentor  { background:#e8f5e9; color:#2e7d32; }
        .pf-role-mentee  { background:#e3f2fd; color:#1565c0; }
        .pf-role-admin   { background:#fce4ec; color:#c62828; }
        .pf-tabs { display:flex; gap:0.5rem; margin-bottom:1.5rem; border-bottom:2px solid #f0f0f0; padding-bottom:0.75rem; }
        .pf-tab-btn {
            flex:1; padding:0.5rem; border:none; background:#f8f9fa; border-radius:8px;
            cursor:pointer; font-size:0.85rem; color:#666; transition:all 0.2s;
            display:flex; align-items:center; justify-content:center; gap:0.3rem;
        }
        .pf-tab-btn.active { background:linear-gradient(135deg,#1abc9c,#3498db); color:#fff; }
        .pf-tab-btn:hover:not(.active) { background:#e9ecef; }
        .pf-info-row {
            display:flex; justify-content:space-between; align-items:flex-start;
            padding:0.75rem 0; border-bottom:1px solid #f0f0f0;
        }
        .pf-info-row:last-child { border-bottom:none; }
        .pf-label { color:#888; font-size:0.9rem; display:flex; align-items:center; gap:0.4rem; }
        .pf-val { color:#2c3e50; font-weight:500; text-align:right; max-width:60%; }
        .pf-form-group { margin-bottom:1rem; }
        .pf-form-group label { display:block; color:#555; font-size:0.9rem; margin-bottom:0.3rem; font-weight:500; }
        .pf-form-group input {
            width:100%; padding:0.65rem 1rem; border:1px solid #ddd;
            border-radius:8px; outline:none; font-size:0.95rem;
        }
        .pf-form-group input:focus { border-color:#3498db; }
        .pf-btn {
            width:100%; padding:0.7rem; border:none; border-radius:8px;
            cursor:pointer; font-size:0.95rem; font-weight:600; transition:all 0.2s;
            display:flex; align-items:center; justify-content:center; gap:0.5rem;
        }
        .pf-btn-save { background:linear-gradient(135deg,#1abc9c,#3498db); color:#fff; }
        .pf-btn-save:hover { opacity:0.9; }
        .pf-btn-danger { background:#e74c3c; color:#fff; }
        .pf-btn-danger:hover { background:#c0392b; }
        .pf-btn-secondary { background:#95a5a6; color:#fff; }
        .pf-btn-secondary:hover { background:#7f8c8d; }
        .pf-settings-section { margin-bottom:1.5rem; }
        .pf-settings-title { font-weight:600; color:#2c3e50; margin-bottom:0.75rem; display:flex; align-items:center; gap:0.4rem; }
        .pf-toggle-row {
            display:flex; justify-content:space-between; align-items:center;
            padding:0.5rem 0; border-bottom:1px solid #f5f5f5; cursor:pointer; color:#555;
        }
        .compact-sidebar .sidebar nav ul li span,
        .compact-sidebar .sidebar nav ul li { font-size:0; }
        .compact-sidebar .sidebar { width:60px; }
        .compact-sidebar .sidebar nav ul li i { font-size:1.2rem; margin:0 auto; }
        `;
        document.head.appendChild(style);
    }

    return { init, openProfile, saveProfile, deleteAccount, _showTab, _fillEditForm, _saveSetting, _toggleCompact };
})();
