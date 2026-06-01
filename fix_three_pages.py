import os


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('Written: ' + path)


# ── APPROVALS ──────────────────────────────────────────────────
approvals = """{% extends 'base.html' %}
{% block title %}Approval Queue{% endblock %}
{% block page_title %}Pending Approvals{% endblock %}

{% block content %}
<div class="cg-card">
  <div id="approvals-list">
    <div style="display:grid;gap:8px;">
      <div class="skeleton" style="height:120px;border-radius:6px;"></div>
      <div class="skeleton" style="height:120px;border-radius:6px;"></div>
    </div>
  </div>
</div>

<div id="approval-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:28px;width:100%;max-width:440px;">
    <h5 style="font-family:'Playfair Display',serif;font-size:1.15rem;margin-bottom:16px;" id="modal-title">Review Booking</h5>
    <input type="hidden" id="modal-booking-id"/>
    <input type="hidden" id="modal-action"/>
    <div style="margin-bottom:16px;">
      <label class="cg-label">Comments (optional)</label>
      <textarea class="cg-input" id="modal-comments" rows="3" placeholder="Add a note for the requester..."></textarea>
    </div>
    <div style="display:flex;gap:12px;">
      <button id="modal-confirm-btn" class="btn-cg-primary" onclick="confirmAction()">Confirm</button>
      <button onclick="closeApprovalModal()" class="btn-cg-outline">Cancel</button>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
function openApprovalModal(bookingId, action) {
  document.getElementById('modal-booking-id').value = bookingId;
  document.getElementById('modal-action').value = action;
  document.getElementById('modal-title').textContent = action === 'approve' ? 'Approve Booking' : 'Reject Booking';
  document.getElementById('modal-confirm-btn').style.background = action === 'approve' ? '#2A6B4A' : '#7B2828';
  document.getElementById('modal-comments').value = '';
  document.getElementById('approval-modal').style.display = 'flex';
}

function closeApprovalModal() {
  document.getElementById('approval-modal').style.display = 'none';
}

async function confirmAction() {
  var bookingId = document.getElementById('modal-booking-id').value;
  var action    = document.getElementById('modal-action').value;
  var comments  = document.getElementById('modal-comments').value;
  var res = await API.post('/approvals/' + bookingId + '/' + action + '/', { comments: comments });
  if (res && res.ok) {
    closeApprovalModal();
    loadApprovals();
  }
}

async function loadApprovals() {
  var res = await API.get('/approvals/pending/');
  var container = document.getElementById('approvals-list');
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load approvals.</div>';
    return;
  }
  var data     = await res.json();
  var bookings = data.bookings || [];
  var count    = data.count || bookings.length;

  if (!bookings.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-check-all" style="font-size:2.5rem;color:#6BAB8A;"></i><p style="margin-top:12px;">No pending bookings.</p></div>';
    return;
  }

  var html = '<div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border);">';
  html += count + ' booking' + (count !== 1 ? 's' : '') + ' awaiting review</div>';
  html += '<div style="display:grid;gap:12px;">';

  for (var i = 0; i < bookings.length; i++) {
    var b        = bookings[i];
    var bid      = b.id;
    var startD   = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
    var startT   = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    var endT     = new Date(b.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    var sub      = new Date(b.created_at).toLocaleDateString('en-KE', {month:'short', day:'numeric'});
    var uname    = b.user_detail ? b.user_detail.username : String(b.user);
    var facname  = b.facility_detail ? b.facility_detail.name : 'Unknown';
    var zone     = b.zone_name || 'Entire facility';
    var att      = b.expected_attendance;
    var purpose  = b.purpose;

    html += '<div style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:6px;padding:16px;">';
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">';
    html += '<div><div style="font-weight:600;font-size:0.9rem;">' + purpose + '</div>';
    html += '<div style="font-size:0.76rem;color:var(--text-muted);margin-top:2px;">by ' + uname + '</div></div>';
    html += '<span class="status-badge badge-pending">Pending</span></div>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;margin-bottom:14px;">';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Facility</div>';
    html += '<div style="font-weight:500;">' + facname + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + zone + '</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Date and Time</div>';
    html += '<div style="font-weight:500;">' + startD + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + startT + ' to ' + endT + '</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Attendance</div>';
    html += '<div style="font-weight:500;">' + att + ' people</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Submitted</div>';
    html += '<div style="font-weight:500;">' + sub + '</div></div></div>';
    html += '<div style="display:flex;gap:8px;">';
    html += '<button onclick="openApprovalModal(' + bid + ', \\'approve\\')" style="flex:1;background:rgba(42,107,74,0.12);border:1px solid rgba(42,107,74,0.3);color:#6BAB8A;border-radius:4px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;">Approve</button>';
    html += '<button onclick="openApprovalModal(' + bid + ', \\'reject\\')" style="flex:1;background:rgba(123,40,40,0.12);border:1px solid rgba(123,40,40,0.3);color:#C4827A;border-radius:4px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;">Reject</button>';
    html += '</div></div>';
  }

  html += '</div>';
  container.innerHTML = html;
}

loadApprovals();
</script>
{% endblock %}
"""

# ── USER MANAGEMENT ────────────────────────────────────────────
users = """{% extends 'base.html' %}
{% block title %}User Management{% endblock %}
{% block page_title %}User Management{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div style="font-size:0.84rem;color:var(--text-muted);">Manage registered users, roles and account access.</div>
  <div style="display:flex;gap:8px;">
    <select id="role-filter" class="cg-input" style="width:auto;padding:6px 12px;" onchange="loadUsers()">
      <option value="">All Roles</option>
      <option value="requester">Requesters</option>
      <option value="approver">Approvers</option>
      <option value="admin">Admins</option>
    </select>
    <select id="status-filter" class="cg-input" style="width:auto;padding:6px 12px;" onchange="loadUsers()">
      <option value="">All Status</option>
      <option value="active">Active</option>
      <option value="inactive">Pending</option>
    </select>
  </div>
</div>

<div class="cg-card">
  <div id="users-list">
    <div style="display:grid;gap:8px;">
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
    </div>
  </div>
</div>

<div id="user-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:28px;width:100%;max-width:420px;">
    <h5 style="font-family:'Playfair Display',serif;font-size:1.15rem;margin-bottom:16px;">Edit User</h5>
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
          <option value="false">Inactive</option>
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
var allUsers = [];

async function loadUsers() {
  var roleFilter   = document.getElementById('role-filter').value;
  var statusFilter = document.getElementById('status-filter').value;
  var res = await API.get('/auth/users/');
  var container = document.getElementById('users-list');

  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load users.</div>';
    return;
  }

  allUsers  = await res.json();
  var data  = allUsers.slice();

  if (roleFilter)                  data = data.filter(function(u){ return u.role === roleFilter; });
  if (statusFilter === 'active')   data = data.filter(function(u){ return u.is_active; });
  if (statusFilter === 'inactive') data = data.filter(function(u){ return !u.is_active; });

  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:32px;color:var(--text-muted);">No users match the selected filters.</div>';
    return;
  }

  var html = '<table class="cg-table"><thead><tr>';
  html += '<th>Name</th><th>ID</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th>';
  html += '</tr></thead><tbody>';

  for (var i = 0; i < data.length; i++) {
    var u        = data[i];
    var joined   = new Date(u.date_joined).toLocaleDateString('en-KE', {month:'short', day:'numeric', year:'numeric'});
    var fullName = (u.first_name || u.last_name) ? (u.first_name + ' ' + u.last_name).trim() : u.username;
    var rc       = u.role === 'admin' ? 'badge-priority' : (u.role === 'approver' ? 'badge-pending' : 'badge-approved');
    var uid      = u.id;
    var urole    = u.role;
    var uactive  = u.is_active;

    html += '<tr>';
    html += '<td style="font-weight:500;">' + fullName + '</td>';
    html += '<td style="font-family:monospace;font-size:0.8rem;color:var(--text-muted);">' + u.username + '</td>';
    html += '<td style="font-size:0.8rem;color:var(--text-muted);">' + (u.email || '-') + '</td>';
    html += '<td><span class="status-badge ' + rc + '">' + urole + '</span></td>';
    html += '<td>' + (uactive ? '<span class="status-badge badge-approved">Active</span>' : '<span class="status-badge badge-pending">Pending</span>') + '</td>';
    html += '<td style="font-size:0.78rem;color:var(--text-muted);">' + joined + '</td>';
    html += '<td><button onclick="openUserModal(' + uid + ')" style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);color:var(--accent);border-radius:4px;padding:3px 10px;font-size:0.75rem;cursor:pointer;">Edit</button></td>';
    html += '</tr>';
  }

  html += '</tbody></table>';
  container.innerHTML = html;
}

function openUserModal(userId) {
  var u = allUsers.find(function(x){ return x.id === userId; });
  if (!u) return;
  document.getElementById('edit-user-id').value = userId;
  document.getElementById('edit-role').value    = u.role;
  document.getElementById('edit-active').value  = u.is_active ? 'true' : 'false';
  document.getElementById('user-modal').style.display = 'flex';
}

function closeUserModal() {
  document.getElementById('user-modal').style.display = 'none';
}

async function saveUser() {
  var userId    = document.getElementById('edit-user-id').value;
  var newRole   = document.getElementById('edit-role').value;
  var newActive = document.getElementById('edit-active').value === 'true';
  var u         = allUsers.find(function(x){ return String(x.id) === String(userId); });
  if (!u) return;

  if (u.role !== newRole) {
    await API.patch('/auth/users/' + userId + '/role/', { role: newRole });
  }
  if (u.is_active !== newActive) {
    await API.patch('/auth/users/' + userId + '/toggle/', {});
  }

  closeUserModal();
  loadUsers();
}

loadUsers();
</script>
{% endblock %}
"""

# ── REPORTS ────────────────────────────────────────────────────
reports = """{% extends 'base.html' %}
{% block title %}Reports{% endblock %}
{% block page_title %}Reports and Analytics{% endblock %}

{% block extra_styles %}
@media print {
  .sidebar, .topbar, .no-print { display: none !important; }
  .main-content { margin-left: 0 !important; }
  body { background: white !important; color: black !important; }
  .cg-card { border: 1px solid #ccc !important; background: white !important; }
  .cg-table th, .cg-table td { color: black !important; border-color: #ccc !important; }
  .print-header { display: block !important; }
}
.print-header { display: none; }
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4 no-print">
  <div style="display:flex;gap:8px;align-items:center;">
    <select id="month-select" onchange="loadReports()" class="cg-input" style="width:auto;padding:6px 12px;">
      <option value="1">January</option><option value="2">February</option>
      <option value="3">March</option><option value="4">April</option>
      <option value="5" selected>May</option><option value="6">June</option>
      <option value="7">July</option><option value="8">August</option>
      <option value="9">September</option><option value="10">October</option>
      <option value="11">November</option><option value="12">December</option>
    </select>
    <select id="year-select" onchange="loadReports()" class="cg-input" style="width:auto;padding:6px 12px;">
      <option value="2026" selected>2026</option>
      <option value="2027">2027</option>
    </select>
  </div>
  <div style="display:flex;gap:8px;">
    <button onclick="window.print()" class="btn-cg-outline" style="font-size:0.82rem;">
      <i class="bi bi-printer me-1"></i> Print
    </button>
    <button onclick="exportCSV()" class="btn-cg-primary" style="font-size:0.82rem;">
      <i class="bi bi-download me-1"></i> Export CSV
    </button>
  </div>
</div>

<div class="print-header" style="margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid #333;">
  <h2 style="margin:0;font-size:1.4rem;">CampusGrid - Facility Utilization Report</h2>
  <p style="margin:4px 0 0;font-size:0.85rem;color:#666;">University of Eastern Africa Baraton</p>
  <p id="print-period" style="margin:4px 0 0;font-size:0.85rem;"></p>
</div>

<div id="reports-content">
  <div style="display:grid;gap:12px;">
    <div class="skeleton" style="height:60px;"></div>
    <div class="skeleton" style="height:180px;"></div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
var reportData   = null;
var conflictData = null;
var MONTHS = ['','January','February','March','April','May','June','July','August','September','October','November','December'];

async function loadReports() {
  var month = document.getElementById('month-select').value;
  var year  = document.getElementById('year-select').value;
  var pp    = document.getElementById('print-period');
  if (pp) pp.textContent = 'Period: ' + MONTHS[parseInt(month)] + ' ' + year;

  var utilRes     = await API.get('/reports/utilization/?month=' + month + '&year=' + year);
  var conflictRes = await API.get('/reports/conflicts/?month=' + month + '&year=' + year);
  var container   = document.getElementById('reports-content');

  if (!utilRes || !utilRes.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load report data.</div>';
    return;
  }

  reportData   = await utilRes.json();
  conflictData = (conflictRes && conflictRes.ok) ? await conflictRes.json() : null;
  var facs     = reportData.facilities || [];

  var html = '<div style="display:grid;gap:20px;">';

  if (facs.length) {
    var totB = 0, totA = 0, totH = 0, totC = 0;
    facs.forEach(function(f){ totB += f.total_bookings; totA += f.approved; totH += parseFloat(f.total_hours_booked); totC += f.conflicts; });

    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;">';
    html += sbox('Total Bookings', totB,               'bi-journal-bookmark', 'rgba(201,168,76,0.15)',  'var(--accent)');
    html += sbox('Approved',       totA,               'bi-check-circle',     'rgba(42,107,74,0.15)',   '#6BAB8A');
    html += sbox('Hours Booked',   totH.toFixed(1)+'h','bi-clock',            'rgba(30,75,143,0.15)',   '#7BA7DC');
    html += sbox('Conflicts',      totC,               'bi-shield-exclamation','rgba(184,134,11,0.15)', 'var(--accent)');
    html += '</div>';
  }

  html += '<div class="cg-card"><div class="cg-card-title">Facility Utilization - ' + MONTHS[parseInt(month)] + ' ' + year + '</div>';
  html += '<div style="overflow-x:auto;"><table class="cg-table" id="util-table"><thead><tr>';
  html += '<th>Facility</th><th>Total</th><th>Approved</th><th>Pending</th><th>Rejected</th><th>Displaced</th><th>Conflicts</th><th>Hours</th>';
  html += '</tr></thead><tbody>';
  facs.forEach(function(f){
    html += '<tr>';
    html += '<td style="font-weight:500;">'                    + f.facility          + '</td>';
    html += '<td style="text-align:center;">'                  + f.total_bookings    + '</td>';
    html += '<td style="text-align:center;color:#6BAB8A;">'    + f.approved          + '</td>';
    html += '<td style="text-align:center;color:var(--accent);">' + f.pending        + '</td>';
    html += '<td style="text-align:center;color:#C4827A;">'    + f.rejected          + '</td>';
    html += '<td style="text-align:center;color:#C49A6C;">'    + f.displaced         + '</td>';
    html += '<td style="text-align:center;color:var(--accent);">' + f.conflicts      + '</td>';
    html += '<td style="text-align:center;">'                  + f.total_hours_booked + 'h</td>';
    html += '</tr>';
  });
  html += '</tbody></table></div></div>';

  if (conflictData && conflictData.total_conflicts > 0) {
    html += '<div class="cg-card"><div class="cg-card-title">Conflict Summary</div>';
    html += '<div style="display:flex;align-items:center;gap:20px;margin-top:12px;">';
    html += '<div style="text-align:center;padding:16px 20px;background:rgba(184,134,11,0.08);border:1px solid rgba(184,134,11,0.2);border-radius:6px;">';
    html += '<div style="font-size:2.4rem;font-weight:700;color:var(--accent);">' + conflictData.total_conflicts + '</div>';
    html += '<div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;">Total</div></div>';
    html += '<div style="flex:1;display:grid;gap:6px;">';
    Object.entries(conflictData.by_facility).forEach(function(e){
      html += '<div style="display:flex;justify-content:space-between;padding:7px 12px;background:var(--bg-secondary);border-radius:4px;font-size:0.84rem;">';
      html += '<span>' + e[0] + '</span><span style="color:var(--accent);font-weight:600;">' + e[1] + ' conflict' + (e[1]!==1?'s':'') + '</span></div>';
    });
    html += '</div></div></div>';
  }

  html += '</div>';
  container.innerHTML = html;
}

function sbox(label, val, icon, bg, color) {
  return '<div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:14px 16px;display:flex;align-items:center;gap:12px;">' +
    '<div style="width:38px;height:38px;border-radius:6px;background:' + bg + ';display:flex;align-items:center;justify-content:center;">' +
    '<i class="bi ' + icon + '" style="color:' + color + ';font-size:1rem;"></i></div>' +
    '<div><div style="font-size:1.6rem;font-weight:700;color:' + color + ';line-height:1;">' + val + '</div>' +
    '<div style="font-size:0.73rem;color:var(--text-muted);margin-top:2px;">' + label + '</div></div></div>';
}

function exportCSV() {
  if (!reportData || !reportData.facilities) return;
  var month = document.getElementById('month-select').value;
  var year  = document.getElementById('year-select').value;
  var csv   = 'Facility,Total,Approved,Pending,Rejected,Displaced,Conflicts,Hours\n';
  reportData.facilities.forEach(function(f){
    csv += f.facility+','+f.total_bookings+','+f.approved+','+f.pending+','+f.rejected+','+f.displaced+','+f.conflicts+','+f.total_hours_booked+'\n';
  });
  var blob = new Blob([csv], {type:'text/csv'});
  var url  = URL.createObjectURL(blob);
  var a    = document.createElement('a');
  a.href   = url;
  a.download = 'CampusGrid_' + MONTHS[parseInt(month)] + '_' + year + '.csv';
  a.click();
  URL.revokeObjectURL(url);
}

loadReports();
</script>
{% endblock %}
"""

w('templates/approvals/queue.html', approvals)
w('templates/users/list.html',      users)
w('templates/reports/index.html',   reports)
print('\nAll three pages fixed.')
