content = """\
{% extends 'base.html' %}
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
      <label class="cg-label">Comments <span style="color:var(--text-muted);font-size:0.72rem;">(optional)</span></label>
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
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load approvals. Status: ' + (res ? res.status : 'no response') + '</div>';
    return;
  }
  const data = await res.json();
  const bookings = data.bookings || data;
  const count    = data.count !== undefined ? data.count : (bookings.length || 0);

  if (!bookings || !bookings.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-check-all" style="font-size:2.5rem;color:var(--accent-green);"></i><p style="margin-top:12px;">No pending bookings. All caught up!</p></div>';
    return;
  }

  let html = '<div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border);">';
  html += '<i class="bi bi-hourglass-split me-2" style="color:var(--accent);"></i>' + count + ' booking' + (count !== 1 ? 's' : '') + ' awaiting review</div>';
  html += '<div style="display:grid;gap:12px;">';

  bookings.forEach(function(b) {
    const startDate = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
    const startTime = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const endTime   = new Date(b.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const submitted = new Date(b.created_at).toLocaleDateString('en-KE', {month:'short', day:'numeric'});
    const userName  = b.user_detail ? b.user_detail.username : (b.user || 'Unknown');
    const facName   = b.facility_detail ? b.facility_detail.name : 'Unknown facility';
    const zoneName  = b.zone_name || 'Entire facility';

    html += '<div style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:6px;padding:16px;">';
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">';
    html += '<div><div style="font-weight:600;font-size:0.9rem;">' + b.purpose + '</div>';
    html += '<div style="font-size:0.76rem;color:var(--text-muted);margin-top:2px;">by ' + userName + '</div></div>';
    html += '<span class="status-badge badge-pending">Pending</span></div>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.82rem;margin-bottom:14px;">';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Facility</div>';
    html += '<div style="font-weight:500;">' + facName + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + zoneName + '</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Date &amp; Time</div>';
    html += '<div style="font-weight:500;">' + startDate + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + startTime + ' \u2014 ' + endTime + '</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Attendance</div>';
    html += '<div style="font-weight:500;">' + b.expected_attendance + ' people</div></div>';
    html += '<div><div style="color:var(--text-muted);font-size:0.7rem;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:2px;">Submitted</div>';
    html += '<div style="font-weight:500;">' + submitted + '</div></div></div>';
    html += '<div style="display:flex;gap:8px;">';
    html += '<button onclick="openApprovalModal(' + b.id + ',\'approve\')" style="flex:1;background:rgba(42,107,74,0.12);border:1px solid rgba(42,107,74,0.3);color:#6BAB8A;border-radius:4px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;transition:all 0.15s;" onmouseover="this.style.background=\'rgba(42,107,74,0.25)\'" onmouseout="this.style.background=\'rgba(42,107,74,0.12)\'"><i class="bi bi-check-lg me-1"></i> Approve</button>';
    html += '<button onclick="openApprovalModal(' + b.id + ',\'reject\')" style="flex:1;background:rgba(123,40,40,0.12);border:1px solid rgba(123,40,40,0.3);color:#C4827A;border-radius:4px;padding:8px;font-size:0.82rem;cursor:pointer;font-weight:500;transition:all 0.15s;" onmouseover="this.style.background=\'rgba(123,40,40,0.25)\'" onmouseout="this.style.background=\'rgba(123,40,40,0.12)\'"><i class="bi bi-x-lg me-1"></i> Reject</button>';
    html += '</div></div>';
  });
  html += '</div>';
  container.innerHTML = html;
}

function openApprovalModal(bookingId, action) {
  document.getElementById('modal-booking-id').value = bookingId;
  document.getElementById('modal-action').value     = action;
  document.getElementById('modal-title').textContent = action === 'approve' ? 'Approve Booking' : 'Reject Booking';
  document.getElementById('modal-confirm-btn').style.background = action === 'approve' ? '#2A6B4A' : '#7B2828';
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
  const res = await API.post('/approvals/' + bookingId + '/' + action + '/', { comments: comments });
  if (res && res.ok) {
    closeApprovalModal();
    loadApprovals();
  }
}

loadApprovals();
</script>
{% endblock %}
"""

with open('templates/approvals/queue.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Approvals template written successfully')
