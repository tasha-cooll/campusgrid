import os

content = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{% block title %}CampusGrid{% endblock %} — UEAB</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet"/>
  <link rel="icon" type="image/svg+xml" href="/static/favicon.svg"/>
  <style>
    :root {
      --bg-primary:    #0B1120;
      --bg-secondary:  #111D35;
      --bg-sidebar:    #0D1628;
      --accent:        #C9A84C;
      --accent-blue:   #1E4B8F;
      --accent-green:  #2A6B4A;
      --accent-red:    #7B2828;
      --accent-orange: #8B4513;
      --accent-amber:  #B8860B;
      --text-primary:  #F0F4FF;
      --text-muted:    #8A9BBF;
      --border:        #1E2D4A;
      --card-bg:       #0F1A30;
    }
    * { box-sizing: border-box; }
    body {
      background: var(--bg-primary);
      color: var(--text-primary);
      font-family: 'Inter', 'Segoe UI', sans-serif;
      min-height: 100vh;
      display: flex;
      margin: 0;
      font-size: 14px;
    }
    h1,h2,h3,h4,h5,h6 {
      font-family: 'Playfair Display', Georgia, serif;
      letter-spacing: 0.2px;
    }

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
      padding: 22px 20px 16px;
      border-bottom: 1px solid var(--border);
    }
    .sidebar-brand .brand-name {
      font-family: 'Playfair Display', serif;
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--accent);
      letter-spacing: 0.5px;
    }
    .sidebar-brand .brand-sub {
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-top: 2px;
    }
    .sidebar-nav { flex: 1; padding: 12px 0; }
    .nav-item-link {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 20px;
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.855rem;
      font-weight: 400;
      border-left: 3px solid transparent;
      transition: all 0.15s;
      letter-spacing: 0.1px;
    }
    .nav-item-link:hover {
      color: var(--text-primary);
      background: rgba(201,168,76,0.06);
    }
    .nav-item-link.active {
      color: var(--accent);
      border-left-color: var(--accent);
      background: rgba(201,168,76,0.08);
      font-weight: 500;
    }
    .nav-item-link i { font-size: 0.95rem; width: 18px; }
    .sidebar-user {
      padding: 14px 20px;
      border-top: 1px solid var(--border);
    }
    .user-role-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 0.6rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1.2px;
    }
    .role-admin     { background: rgba(201,168,76,0.15); color: #C9A84C; border: 1px solid rgba(201,168,76,0.3); }
    .role-approver  { background: rgba(30,75,143,0.2);  color: #7BA7DC; border: 1px solid rgba(30,75,143,0.4); }
    .role-requester { background: rgba(42,107,74,0.2);  color: #6BAB8A; border: 1px solid rgba(42,107,74,0.4); }

    /* ── MAIN CONTENT ── */
    .main-content {
      margin-left: 240px;
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .topbar {
      height: 58px;
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
      font-family: 'Playfair Display', serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-primary);
      letter-spacing: 0.3px;
    }
    .notification-bell {
      position: relative;
      color: var(--text-muted);
      font-size: 1.05rem;
      cursor: pointer;
      text-decoration: none;
      transition: color 0.15s;
    }
    .notification-bell:hover { color: var(--accent); }
    .notif-badge {
      position: absolute;
      top: -4px; right: -6px;
      background: #7B2828;
      color: #F0F4FF;
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
      border-radius: 6px;
      padding: 20px;
    }
    .cg-card-title {
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--text-muted);
      margin-bottom: 10px;
    }

    /* ── STAT CARDS ── */
    .stat-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .stat-icon {
      width: 44px; height: 44px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.15rem;
    }
    .stat-value {
      font-family: 'Playfair Display', serif;
      font-size: 1.9rem;
      font-weight: 700;
      line-height: 1;
      color: var(--accent);
    }
    .stat-label { font-size: 0.76rem; color: var(--text-muted); margin-top: 3px; }

    /* ── BUTTONS ── */
    .btn-cg-primary {
      background: var(--accent);
      color: #0B1120;
      border: none;
      border-radius: 4px;
      padding: 8px 18px;
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      text-decoration: none;
      display: inline-block;
      font-family: 'Inter', sans-serif;
      letter-spacing: 0.2px;
    }
    .btn-cg-primary:hover { background: #D4B55A; color: #0B1120; }
    .btn-cg-outline {
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--accent);
      border-radius: 4px;
      padding: 8px 18px;
      font-size: 0.84rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
      text-decoration: none;
      display: inline-block;
    }
    .btn-cg-outline:hover { background: var(--accent); color: #0B1120; }

    /* ── FORMS ── */
    .cg-input {
      background: rgba(11,17,32,0.8);
      border: 1px solid var(--border);
      border-radius: 4px;
      color: var(--text-primary);
      padding: 9px 13px;
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
    .cg-input option { background: var(--bg-secondary); color: var(--text-primary); }
    .cg-label {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 5px;
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }

    /* ── STATUS BADGES ── */
    .badge-pending   { background: rgba(184,134,11,0.12);  color: #C9A84C; border: 1px solid rgba(184,134,11,0.25); }
    .badge-approved  { background: rgba(42,107,74,0.12);   color: #6BAB8A; border: 1px solid rgba(42,107,74,0.25); }
    .badge-rejected  { background: rgba(123,40,40,0.15);   color: #C4827A; border: 1px solid rgba(123,40,40,0.3); }
    .badge-cancelled { background: rgba(138,155,191,0.1);  color: #8A9BBF; border: 1px solid rgba(138,155,191,0.2); }
    .badge-displaced { background: rgba(139,69,19,0.12);   color: #C49A6C; border: 1px solid rgba(139,69,19,0.25); }
    .badge-priority  { background: rgba(201,168,76,0.15);  color: #C9A84C; border: 1px solid rgba(201,168,76,0.35); }
    .status-badge {
      padding: 2px 9px;
      border-radius: 3px;
      font-size: 0.65rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    /* ── ALERTS ── */
    .cg-alert {
      border-radius: 4px;
      padding: 11px 15px;
      font-size: 0.845rem;
      margin-bottom: 14px;
      border-left: 3px solid;
    }
    .cg-alert-error   { background: rgba(123,40,40,0.1);   border-color: #7B2828;  color: #C4827A; }
    .cg-alert-success { background: rgba(42,107,74,0.1);   border-color: #2A6B4A;  color: #6BAB8A; }
    .cg-alert-info    { background: rgba(201,168,76,0.08); border-color: #C9A84C;  color: #C9A84C; }
    .cg-alert-warning { background: rgba(184,134,11,0.1);  border-color: #B8860B;  color: #C9A84C; }

    /* ── SKELETON ── */
    .skeleton {
      background: linear-gradient(90deg, var(--border) 25%, var(--bg-secondary) 50%, var(--border) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.5s infinite;
      border-radius: 4px;
    }
    @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

    /* ── TABLE ── */
    .cg-table { width:100%; border-collapse:collapse; font-size:0.845rem; }
    .cg-table th {
      padding: 9px 12px;
      text-align: left;
      color: var(--text-muted);
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      border-bottom: 1px solid var(--border);
      font-weight: 600;
    }
    .cg-table td { padding: 11px 12px; border-bottom: 1px solid var(--border); }
    .cg-table tr:hover td { background: rgba(201,168,76,0.03); }

    /* ── DIVIDER ── */
    .cg-divider { border:none; border-top:1px solid var(--border); margin:18px 0; }

    /* ── GOLD ACCENT LINE ── */
    .gold-line {
      width: 40px;
      height: 2px;
      background: var(--accent);
      margin: 8px 0 16px 0;
      border-radius: 1px;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

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
      <span id="pending-count-badge" class="ms-auto" style="background:rgba(201,168,76,0.15);color:var(--accent);padding:1px 7px;border-radius:3px;font-size:0.62rem;font-weight:600;display:none;"></span>
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
    <div style="font-size:0.84rem;font-weight:600;margin-bottom:2px;color:var(--text-primary);">{{ user.get_full_name|default:user.username }}</div>
    <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:8px;font-family:'Inter',monospace;letter-spacing:0.3px;">{{ user.institutional_id }}</div>
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
      <span style="font-size:0.76rem;color:var(--text-muted);font-family:'Inter',monospace;letter-spacing:0.3px;">{{ user.institutional_id }}</span>
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
        badge.textContent   = data.unread_count;
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
            pb.textContent   = ad.count;
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
setInterval(loadNotifCount, 60000);
{% endif %}
</script>
{% block extra_scripts %}{% endblock %}
</body>
</html>
"""

with open('templates/base.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Theme updated successfully — UEAB Navy and Gold')
