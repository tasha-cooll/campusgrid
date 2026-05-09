content = """\
{% extends 'base.html' %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}Dashboard{% endblock %}

{% block content %}
<div id="dashboard-content">
  <div style="text-align:center;padding:40px;color:var(--text-muted);">
    <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
    <p style="margin-top:8px;">Loading dashboard...</p>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
const USER_ROLE = '{{ user.role }}';

async function loadDashboard() {
  const container = document.getElementById('dashboard-content');

  if (USER_ROLE === 'admin' || USER_ROLE === 'approver') {
    const res = await API.get('/reports/dashboard/');
    if (!res || !res.ok) {
      container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load dashboard data.</div>';
      return;
    }
    const d = await res.json();
    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px;">';
    html += '<div class="stat-card"><div class="stat-icon" style="background:rgba(46,117,182,0.15);"><i class="bi bi-journal-bookmark" style="color:#2E75B6;"></i></div><div><div class="stat-value">' + d.total_bookings_this_month + '</div><div class="stat-label">Bookings This Month</div></div></div>';
    html += '<div class="stat-card"><div class="stat-icon" style="background:rgba(244,162,97,0.15);"><i class="bi bi-hourglass-split" style="color:#F4A261;"></i></div><div><div class="stat-value">' + d.pending_approvals + '</div><div class="stat-label">Pending Approvals</div></div></div>';
    html += '<div class="stat-card"><div class="stat-icon" style="background:rgba(34,197,94,0.15);"><i class="bi bi-check-circle" style="color:#22C55E;"></i></div><div><div class="stat-value">' + d.approved_this_month + '</div><div class="stat-label">Approved This Month</div></div></div>';
    html += '<div class="stat-card"><div class="stat-icon" style="background:rgba(239,68,68,0.15);"><i class="bi bi-shield-exclamation" style="color:#EF4444;"></i></div><div><div class="stat-value">' + d.conflicts_this_month + '</div><div class="stat-label">Conflicts This Month</div></div></div>';
    html += '<div class="stat-card"><div class="stat-icon" style="background:rgba(46,117,182,0.15);"><i class="bi bi-building" style="color:#2E75B6;"></i></div><div><div class="stat-value">' + d.total_facilities + '</div><div class="stat-label">Active Facilities</div></div></div>';
    html += '</div>';
    if (d.recent_audit_logs && d.recent_audit_logs.length) {
      html += '<div class="cg-card"><div class="cg-card-title">Recent Activity</div><div style="display:grid;gap:10px;margin-top:12px;">';
      d.recent_audit_logs.forEach(function(log) {
        const ts = new Date(log.timestamp).toLocaleString('en-KE', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
        html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:10px;background:var(--bg-primary);border-radius:8px;font-size:0.82rem;">';
        html += '<div><span style="font-weight:500;">' + log.actor_name + '</span><span style="color:var(--text-muted);margin-left:8px;">' + log.action_display + '</span>';
        if (log.booking_info) html += '<span style="color:var(--text-muted);"> &middot; ' + log.booking_info.facility + '</span>';
        html += '</div><div style="color:var(--text-muted);font-size:0.75rem;">' + ts + '</div></div>';
      });
      html += '</div></div>';
    }
    container.innerHTML = html;
  } else {
    const res = await API.get('/bookings/');
    let html = '<div style="margin-bottom:20px;"><h6 style="color:var(--text-muted);font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">My Recent Bookings</h6>';
    if (res && res.ok) {
      const data = await res.json();
      if (!data.length) {
        html += '<div class="cg-card" style="text-align:center;padding:32px;color:var(--text-muted);">';
        html += '<i class="bi bi-calendar-plus" style="font-size:2rem;"></i>';
        html += '<p style="margin-top:8px;">No bookings yet.</p>';
        html += '<a href="/bookings/new/" class="btn-cg-primary" style="margin-top:12px;">Make your first booking</a></div>';
      } else {
        html += '<div style="display:grid;gap:10px;">';
        data.slice(0,5).forEach(function(b) {
          const startDate = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
          const startTime = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
          html += '<div class="cg-card" style="display:flex;justify-content:space-between;align-items:center;">';
          html += '<div><div style="font-weight:500;font-size:0.9rem;">' + b.purpose + '</div>';
          html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;">' + b.facility_detail.name + ' &middot; ' + startDate + ' ' + startTime + '</div></div>';
          html += '<span class="status-badge badge-' + b.status + '">' + b.status_display + '</span></div>';
        });
        html += '</div>';
        if (data.length > 5) {
          html += '<a href="/bookings/" style="display:block;text-align:center;margin-top:12px;font-size:0.82rem;color:var(--accent);">View all bookings</a>';
        }
      }
    }
    html += '</div>';
    container.innerHTML = html;
  }
}

loadDashboard();
</script>
{% endblock %}
"""

with open('templates/dashboard/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Dashboard template written successfully')
