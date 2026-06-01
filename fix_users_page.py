content = """\
{% extends 'base.html' %}
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
      <option value="inactive">Pending Activation</option>
    </select>
  </div>
</div>

<div class="cg-card">
  <div id="users-list">
    <div style="display:grid;gap:8px;">
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
      <div class="skeleton" style="height:44px;"></div>
    </div>
  </div>
</div>

<div id="user-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:28px;width:100%;max-width:420px;">
    <h5 style="font-family:'Playfair Display',serif;font-size:1.15rem;margin-bottom:6px;" id="user-modal-title">Edit User</h5>
    <div class="gold-line"></div>
    <input type="hidden" id="edit-user-id"/>
    <div style="display:grid;gap:14px;">
      <div>
        <label class="cg-label">Role</label>
        <select id="edit-role" class="cg-input">
          <option value="requester">Requester (Student / Club Leader)</option>
          <option value="approver">Approver (Sports Director)</option>
          <option value="admin">Administrator</option>
        </select>
      </div>
      <div>
        <label class="cg-label">Account Status</label>
        <select id="edit-active" class="cg-input">
          <option value="true">Active — can sign in</option>
          <option value="false">Inactive — pending activation</option>
        </select>
      </div>
    </div>
    <div style="display:flex;gap:12px;margin-top:20px;">
      <button class="btn-cg-primary" onclick="saveUser()"><i class="bi bi-check-lg me-1"></i> Save Changes</button>
      <button class="btn-cg-outline" onclick="closeUserModal()">Cancel</button>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
var allUsers = [];

async function loadUsers() {
  const roleFilter   = document.getElementById('role-filter').value;
  const statusFilter = document.getElementById('status-filter').value;
  const res = await API.get('/auth/users/');
  const container = document.getElementById('users-list');

  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load users. Make sure you are logged in as Admin.</div>';
    return;
  }

  allUsers = await res.json();
  var data  = allUsers;

  if (roleFilter)                  data = data.filter(function(u){ return u.role === roleFilter; });
  if (statusFilter === 'active')   data = data.filter(function(u){ return u.is_active; });
  if (statusFilter === 'inactive') data = data.filter(function(u){ return !u.is_active; });

  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:32px;color:var(--text-muted);">No users match the selected filters.</div>';
    return;
  }

  var html = '<table class="cg-table">';
  html += '<thead><tr>';
  html += '<th>Name</th><th>ID</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th>';
  html += '</tr></thead><tbody>';

  data.forEach(function(u) {
    const joined   = new Date(u.date_joined).toLocaleDateString('en-KE', {month:'short', day:'numeric', year:'numeric'});
    const fullName = (u.first_name || u.last_name) ? (u.first_name + ' ' + u.last_name).trim() : u.username;
    const roleClass = u.role === 'admin' ? 'badge-priority' : u.role === 'approver' ? 'badge-pending' : 'badge-approved';

    html += '<tr>';
    html += '<td style="font-weight:500;">' + fullName + '</td>';
    html += '<td style="font-family:monospace;font-size:0.8rem;color:var(--text-muted);">' + u.username + '</td>';
    html += '<td style="font-size:0.8rem;color:var(--text-muted);">' + (u.email || '\u2014') + '</td>';
    html += '<td><span class="status-badge ' + roleClass + '">' + u.role + '</span></td>';
    html += '<td>';
    if (u.is_active) {
      html += '<span class="status-badge badge-approved">Active</span>';
    } else {
      html += '<span class="status-badge badge-pending">Pending</span>';
    }
    html += '</td>';
    html += '<td style="font-size:0.78rem;color:var(--text-muted);">' + joined + '</td>';
    html += '<td><button onclick="openUserModal(' + u.id + ',\'' + u.role + '\',' + u.is_active + ')" style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);color:var(--accent);border-radius:4px;padding:3px 10px;font-size:0.75rem;cursor:pointer;transition:all 0.15s;" onmouseover="this.style.background=\'rgba(201,168,76,0.18)\'" onmouseout="this.style.background=\'rgba(201,168,76,0.08)\'">Edit</button></td>';
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
  const userId     = document.getElementById('edit-user-id').value;
  const newRole    = document.getElementById('edit-role').value;
  const newActive  = document.getElementById('edit-active').value === 'true';
  const user       = allUsers.find(function(u){ return String(u.id) === String(userId); });

  var promises = [];

  if (user && user.role !== newRole) {
    promises.push(API.patch('/auth/users/' + userId + '/role/', { role: newRole }));
  }

  if (user && user.is_active !== newActive) {
    promises.push(API.patch('/auth/users/' + userId + '/toggle/', {}));
  }

  if (promises.length) {
    await Promise.all(promises);
  }

  closeUserModal();
  loadUsers();
}

loadUsers();
</script>
{% endblock %}
"""

with open('templates/users/list.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('User management template written successfully')
