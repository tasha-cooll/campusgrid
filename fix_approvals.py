content = """\
{% extends 'base.html' %}
{% block title %}Approval Queue{% endblock %}
{% block page_title %}Pending Approvals{% endblock %}

{% block content %}
<div class="cg-card">
  <div id="approvals-list">
    <div style="text-align:center;padding:40px;color:var(--text-muted);">
      <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
      <p style="margin-top:8px;">Loading pending bookings...</p>
    </div>
  </div>
</div>

<div id="approval-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:16px;padding:28px;width:100%;max-width:440px;">
    <h5 style="margin-bottom:16px;" id="modal-title">Review Booking</h5>
    <input type="hidden" id="modal-booking-id"/>
    <input type="hidden" id="modal-action"/>
    <div style="margin-bottom:16px;">
      <label class="cg-label">Comments <span style="color:var(--text-muted);">(optional)</span></label>
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
async function loadApprovals() {
  const res = await API.get('/approvals/pending/');
  const container = document.getElementById('approvals-list');
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load approvals.</div>';
    return;
  }
  const data = await res.json();
  if (!data.bookings || !data.bookings.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-check-all" style="font-size:2.5rem;color:#22C55E;"></i><p style="margin-top:12px;">No pending bookings. All caught up!</p></div>';
    return;
  }
  let html = '<div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:16px;">' + data.count + ' booking' + (data.count !== 1 ? 's' : '') + ' awaiting review</div>';
  html += '<div style="display:grid;gap:12px;">';
  data.bookings.forEach(function(b) {
    const startDate = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
    const startTime = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const endTime   = new Date(b.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const submitted = new Date(b.created_at).toLocaleDateString('en-KE', {month:'short', day:'numeric'});
    html += '<div style="background:var(--bg-primary);border:1px solid var(--border);border-radius:10px;padding:16px;">';
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">';
    html += '<div><div style="font-weight:600;">' + b.purpose + '</div>';
    html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;">by ' + b.user_detail.username + '</div></div>';
    html += '<span class="status-badge badge-pending">Pending</span></div>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;margin-bottom:14px;">';
    html += '<div><span style="color:var(--text-muted);">Facility</span><div style="font-weight:500;">' + b.facility_detail.name + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + (b.zone_name || 'Entire facility') + '</div></div>';
    html += '<div><span style="color:var(--text-muted);">Date &amp; Time</span><div style="font-weight:500;">' + startDate + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + startTime + ' \u2014 ' + endTime + '</div></div>';
    html += '<div><span style="color:var(--text-muted);">Attendance</span><div style="font-weight:500;">' + b.expected_attendance + ' people</div></div>';
    html += '<div><span style="color:var(--text-muted);">Submitted</span><div style="font-weight:500;">' + submitted + '</div></div></div>';
    html += '<div style="display:flex;gap:8px;">';
    html += '<button onclick="openApprovalModal(' + b.id + ',\'approve\')" style="flex:1;background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#22C55E;border-radius:8px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;"><i class="bi bi-check-lg me-1"></i> Approve</button>';
    html += '<button onclick="openApprovalModal(' + b.id + ',\'reject\')" style="flex:1;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#EF4444;border-radius:8px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;"><i class="bi bi-x-lg me-1"></i> Reject</button>';
    html += '</div></div>';
  });
  html += '</div>';
  container.innerHTML = html;
}

function openApprovalModal(bookingId, action) {
  document.getElementById('modal-booking-id').value = bookingId;
  document.getElementById('modal-action').value     = action;
  document.getElementById('modal-title').textContent = action === 'approve' ? 'Approve Booking' : 'Reject Booking';
  document.getElementById('modal-confirm-btn').style.background = action === 'approve' ? '#22C55E' : '#EF4444';
  document.getElementById('modal-comments').value = '';
  document.getElementById('approval-modal').style.display = 'flex';
}

function closeApprovalModal() {
  document.getElementById('approval-modal').style.display = 'none';
}

async function confirmAction() {
  const bookingId = document.getElementById('modal-booking-id').value;
  const action    = document.getElementById('modal-action').value;
  const comments  = document.getElementById('modal-comments').value;
  const res = await API.post('/approvals/' + bookingId + '/' + action + '/', {comments: comments});
  if (res && res.ok) { closeApprovalModal(); loadApprovals(); }
}

loadApprovals();
</script>
{% endblock %}
"""

with open('templates/approvals/queue.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Approvals template written successfully')
