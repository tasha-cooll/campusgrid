
var API = {
  baseURL: '/api',
  getToken: function() { return localStorage.getItem('cg_access_token'); },
  clearTokens: function() {
    localStorage.removeItem('cg_access_token');
    localStorage.removeItem('cg_refresh_token');
  },
  request: async function(method, endpoint, data) {
    var headers = { 'Content-Type': 'application/json' };
    var token = this.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    var config = { method: method, headers: headers };
    if (data) config.body = JSON.stringify(data);
    var res = await fetch(this.baseURL + endpoint, config);
    if (res.status === 401) {
      var refreshed = await this.refreshToken();
      if (refreshed) return this.request(method, endpoint, data);
      this.clearTokens();
      if (!window._redirecting) {
        window._redirecting = true;
        window.location.href = '/';
      }
      return null;
    }
    return res;
  },
  refreshToken: async function() {
    var refresh = localStorage.getItem('cg_refresh_token');
    if (!refresh) return false;
    var res = await fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refresh })
    });
    if (res.ok) {
      var data = await res.json();
      localStorage.setItem('cg_access_token', data.access);
      return true;
    }
    return false;
  },
  get:    function(ep)      { return this.request('GET',    ep, null); },
  post:   function(ep, d)   { return this.request('POST',   ep, d); },
  patch:  function(ep, d)   { return this.request('PATCH',  ep, d); },
  delete: function(ep)      { return this.request('DELETE', ep, null); }
};

function showToast(message, type) {
  var existing = document.getElementById('cg-toast');
  if (existing) existing.remove();
  var color = type === 'error' ? '#7B2828' : '#C9A84C';
  var icon  = type === 'error' ? 'bi-exclamation-circle-fill' : 'bi-check-circle-fill';
  var toast = document.createElement('div');
  toast.id  = 'cg-toast';
  toast.style.cssText = 'position:fixed;bottom:28px;right:28px;background:#0F1A30;border:1px solid ' + color + ';border-left:4px solid ' + color + ';color:#F0F4FF;padding:14px 20px;border-radius:6px;font-size:0.875rem;font-family:Inter,sans-serif;z-index:9999;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.4);display:flex;align-items:center;gap:12px;opacity:0;transform:translateY(12px);transition:all 0.3s ease';
  toast.innerHTML = '<i class="bi ' + icon + '" style="color:' + color + ';font-size:1.1rem;flex-shrink:0;"></i><span>' + message + '</span>';
  document.body.appendChild(toast);
  setTimeout(function() { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 10);
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
  }, 3500);
}

async function loadNotifCount() {
  try {
    var res = await API.get('/notifications/unread-count/');
    if (res && res.ok) {
      var data = await res.json();
      var badge = document.getElementById('notif-badge');
      if (badge) {
        badge.textContent   = data.unread_count > 0 ? data.unread_count : '';
        badge.style.display = data.unread_count > 0 ? 'flex' : 'none';
      }
      var pb = document.getElementById('pending-count-badge');
      if (pb) {
        var ar = await API.get('/approvals/pending/');
        if (ar && ar.ok) {
          var ad = await ar.json();
          pb.textContent   = ad.count > 0 ? ad.count : '';
          pb.style.display = ad.count > 0 ? 'inline' : 'none';
        }
      }
    }
  } catch(e) {}
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('.sidebar')) {
    loadNotifCount();
    setInterval(loadNotifCount, 60000);
  }
});
