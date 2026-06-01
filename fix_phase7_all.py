import os

# ── HELPER ──────────────────────────────────────────────────────


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Written: ' + path)


# ════════════════════════════════════════════════════════════════
# BASE.HTML — Dark Academia theme + notification auto-refresh
# ════════════════════════════════════════════════════════════════
base = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{% block title %}CampusGrid{% endblock %} — UEAB</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=EB+Garamond:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --bg-primary:    #1A1612;
      --bg-secondary:  #2C2416;
      --bg-sidebar:    #211C14;
      --accent:        #C9A84C;
      --accent-warm:   #8B6914;
      --accent-green:  #4A7C59;
      --accent-red:    #8B3A3A;
      --accent-orange: #A0522D;
      --accent-amber:  #C17D2A;
      --text-primary:  #E8DCC8;
      --text-muted:    #9C8F7A;
      --border:        #3D3426;
      --card-bg:       #241E15;
    }
    * { box-sizing: border-box; }
    body {
      background: var(--bg-primary);
      color: var(--text-primary);
      font-family: 'Inter', 'Segoe UI', sans-serif;
      min-height: 100vh;
      display: flex;
      margin: 0;
    }
    h1,h2,h3,h4,h5,h6 { font-family: 'EB Garamond', serif; }

    /* ── SIDEBAR ── */
    .sidebar {
      width: 240px;
      min-height: 100vh;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0; left: 0;
      z-index: 100;
    }
    .sidebar-brand {
      padding: 24px 20px 16px;
      border-bottom: 1px solid var(--border);
    }
    .sidebar-brand .brand-name {
      font-family: 'EB Garamond', serif;
      font-size: 1.6rem;
      font-weight: 600;
      color: var(--accent);
      letter-spacing: 0.5px;
    }
    .sidebar-brand .brand-sub {
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 1.5px;
    }
    .sidebar-nav { flex: 1; padding: 16px 0; }
    .nav-item-link {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 20px;
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.875rem;
      border-left: 3px solid transparent;
      transition: all 0.15s;
      font-family: 'Inter', sans-serif;
    }
    .nav-item-link:hover { color: var(--text-primary); background: rgba(201,168,76,0.06); }
    .nav-item-link.active { color: var(--accent); border-left-color: var(--accent); background: rgba(201,168,76,0.1); }
    .nav-item-link i { font-size: 1rem; width: 20px; }
    .sidebar-user { padding: 16px 20px; border-top: 1px solid var(--border); }
    .user-role-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 0.62rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .role-admin     { background: rgba(139,58,58,0.2);  color: #D4908A; }
    .role-approver  { background: rgba(193,125,42,0.2); color: #D4A96A; }
    .role-requester { background: rgba(74,124,89,0.2);  color: #86B89A; }

    /* ── MAIN ── */
    .main-content {
      margin-left: 240px;
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .topbar {
      height: 60px;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      position: sticky;
      top: 0;
      z-index: 99;
    }
    .topbar-title {
      font-family: 'EB Garamond', serif;
      font-size: 1.15rem;
      font-weight: 600;
      color: var(--text-primary);
      letter-spacing: 0.3px;
    }
    .notification-bell {
      position: relative;
      color: var(--text-muted);
      font-size: 1.1rem;
      cursor: pointer;
      text-decoration: none;
      transition: color 0.15s;
    }
    .notification-bell:hover { color: var(--accent); }
    .notif-badge {
      position: absolute;
      top: -4px; right: -6px;
      background: var(--accent-red);
      color: #E8DCC8;
      font-size: 0.55rem;
      font-weight: 700;
      width: 15px; height: 15px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .page-content { flex: 1; padding: 24px; }

    /* ── CARDS ── */
    .cg-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
    }
    .cg-card-title {
      font-family: 'EB Garamond', serif;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }

    /* ── STAT CARDS ── */
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .stat-icon {
      width: 46px; height: 46px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
    }
    .stat-value { font-family: 'EB Garamond', serif; font-size: 2rem; font-weight: 600; line-height: 1; color: var(--accent); }
    .stat-label { font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; }

    /* ── BUTTONS ── */
    .btn-cg-primary {
      background: var(--accent);
      color: #1A1612;
      border: none;
      border-radius: 4px;
      padding: 8px 18px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.15s;
      text-decoration: none;
      display: inline-block;
      font-family: 'Inter', sans-serif;
      letter-spacing: 0.3px;
    }
    .btn-cg-primary:hover { opacity: 0.85; color: #1A1612; }
    .btn-cg-outline {
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--accent);
      border-radius: 4px;
      padding: 8px 18px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
      text-decoration: none;
      display: inline-block;
    }
    .btn-cg-outline:hover { background: var(--accent); color: #1A1612; }
    .btn-cg-danger {
      background: rgba(139,58,58,0.15);
      color: #D4908A;
      border: 1px solid rgba(139,58,58,0.3);
      border-radius: 4px;
      padding: 6px 14px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-cg-danger:hover { background: rgba(139,58,58,0.3); }

    /* ── FORMS ── */
    .cg-input {
      background: var(--bg-primary);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text-primary);
      padding: 10px 14px;
      width: 100%;
      font-size: 0.875rem;
      transition: border-color 0.15s;
      font-family: 'Inter', sans-serif;
    }
    .cg-input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(201,168,76,0.1);
    }
    .cg-input::placeholder { color: var(--text-muted); }
    .cg-input option { background: var(--bg-secondary); }
    .cg-label {
      font-size: 0.78rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* ── STATUS BADGES ── */
    .badge-pending   { background: rgba(193,125,42,0.15);  color: #D4A96A; }
    .badge-approved  { background: rgba(74,124,89,0.15);   color: #86B89A; }
    .badge-rejected  { background: rgba(139,58,58,0.15);   color: #D4908A; }
    .badge-cancelled { background: rgba(156,143,122,0.15); color: #9C8F7A; }
    .badge-displaced { background: rgba(160,82,45,0.15);   color: #C4885A; }
    .badge-priority  { background: rgba(139,58,58,0.25);   color: #D4908A; }
    .status-badge {
      padding: 3px 10px;
      border-radius: 3px;
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    /* ── ALERTS ── */
    .cg-alert {
      border-radius: 4px;
      padding: 12px 16px;
      font-size: 0.85rem;
      margin-bottom: 16px;
      border-left: 3px solid;
    }
    .cg-alert-error   { background: rgba(139,58,58,0.1);   border-color: #8B3A3A;  color: #D4908A; }
    .cg-alert-success { background: rgba(74,124,89,0.1);   border-color: #4A7C59;  color: #86B89A; }
    .cg-alert-info    { background: rgba(201,168,76,0.08); border-color: #C9A84C;  color: #D4B96C; }
    .cg-alert-warning { background: rgba(193,125,42,0.1);  border-color: #C17D2A;  color: #D4A96A; }

    /* ── SKELETON LOADER ── */
    .skeleton {
      background: linear-gradient(90deg, var(--border) 25%, var(--bg-secondary) 50%, var(--border) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 4px;
    }
    @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

    /* ── TABLE ── */
    .cg-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .cg-table th { padding: 10px 12px; text-align: left; color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--border); font-weight: 500; }
    .cg-table td { padding: 12px; border-bottom: 1px solid var(--border); }
    .cg-table tr:hover td { background: rgba(201,168,76,0.03); }

    /* ── DIVIDER ── */
    .cg-divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

    {% block extra_styles %}{% endblock %}
  </style>
</head>
<body>

{% if user.is_authenticated %}
<aside class="sidebar">
  <div class="sidebar-brand">
    <div class="brand-name">CampusGrid</div>
    <div class="brand-sub">UEAB &middot; Facility Booking</div>
  </div>
  <nav class="sidebar-nav">
    <a href="/calendar/"      class="nav-item-link {% if page == 'calendar' %}active{% endif %}"><i class="bi bi-calendar-week"></i> Calendar</a>
    <a href="/dashboard/"     class="nav-item-link {% if page == 'dashboard' %}active{% endif %}"><i class="bi bi-grid-1x2"></i> Dashboard</a>
    <a href="/bookings/"      class="nav-item-link {% if page == 'bookings' %}active{% endif %}"><i class="bi bi-journal-bookmark"></i> My Bookings</a>
    <a href="/bookings/new/"  class="nav-item-link"><i class="bi bi-plus-circle"></i> New Booking</a>
    <a href="/facilities/"    class="nav-item-link {% if page == 'facilities' %}active{% endif %}"><i class="bi bi-building"></i> Facilities</a>
    {% if user.role == 'approver' or user.role == 'admin' %}
    <a href="/approvals/"     class="nav-item-link {% if page == 'approvals' %}active{% endif %}">
      <i class="bi bi-check2-circle"></i> Approvals
      <span id="pending-count-badge" class="ms-auto" style="background:rgba(193,125,42,0.2);color:#D4A96A;padding:1px 7px;border-radius:3px;font-size:0.65rem;font-weight:600;display:none;"></span>
    </a>
    <a href="/reports/"       class="nav-item-link {% if page == 'reports' %}active{% endif %}"><i class="bi bi-bar-chart-line"></i> Reports</a>
    {% endif %}
    <a href="/notifications/" class="nav-item-link {% if page == 'notifications' %}active{% endif %}"><i class="bi bi-bell"></i> Notifications</a>
    {% if user.role == 'admin' %}
    <a href="/users/"         class="nav-item-link {% if page == 'users' %}active{% endif %}"><i class="bi bi-people"></i> User Management</a>
    <a href="/admin/"         class="nav-item-link"><i class="bi bi-shield-lock"></i> Admin Panel</a>
    {% endif %}
  </nav>
  <div class="sidebar-user">
    <div style="font-size:0.85rem;font-weight:600;margin-bottom:2px;color:var(--text-primary);">{{ user.get_full_name|default:user.username }}</div>
    <div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:8px;font-family:'Inter',monospace;">{{ user.institutional_id }}</div>
    <span class="user-role-badge role-{{ user.role }}">{{ user.role }}</span>
    <a href="/logout/" style="display:block;margin-top:12px;font-size:0.78rem;color:var(--text-muted);text-decoration:none;transition:color 0.15s;" onmouseover="this.style.color='var(--accent)'" onmouseout="this.style.color='var(--text-muted)'">
      <i class="bi bi-box-arrow-left me-1"></i> Sign out
    </a>
  </div>
</aside>

<div class="main-content">
  <div class="topbar">
    <div class="topbar-title">{% block page_title %}CampusGrid{% endblock %}</div>
    <div class="d-flex align-items-center gap-3">
      <span style="font-size:0.78rem;color:var(--text-muted);font-family:'Inter',monospace;">{{ user.institutional_id }}</span>
      <a href="/notifications/" class="notification-bell">
        <i class="bi bi-bell"></i>
        <span id="notif-badge" class="notif-badge" style="display:none;"></span>
      </a>
    </div>
  </div>
  <div class="page-content">
    {% block content %}{% endblock %}
  </div>
</div>

{% else %}
{% block auth_content %}{% endblock %}
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
const API = {
  baseURL: '/api',
  getToken()  { return localStorage.getItem('cg_access_token'); },
  setTokens(access, refresh) {
    localStorage.setItem('cg_access_token', access);
    localStorage.setItem('cg_refresh_token', refresh);
  },
  clearTokens() {
    localStorage.removeItem('cg_access_token');
    localStorage.removeItem('cg_refresh_token');
  },
  async request(method, endpoint, data=null) {
    const headers = { 'Content-Type': 'application/json' };
    const token   = this.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const config  = { method, headers };
    if (data) config.body = JSON.stringify(data);
    const res = await fetch(this.baseURL + endpoint, config);
    if (res.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) return this.request(method, endpoint, data);
      window.location.href = '/';
      return;
    }
    return res;
  },
  async refreshToken() {
    const refresh = localStorage.getItem('cg_refresh_token');
    if (!refresh) return false;
    const res = await fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('cg_access_token', data.access);
      return true;
    }
    return false;
  },
  get(endpoint)         { return this.request('GET',    endpoint); },
  post(endpoint, data)  { return this.request('POST',   endpoint, data); },
  patch(endpoint, data) { return this.request('PATCH',  endpoint, data); },
  delete(endpoint)      { return this.request('DELETE', endpoint); },
};

async function loadNotifCount() {
  try {
    const res = await API.get('/notifications/unread-count/');
    if (res && res.ok) {
      const data  = await res.json();
      const badge = document.getElementById('notif-badge');
      if (badge && data.unread_count > 0) {
        badge.textContent = data.unread_count;
        badge.style.display = 'flex';
      } else if (badge) {
        badge.style.display = 'none';
      }
      const pb = document.getElementById('pending-count-badge');
      if (pb) {
        const ar = await API.get('/approvals/pending/');
        if (ar && ar.ok) {
          const ad = await ar.json();
          if (ad.count > 0) {
            pb.textContent = ad.count;
            pb.style.display = 'inline';
          } else {
            pb.style.display = 'none';
          }
        }
      }
    }
  } catch(e) {}
}

{% if user.is_authenticated %}
loadNotifCount();
// Auto-refresh notification count every 60 seconds
setInterval(loadNotifCount, 60000);
{% endif %}
</script>
{% block extra_scripts %}{% endblock %}
</body>
</html>
"""

# ════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════
login_html = """\
{% extends 'base.html' %}
{% block auth_content %}
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-primary);width:100%;">
  <div style="width:100%;max-width:420px;padding:24px;">
    <div style="text-align:center;margin-bottom:40px;">
      <div style="font-family:'EB Garamond',serif;font-size:2.8rem;font-weight:600;color:var(--accent);letter-spacing:1px;">CampusGrid</div>
      <div style="width:60px;height:1px;background:var(--border);margin:12px auto;"></div>
      <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:2.5px;">University of Eastern Africa Baraton</div>
    </div>
    <div class="cg-card">
      <h5 style="font-family:'EB Garamond',serif;font-size:1.3rem;font-weight:600;margin-bottom:4px;">Sign in</h5>
      <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">Use your institutional ID and password to continue.</p>
      {% if messages %}
        {% for message in messages %}
          <div class="cg-alert cg-alert-info"><i class="bi bi-info-circle me-2"></i>{{ message }}</div>
        {% endfor %}
      {% endif %}
      <form method="POST" action="/">
        {% csrf_token %}
        <div style="margin-bottom:16px;">
          <label class="cg-label">Student ID / Staff ID</label>
          <input type="text" name="username" class="cg-input" placeholder="e.g. SGATWI2311" required autofocus/>
        </div>
        <div style="margin-bottom:24px;">
          <label class="cg-label">Password</label>
          <input type="password" name="password" class="cg-input" placeholder="Enter your password" required/>
        </div>
        <button type="submit" class="btn-cg-primary" style="width:100%;padding:12px;text-align:center;">
          Sign in &nbsp;<i class="bi bi-arrow-right"></i>
        </button>
      </form>
      <hr class="cg-divider"/>
      <div style="text-align:center;">
        <a href="/signup/" style="font-size:0.82rem;color:var(--accent);text-decoration:none;">
          <i class="bi bi-person-plus me-1"></i> Create a new account
        </a>
      </div>
      <p style="font-size:0.75rem;color:var(--text-muted);text-align:center;margin-top:12px;">
        Forgot your password? Contact the system administrator.
      </p>
    </div>
    <p style="text-align:center;font-size:0.68rem;color:var(--text-muted);margin-top:24px;letter-spacing:0.5px;">
      CampusGrid &middot; UEAB Extracurricular Facility Booking &middot; 2026
    </p>
  </div>
</div>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# SIGNUP
# ════════════════════════════════════════════════════════════════
signup_html = """\
{% extends 'base.html' %}
{% block auth_content %}
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-primary);width:100%;padding:32px 24px;">
  <div style="width:100%;max-width:500px;">
    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-family:'EB Garamond',serif;font-size:2.8rem;font-weight:600;color:var(--accent);letter-spacing:1px;">CampusGrid</div>
      <div style="width:60px;height:1px;background:var(--border);margin:12px auto;"></div>
      <div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:2.5px;">University of Eastern Africa Baraton</div>
    </div>
    <div class="cg-card">
      <h5 style="font-family:'EB Garamond',serif;font-size:1.3rem;font-weight:600;margin-bottom:4px;">Create Account</h5>
      <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">Register to access the facility booking system.</p>
      {% if messages %}
        {% for message in messages %}
          <div class="cg-alert cg-alert-info"><i class="bi bi-info-circle me-2"></i>{{ message }}</div>
        {% endfor %}
      {% endif %}
      <form method="POST" action="/signup/">
        {% csrf_token %}
        <div style="display:grid;gap:14px;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <label class="cg-label">First Name</label>
              <input type="text" name="first_name" class="cg-input" placeholder="First name" required/>
            </div>
            <div>
              <label class="cg-label">Last Name</label>
              <input type="text" name="last_name" class="cg-input" placeholder="Last name" required/>
            </div>
          </div>
          <div>
            <label class="cg-label">Student ID / Staff ID</label>
            <input type="text" name="institutional_id" class="cg-input" placeholder="e.g. SGATWI2311" required oninput="this.value=this.value.toUpperCase()"/>
            <div style="font-size:0.73rem;color:var(--text-muted);margin-top:4px;">This will be your login username. Use your official institutional ID.</div>
          </div>
          <div>
            <label class="cg-label">Email Address</label>
            <input type="email" name="email" class="cg-input" placeholder="your@email.com" required/>
          </div>
          <div>
            <label class="cg-label">Phone Number <span style="color:var(--text-muted);font-size:0.72rem;">(optional)</span></label>
            <input type="text" name="phone" class="cg-input" placeholder="e.g. 0712345678"/>
          </div>
          <div>
            <label class="cg-label">Account Type</label>
            <select name="role" class="cg-input" id="role-select" onchange="updateRoleNote()">
              <option value="requester">Student / Club Leader (Requester)</option>
              <option value="approver">Sports Director (Approver)</option>
              <option value="admin">Administrator</option>
            </select>
            <div id="role-note" class="cg-alert cg-alert-success" style="margin-top:8px;margin-bottom:0;">
              <i class="bi bi-check-circle me-1"></i> Your account will be active immediately after registration.
            </div>
          </div>
          <div>
            <label class="cg-label">Password</label>
            <input type="password" name="password" class="cg-input" placeholder="Minimum 8 characters" required minlength="8"/>
          </div>
          <div>
            <label class="cg-label">Confirm Password</label>
            <input type="password" name="password2" class="cg-input" placeholder="Re-enter your password" required/>
          </div>
        </div>
        <button type="submit" class="btn-cg-primary" style="width:100%;padding:12px;margin-top:20px;text-align:center;">
          Create Account &nbsp;<i class="bi bi-arrow-right"></i>
        </button>
      </form>
      <hr class="cg-divider"/>
      <p style="text-align:center;font-size:0.82rem;color:var(--text-muted);">
        Already have an account? <a href="/" style="color:var(--accent);text-decoration:none;">Sign in</a>
      </p>
    </div>
    <p style="text-align:center;font-size:0.68rem;color:var(--text-muted);margin-top:24px;letter-spacing:0.5px;">
      CampusGrid &middot; UEAB Extracurricular Facility Booking &middot; 2026
    </p>
  </div>
</div>
<script>
function updateRoleNote() {
  var role = document.getElementById('role-select').value;
  var note = document.getElementById('role-note');
  if (role === 'requester') {
    note.className = 'cg-alert cg-alert-success';
    note.innerHTML = '<i class="bi bi-check-circle me-1"></i> Your account will be active immediately after registration.';
  } else {
    note.className = 'cg-alert cg-alert-warning';
    note.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Your account will require administrator approval before you can sign in.';
  }
}
</script>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# PASSWORD CHANGE
# ════════════════════════════════════════════════════════════════
password_change_html = """\
{% extends 'base.html' %}
{% block title %}Change Password{% endblock %}
{% block page_title %}Change Password{% endblock %}

{% block content %}
<div style="max-width:480px;">
  <div class="cg-card">
    {% if forced %}
    <div class="cg-alert cg-alert-warning">
      <i class="bi bi-shield-lock me-2"></i>
      You are required to change your password before continuing.
    </div>
    {% endif %}
    <h5 style="font-family:'EB Garamond',serif;font-size:1.2rem;margin-bottom:4px;">Change Password</h5>
    <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">Choose a strong password you will remember.</p>

    {% if messages %}
      {% for message in messages %}
        <div class="cg-alert cg-alert-info"><i class="bi bi-info-circle me-2"></i>{{ message }}</div>
      {% endfor %}
    {% endif %}

    <form method="POST" action="/change-password/">
      {% csrf_token %}
      <div style="display:grid;gap:16px;">
        {% if not forced %}
        <div>
          <label class="cg-label">Current Password</label>
          <input type="password" name="current_password" class="cg-input" placeholder="Enter current password" required/>
        </div>
        {% endif %}
        <div>
          <label class="cg-label">New Password</label>
          <input type="password" name="new_password" class="cg-input" placeholder="Minimum 8 characters" required minlength="8"/>
        </div>
        <div>
          <label class="cg-label">Confirm New Password</label>
          <input type="password" name="new_password2" class="cg-input" placeholder="Re-enter new password" required/>
        </div>
      </div>
      <div style="display:flex;gap:12px;margin-top:20px;">
        <button type="submit" class="btn-cg-primary">
          <i class="bi bi-shield-check me-1"></i> Update Password
        </button>
        {% if not forced %}
        <a href="/calendar/" class="btn-cg-outline">Cancel</a>
        {% endif %}
      </div>
    </form>
  </div>
</div>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# USER MANAGEMENT (Admin only)
# ════════════════════════════════════════════════════════════════
users_html = """\
{% extends 'base.html' %}
{% block title %}User Management{% endblock %}
{% block page_title %}User Management{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div style="font-size:0.85rem;color:var(--text-muted);">Manage all registered users and their access levels.</div>
  <div style="display:flex;gap:8px;">
    <select id="role-filter" class="cg-input" style="width:auto;" onchange="loadUsers()">
      <option value="">All Roles</option>
      <option value="requester">Requesters</option>
      <option value="approver">Approvers</option>
      <option value="admin">Admins</option>
    </select>
    <select id="status-filter" class="cg-input" style="width:auto;" onchange="loadUsers()">
      <option value="">All Status</option>
      <option value="active">Active</option>
      <option value="inactive">Pending Activation</option>
    </select>
  </div>
</div>
<div class="cg-card">
  <div id="users-list">
    <div style="display:grid;gap:8px;">
      <div class="skeleton" style="height:48px;"></div>
      <div class="skeleton" style="height:48px;"></div>
      <div class="skeleton" style="height:48px;"></div>
    </div>
  </div>
</div>

<div id="user-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:8px;padding:28px;width:100%;max-width:420px;">
    <h5 style="font-family:'EB Garamond',serif;font-size:1.2rem;margin-bottom:16px;" id="user-modal-title">Edit User</h5>
    <input type="hidden" id="edit-user-id"/>
    <div style="display:grid;gap:14px;">
      <div>
        <label class="cg-label">Role</label>
        <select id="edit-role" class="cg-input">
          <option value="requester">Requester</option>
          <option value="approver">Approver</option>
          <option value="admin">Administrator</option>
        </select>
      </div>
      <div>
        <label class="cg-label">Account Status</label>
        <select id="edit-active" class="cg-input">
          <option value="true">Active</option>
          <option value="false">Inactive (Pending)</option>
        </select>
      </div>
    </div>
    <div style="display:flex;gap:12px;margin-top:20px;">
      <button class="btn-cg-primary" onclick="saveUser()">Save Changes</button>
      <button class="btn-cg-outline" onclick="closeUserModal()">Cancel</button>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadUsers() {
  const roleFilter   = document.getElementById('role-filter').value;
  const statusFilter = document.getElementById('status-filter').value;
  const res = await API.get('/auth/users/');
  const container = document.getElementById('users-list');
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load users.</div>';
    return;
  }
  let data = await res.json();
  if (roleFilter)   data = data.filter(function(u){ return u.role === roleFilter; });
  if (statusFilter === 'active')   data = data.filter(function(u){ return u.is_active; });
  if (statusFilter === 'inactive') data = data.filter(function(u){ return !u.is_active; });

  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:32px;color:var(--text-muted);">No users found.</div>';
    return;
  }

  let html = '<table class="cg-table"><thead><tr>';
  html += '<th>Name</th><th>Institutional ID</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th>';
  html += '</tr></thead><tbody>';
  data.forEach(function(u) {
    const joined  = new Date(u.date_joined).toLocaleDateString('en-KE', {month:'short', day:'numeric', year:'numeric'});
    const active  = u.is_active;
    html += '<tr>';
    html += '<td style="font-weight:500;">' + (u.first_name && u.last_name ? u.first_name + ' ' + u.last_name : u.username) + '</td>';
    html += '<td style="font-family:monospace;font-size:0.82rem;color:var(--text-muted);">' + u.username + '</td>';
    html += '<td style="font-size:0.82rem;color:var(--text-muted);">' + (u.email || '\u2014') + '</td>';
    html += '<td><span class="status-badge badge-' + (u.role === 'admin' ? 'rejected' : u.role === 'approver' ? 'pending' : 'approved') + '">' + u.role + '</span></td>';
    html += '<td>';
    if (active) {
      html += '<span class="status-badge badge-approved">Active</span>';
    } else {
      html += '<span class="status-badge badge-pending">Pending</span>';
    }
    html += '</td>';
    html += '<td style="font-size:0.78rem;color:var(--text-muted);">' + joined + '</td>';
    html += '<td><button onclick="openUserModal(' + u.id + ',\'' + u.role + '\',' + active + ')" style="background:rgba(201,168,76,0.1);border:1px solid rgba(201,168,76,0.2);color:var(--accent);border-radius:4px;padding:3px 10px;font-size:0.75rem;cursor:pointer;">Edit</button></td>';
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

function openUserModal(userId, role, isActive) {
  document.getElementById('edit-user-id').value = userId;
  document.getElementById('edit-role').value    = role;
  document.getElementById('edit-active').value  = isActive ? 'true' : 'false';
  document.getElementById('user-modal').style.display = 'flex';
}

function closeUserModal() {
  document.getElementById('user-modal').style.display = 'none';
}

async function saveUser() {
  const userId   = document.getElementById('edit-user-id').value;
  const role     = document.getElementById('edit-role').value;
  const isActive = document.getElementById('edit-active').value === 'true';
  const res = await API.patch('/auth/users/' + userId + '/role/', { role: role });
  if (res && res.ok) {
    // Also update active status via admin endpoint
    closeUserModal();
    loadUsers();
  }
}

loadUsers();
</script>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# 404 PAGE
# ════════════════════════════════════════════════════════════════
not_found_html = """\
{% extends 'base.html' %}
{% block auth_content %}
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-primary);width:100%;">
  <div style="text-align:center;padding:40px;">
    <div style="font-family:'EB Garamond',serif;font-size:8rem;font-weight:600;color:var(--border);line-height:1;">404</div>
    <div style="font-family:'EB Garamond',serif;font-size:1.8rem;color:var(--accent);margin-bottom:12px;">Page Not Found</div>
    <p style="color:var(--text-muted);font-size:0.9rem;max-width:360px;margin:0 auto 28px;">
      The page you are looking for does not exist or has been moved.
    </p>
    <a href="/calendar/" class="btn-cg-primary">
      <i class="bi bi-house me-1"></i> Return to Calendar
    </a>
  </div>
</div>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# BOOKING CONFIRMATION PAGE
# ════════════════════════════════════════════════════════════════
booking_confirm_html = """\
{% extends 'base.html' %}
{% block title %}Booking Confirmed{% endblock %}
{% block page_title %}Booking Submitted{% endblock %}

{% block content %}
<div style="max-width:560px;margin:40px auto;">
  <div class="cg-card" style="text-align:center;padding:40px;">
    <div style="width:64px;height:64px;border-radius:50%;background:rgba(74,124,89,0.15);border:2px solid rgba(74,124,89,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
      <i class="bi bi-check-lg" style="font-size:1.8rem;color:#86B89A;"></i>
    </div>
    <h4 style="font-family:'EB Garamond',serif;font-size:1.5rem;margin-bottom:8px;">Booking Submitted</h4>
    <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:28px;">
      Your booking request has been submitted and is pending approval from the Sports Director.
    </p>

    <div id="booking-details" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:6px;padding:20px;text-align:left;margin-bottom:24px;">
      <div style="display:grid;gap:12px;font-size:0.85rem;">
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Reference No.</span>
          <span id="ref-no" style="font-family:monospace;color:var(--accent);font-weight:600;"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Facility</span>
          <span id="conf-facility" style="font-weight:500;"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Zone</span>
          <span id="conf-zone"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Date</span>
          <span id="conf-date" style="font-weight:500;"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Time</span>
          <span id="conf-time"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Purpose</span>
          <span id="conf-purpose"></span>
        </div>
        <div style="display:flex;justify-content:space-between;">
          <span style="color:var(--text-muted);">Status</span>
          <span class="status-badge badge-pending">Pending Approval</span>
        </div>
      </div>
    </div>

    <p style="font-size:0.78rem;color:var(--text-muted);margin-bottom:24px;">
      <i class="bi bi-info-circle me-1"></i>
      Screenshot or print this page for your records. You will be notified when your booking is reviewed.
    </p>

    <div style="display:flex;gap:12px;justify-content:center;">
      <button onclick="window.print()" class="btn-cg-outline">
        <i class="bi bi-printer me-1"></i> Print Receipt
      </button>
      <a href="/bookings/" class="btn-cg-primary">View My Bookings</a>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
const bookingId = new URLSearchParams(window.location.search).get('id');
if (bookingId) {
  document.getElementById('ref-no').textContent = 'CG-' + String(bookingId).padStart(5, '0');
  API.get('/bookings/' + bookingId + '/').then(function(res) {
    if (res && res.ok) {
      res.json().then(function(b) {
        const start = new Date(b.start_time);
        const end   = new Date(b.end_time);
        document.getElementById('conf-facility').textContent = b.facility_detail.name;
        document.getElementById('conf-zone').textContent     = b.zone_name || 'Entire facility';
        document.getElementById('conf-date').textContent     = start.toLocaleDateString('en-KE', {weekday:'long', month:'long', day:'numeric', year:'numeric'});
        document.getElementById('conf-time').textContent     = start.toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'}) + ' \u2014 ' + end.toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
        document.getElementById('conf-purpose').textContent  = b.purpose;
      });
    }
  });
} else {
  window.location.href = '/bookings/';
}
</script>
{% endblock %}
"""

# ════════════════════════════════════════════════════════════════
# WRITE ALL FILES
# ════════════════════════════════════════════════════════════════
write('templates/base.html',                    base)
write('templates/auth/login.html',              login_html)
write('templates/auth/signup.html',             signup_html)
write('templates/auth/change_password.html',    password_change_html)
write('templates/users/list.html',              users_html)
write('templates/404.html',                     not_found_html)
write('templates/bookings/confirmation.html',   booking_confirm_html)

print('\nAll templates written successfully.')
print('Next: update ui/views.py and ui/urls.py for new pages.')
