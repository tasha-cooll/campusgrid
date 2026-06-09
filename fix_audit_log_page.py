import os

content = """\
{% extends 'base.html' %}
{% block title %}Audit Log{% endblock %}
{% block page_title %}System Audit Log{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div style="font-size:0.84rem;color:var(--text-muted);">
    Complete record of all system actions. Read-only. Tamper-proof.
  </div>
  <div style="display:flex;gap:8px;">
    <select id="action-filter" class="cg-input" style="width:auto;padding:6px 12px;" onchange="loadLogs()">
      <option value="">All Actions</option>
      <option value="booking_created">Bookings Created</option>
      <option value="booking_approved">Bookings Approved</option>
      <option value="booking_rejected">Bookings Rejected</option>
      <option value="booking_cancelled">Bookings Cancelled</option>
      <option value="booking_displaced">Bookings Displaced</option>
      <option value="user_registered">User Registered</option>
      <option value="user_role_changed">Role Changes</option>
      <option value="user_activated">User Activated</option>
      <option value="user_deactivated">User Deactivated</option>
      <option value="facility_created">Facility Created</option>
      <option value="admin_action">Admin Panel Actions</option>
    </select>
    <select id="days-filter" class="cg-input" style="width:auto;padding:6px 12px;" onchange="loadLogs()">
      <option value="">All Time</option>
      <option value="1">Last 24 Hours</option>
      <option value="7" selected>Last 7 Days</option>
      <option value="30">Last 30 Days</option>
      <option value="90">Last 90 Days</option>
    </select>
    <button onclick="exportAuditCSV()" class="btn-cg-outline" style="font-size:0.82rem;">
      <i class="bi bi-download me-1"></i> Export CSV
    </button>
  </div>
</div>

<div class="cg-card">
  <div id="audit-log-content">
    <div style="display:grid;gap:8px;">
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
var auditData = [];

var ACTION_META = {
  booking_created:   { icon: 'bi-plus-circle',        color: '#7BA7DC', label: 'Booking Created'    },
  booking_approved:  { icon: 'bi-check-circle',        color: '#6BAB8A', label: 'Booking Approved'   },
  booking_rejected:  { icon: 'bi-x-circle',            color: '#C4827A', label: 'Booking Rejected'   },
  booking_cancelled: { icon: 'bi-slash-circle',        color: '#8A9BBF', label: 'Booking Cancelled'  },
  booking_displaced: { icon: 'bi-exclamation-triangle',color: '#C49A6C', label: 'Booking Displaced'  },
  conflict_detected: { icon: 'bi-shield-exclamation',  color: '#C9A84C', label: 'Conflict Detected'  },
  priority_created:  { icon: 'bi-star-fill',           color: '#C4827A', label: 'Priority Created'   },
  user_registered:   { icon: 'bi-person-plus',         color: '#6BAB8A', label: 'User Registered'    },
  user_role_changed: { icon: 'bi-person-gear',         color: '#C9A84C', label: 'Role Changed'       },
  user_activated:    { icon: 'bi-person-check',        color: '#6BAB8A', label: 'User Activated'     },
  user_deactivated:  { icon: 'bi-person-dash',         color: '#C4827A', label: 'User Deactivated'   },
  facility_created:  { icon: 'bi-building-add',        color: '#7BA7DC', label: 'Facility Created'   },
  facility_updated:  { icon: 'bi-building-gear',       color: '#C9A84C', label: 'Facility Updated'   },
  facility_deleted:  { icon: 'bi-building-dash',       color: '#C4827A', label: 'Facility Deleted'   },
  admin_action:      { icon: 'bi-shield-lock',         color: '#C9A84C', label: 'Admin Action'       },
};

async function loadLogs() {
  var action    = document.getElementById('action-filter').value;
  var days      = document.getElementById('days-filter').value;
  var container = document.getElementById('audit-log-content');

  container.innerHTML = '<div style="display:grid;gap:8px;"><div class="skeleton" style="height:44px;"></div><div class="skeleton" style="height:44px;"></div><div class="skeleton" style="height:44px;"></div></div>';

  var url = '/reports/audit-log/';
  var params = [];
  if (action) params.push('action=' + action);
  if (days)   params.push('days='   + days);
  if (params.length) url += '?' + params.join('&');

  var res = await API.get(url);
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load audit log. Admin access required.</div>';
    return;
  }

  auditData = await res.json();

  if (!auditData.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-journal-x" style="font-size:2.5rem;"></i><p style="margin-top:12px;">No log entries found for the selected filters.</p></div>';
    return;
  }

  var html = '<table class="cg-table"><thead><tr>';
  html += '<th style="width:36px;"></th>';
  html += '<th>Action</th>';
  html += '<th>Actor</th>';
  html += '<th>Details</th>';
  html += '<th>Target</th>';
  html += '<th>IP Address</th>';
  html += '<th>Timestamp</th>';
  html += '</tr></thead><tbody>';

  auditData.forEach(function(log) {
    var meta  = ACTION_META[log.action] || { icon: 'bi-activity', color: '#8A9BBF', label: log.action };
    var ts    = new Date(log.timestamp).toLocaleString('en-KE', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    var actor = log.actor_name || 'System';
    var target = log.target_user_name ? '<span style="font-family:monospace;font-size:0.78rem;color:var(--text-muted);">' + log.target_user_name + '</span>' : '<span style="color:var(--border);">—</span>';
    var ip     = log.ip_address ? '<span style="font-family:monospace;font-size:0.78rem;color:var(--text-muted);">' + log.ip_address + '</span>' : '<span style="color:var(--border);">—</span>';

    html += '<tr>';
    html += '<td><div style="width:28px;height:28px;border-radius:6px;background:' + meta.color + '18;display:flex;align-items:center;justify-content:center;"><i class="bi ' + meta.icon + '" style="color:' + meta.color + ';font-size:0.85rem;"></i></div></td>';
    html += '<td><span style="font-size:0.75rem;font-weight:600;color:' + meta.color + ';text-transform:uppercase;letter-spacing:0.8px;">' + meta.label + '</span></td>';
    html += '<td style="font-weight:500;font-family:monospace;font-size:0.82rem;">' + actor + '</td>';
    html += '<td style="font-size:0.82rem;color:var(--text-muted);max-width:280px;">' + (log.details || '—') + '</td>';
    html += '<td>' + target + '</td>';
    html += '<td>' + ip + '</td>';
    html += '<td style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;">' + ts + '</td>';
    html += '</tr>';
  });

  html += '</tbody></table>';
  html += '<div style="margin-top:12px;font-size:0.75rem;color:var(--text-muted);text-align:right;">' + auditData.length + ' entries shown &mdash; maximum 200 per query. Use filters to narrow results.</div>';
  container.innerHTML = html;
}

function exportAuditCSV() {
  if (!auditData.length) return;
  var rows = ['Timestamp,Action,Actor,Details,Target,IP Address'];
  auditData.forEach(function(log) {
    var ts  = new Date(log.timestamp).toLocaleString('en-KE');
    rows.push([
      '"' + ts + '"',
      log.action,
      log.actor_name || 'System',
      '"' + (log.details || '').replace(/"/g, "'") + '"',
      log.target_user_name || '',
      log.ip_address || ''
    ].join(','));
  });
  var blob = new Blob([rows.join('\\n')], { type: 'text/csv;charset=utf-8;' });
  var url  = URL.createObjectURL(blob);
  var a    = document.createElement('a');
  a.href = url;
  a.download = 'CampusGrid_AuditLog_' + new Date().toISOString().slice(0,10) + '.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

loadLogs();
</script>
{% endblock %}
"""

with open('templates/audit/log.html', 'w', encoding='utf-8', newline='\n') as f:
    os.makedirs('templates/audit', exist_ok=True)
    f.write(content)
print('Audit log template written')
