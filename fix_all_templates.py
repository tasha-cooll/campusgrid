import os

# ─── BOOKINGS LIST ───────────────────────────────────────────────
bookings_list = """\
{% extends 'base.html' %}
{% block title %}My Bookings{% endblock %}
{% block page_title %}My Bookings{% endblock %}

{% block content %}
{% if request.GET.success %}
<div class="cg-alert cg-alert-success mb-4">
  <i class="bi bi-check-circle me-2"></i>Booking submitted successfully. It is now pending approval.
</div>
{% endif %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div style="font-size:0.85rem;color:var(--text-muted);">Your booking history and upcoming reservations.</div>
  <a href="/bookings/new/" class="btn-cg-primary"><i class="bi bi-plus-lg me-1"></i> New Booking</a>
</div>
<div class="cg-card">
  <div id="bookings-list">
    <div style="text-align:center;padding:40px;color:var(--text-muted);">
      <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
      <p style="margin-top:8px;">Loading your bookings...</p>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadBookings() {
  const res = await API.get('/bookings/');
  const container = document.getElementById('bookings-list');
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load bookings.</div>';
    return;
  }
  const data = await res.json();
  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-calendar-x" style="font-size:2.5rem;"></i><p style="margin-top:12px;">No bookings yet.</p><a href="/bookings/new/" class="btn-cg-primary" style="display:inline-block;margin-top:12px;">Make your first booking</a></div>';
    return;
  }
  let html = '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">';
  html += '<thead><tr style="border-bottom:1px solid var(--border);color:var(--text-muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">';
  html += '<th style="padding:10px 12px;text-align:left;">Facility / Zone</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Date &amp; Time</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Purpose</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Status</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Actions</th>';
  html += '</tr></thead><tbody>';
  data.forEach(function(b) {
    const startDate = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
    const startTime = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const endTime   = new Date(b.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    html += '<tr style="border-bottom:1px solid var(--border);">';
    html += '<td style="padding:12px;"><div style="font-weight:500;">' + b.facility_detail.name + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + (b.zone_name || 'Entire facility') + '</div>';
    if (b.is_priority) html += '<span class="status-badge badge-priority" style="margin-top:4px;display:inline-block;">Priority</span>';
    html += '</td>';
    html += '<td style="padding:12px;"><div>' + startDate + '</div><div style="color:var(--text-muted);font-size:0.78rem;">' + startTime + ' \u2014 ' + endTime + '</div></td>';
    html += '<td style="padding:12px;">' + b.purpose + '</td>';
    html += '<td style="padding:12px;"><span class="status-badge badge-' + b.status + '">' + b.status_display + '</span></td>';
    html += '<td style="padding:12px;">';
    if (b.status === 'pending') {
      html += '<button onclick="cancelBooking(' + b.id + ')" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#EF4444;border-radius:6px;padding:4px 10px;font-size:0.75rem;cursor:pointer;">Cancel</button>';
    } else {
      html += '\u2014';
    }
    html += '</td></tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

async function cancelBooking(id) {
  if (!confirm('Are you sure you want to cancel this booking?')) return;
  const res = await API.delete('/bookings/' + id + '/');
  if (res && res.ok) loadBookings();
}

loadBookings();
</script>
{% endblock %}
"""

# ─── NEW BOOKING FORM ────────────────────────────────────────────
bookings_new = """\
{% extends 'base.html' %}
{% block title %}New Booking{% endblock %}
{% block page_title %}New Booking Request{% endblock %}

{% block content %}
<div style="max-width:640px;">
  <div class="cg-card">
    <h5 style="font-size:1rem;font-weight:600;margin-bottom:4px;">Submit a Booking Request</h5>
    <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">
      Select a facility and time slot. The system will check for conflicts automatically.
    </p>
    <div id="form-alert" style="display:none;"></div>
    <div id="conflict-alert" style="display:none;"></div>

    <div style="display:grid;gap:16px;">

      <div>
        <label class="cg-label">Facility</label>
        <select class="cg-input" id="facility-select" onchange="onFacilityChange()">
          <option value="">Select a facility...</option>
        </select>
        <div id="facility-info" style="display:none;margin-top:8px;padding:10px 12px;background:rgba(46,117,182,0.08);border:1px solid rgba(46,117,182,0.2);border-radius:8px;font-size:0.82rem;color:var(--text-muted);"></div>
      </div>

      <div id="zone-section" style="display:none;">
        <label class="cg-label">Zone <span style="color:var(--text-muted);font-size:0.75rem;">(optional — leave blank to book entire facility)</span></label>
        <div id="zone-options" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:4px;"></div>
        <input type="hidden" id="zone-select" value=""/>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <div>
          <label class="cg-label">Start Date &amp; Time</label>
          <input type="datetime-local" class="cg-input" id="start-time" onchange="checkConflict()"/>
        </div>
        <div>
          <label class="cg-label">End Date &amp; Time</label>
          <input type="datetime-local" class="cg-input" id="end-time" onchange="checkConflict()"/>
        </div>
      </div>

      <div>
        <label class="cg-label">Purpose</label>
        <input type="text" class="cg-input" id="purpose" placeholder="e.g. Basketball practice, Club meeting"/>
      </div>

      <div>
        <label class="cg-label">Expected Attendance</label>
        <input type="number" class="cg-input" id="attendance" placeholder="Number of people" min="1"/>
      </div>

      <div>
        <label class="cg-label">Additional Notes <span style="color:var(--text-muted);font-size:0.75rem;">(optional)</span></label>
        <textarea class="cg-input" id="notes" rows="3" placeholder="Any additional information..."></textarea>
      </div>

      {% if user.role == 'admin' %}
      <div style="padding:16px;background:rgba(139,0,0,0.08);border:1px solid rgba(139,0,0,0.2);border-radius:8px;">
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer;">
          <input type="checkbox" id="is-priority" style="width:16px;height:16px;accent-color:#EF4444;"/>
          <span style="font-size:0.875rem;font-weight:500;color:#FF4444;">Priority Booking</span>
        </label>
        <p style="font-size:0.78rem;color:var(--text-muted);margin-top:6px;margin-bottom:12px;">
          Priority bookings displace existing bookings. Use only for official university events.
        </p>
        <input type="text" class="cg-input" id="priority-reason" placeholder="Reason e.g. Graduation Ceremony" style="display:none;"/>
      </div>
      {% endif %}

    </div>

    <div style="display:flex;gap:12px;margin-top:24px;">
      <button class="btn-cg-primary" onclick="submitBooking()" id="submit-btn">
        <i class="bi bi-send me-1"></i> Submit Request
      </button>
      <a href="/calendar/" class="btn-cg-outline">Cancel</a>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
let facilitiesData = [];
let selectedZoneId = null;

const params = new URLSearchParams(window.location.search);

const priorityCheck = document.getElementById('is-priority');
if (priorityCheck) {
  priorityCheck.addEventListener('change', function() {
    document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
  })


async function loadFacilities() {
  console.log('loadFacilities called');
  const res = await API.get('/facilities/');
  if (res && res.ok) {
    facilitiesData = await res.json();
    const sel = document.getElementById('facility-select');
    facilitiesData.forEach(function(f) {
      const opt = document.createElement('option');
      opt.value = String(f.id);
      opt.textContent = f.name + ' (capacity: ' + f.capacity + ')';
      sel.appendChild(opt);
    });

    // Pre-select after options are fully loaded
    const preSelected = new URLSearchParams(window.location.search).get('facility');
    if (preSelected) {
      sel.value = preSelected;
      if (sel.value === preSelected) {
        onFacilityChange();
      } else {
        console.log('Could not find facility id:', preSelected, 'in options:', Array.from(sel.options).map(function(o){ return o.value; }));
      }
    }
  }
}

// Remove the old loadFacilities() call at bottom and replace with:
document.addEventListener('DOMContentLoaded', function() {
  loadFacilities();
});

function onFacilityChange() {
  const facilityId = parseInt(document.getElementById('facility-select').value);
  const facility   = facilitiesData.find(function(f) { return f.id === facilityId; });
  const infoBox    = document.getElementById('facility-info');
  const zoneSection = document.getElementById('zone-section');
  const zoneOptions = document.getElementById('zone-options');
  selectedZoneId   = null;
  document.getElementById('zone-select').value = '';

  if (!facility) {
    infoBox.style.display    = 'none';
    zoneSection.style.display = 'none';
    return;
  }

  let infoHtml = '<i class="bi bi-geo-alt me-1"></i>' + facility.location;
  infoHtml += ' &nbsp;&middot;&nbsp; <i class="bi bi-people me-1"></i>' + facility.capacity + ' capacity';
  if (facility.recurring_blocks && facility.recurring_blocks.length) {
    infoHtml += '<div style="margin-top:6px;color:#F4A261;">';
    facility.recurring_blocks.forEach(function(b) {
      infoHtml += '<i class="bi bi-lock me-1"></i>' + b.label + ' every ' + b.day_name + ' ' + b.start_time + '\u2013' + b.end_time + '<br/>';
    });
    infoHtml += '</div>';
  }
  infoBox.innerHTML      = infoHtml;
  infoBox.style.display  = 'block';

  if (facility.zones && facility.zones.length) {
    let zonesHtml = '<button onclick="selectZone(null, this)" class="zone-btn active" style="background:rgba(46,117,182,0.15);border:1px solid var(--accent);border-radius:8px;padding:6px 14px;font-size:0.8rem;color:var(--accent);cursor:pointer;font-weight:500;">Entire facility</button>';
    facility.zones.forEach(function(z) {
      zonesHtml += '<button onclick="selectZone(' + z.id + ', this)" class="zone-btn" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:8px;padding:6px 14px;font-size:0.8rem;color:var(--text-muted);cursor:pointer;">';
      zonesHtml += z.name + ' <span style="font-size:0.72rem;">(cap: ' + z.capacity + ')</span></button>';
    });
    zoneOptions.innerHTML    = zonesHtml;
    zoneSection.style.display = 'block';
  } else {
    zoneSection.style.display = 'none';
  }

  checkConflict();
}

function selectZone(zoneId, btn) {
  selectedZoneId = zoneId;
  document.getElementById('zone-select').value = zoneId || '';
  document.querySelectorAll('.zone-btn').forEach(function(b) {
    b.style.background = 'var(--bg-primary)';
    b.style.borderColor = 'var(--border)';
    b.style.color = 'var(--text-muted)';
    b.style.fontWeight = 'normal';
  });
  btn.style.background  = 'rgba(46,117,182,0.15)';
  btn.style.borderColor = 'var(--accent)';
  btn.style.color       = 'var(--accent)';
  btn.style.fontWeight  = '500';
  checkConflict();
}

if (params.get('date') && params.get('hour')) {
  const date = params.get('date');
  const hour = params.get('hour').padStart(2,'0');
  const endH = String(parseInt(hour) + 2).padStart(2,'0');
  document.getElementById('start-time').value = date + 'T' + hour + ':00';
  document.getElementById('end-time').value   = date + 'T' + endH + ':00';
}

let conflictTimer;
function checkConflict() {
  clearTimeout(conflictTimer);
  conflictTimer = setTimeout(_doConflictCheck, 600);
}

async function _doConflictCheck() {
  const facilityId = document.getElementById('facility-select').value;
  const startTime  = document.getElementById('start-time').value;
  const endTime    = document.getElementById('end-time').value;
  if (!facilityId || !startTime || !endTime) return;
  const payload = {
    facility_id: parseInt(facilityId),
    start_time:  new Date(startTime).toISOString(),
    end_time:    new Date(endTime).toISOString(),
  };
  if (selectedZoneId) payload.zone_id = selectedZoneId;
  const res   = await API.post('/bookings/check-conflict/', payload);
  const alert = document.getElementById('conflict-alert');
  const btn   = document.getElementById('submit-btn');
  if (res && res.ok) {
    const data = await res.json();
    if (!data.available) {
      let html = '<div class="cg-alert cg-alert-warning"><strong><i class="bi bi-exclamation-triangle me-2"></i>' + data.message + '</strong>';
      if (data.reason === 'recurring_block') {
        html += '<div style="margin-top:8px;font-size:0.82rem;">Blocked by: <strong>' + data.blocked_by + '</strong> every ' + data.day + ' ' + data.time + '</div>';
        btn.disabled = true; btn.style.opacity = '0.5';
      } else if (data.alternative_slots) {
        html += '<div style="margin-top:10px;font-size:0.82rem;"><strong>Available alternatives:</strong><div style="margin-top:8px;display:grid;gap:6px;">';
        data.alternative_slots.forEach(function(slot) {
          const s = new Date(slot.start_time).toLocaleString('en-KE', {weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
          const e = new Date(slot.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
          html += '<button onclick="useSlot(\'' + slot.start_time + '\',\'' + slot.end_time + '\')" style="background:rgba(46,117,182,0.1);border:1px solid var(--accent);border-radius:6px;color:var(--accent);padding:6px 12px;font-size:0.8rem;cursor:pointer;text-align:left;"><i class="bi bi-clock me-1"></i>' + s + ' \u2014 ' + e + '</button>';
        });
        html += '</div></div>';
        btn.disabled = true; btn.style.opacity = '0.5';
      }
      html += '</div>';
      alert.innerHTML = html; alert.style.display = 'block';
    } else {
      alert.innerHTML = '<div class="cg-alert cg-alert-success"><i class="bi bi-check-circle me-2"></i>' + data.message + '</div>';
      alert.style.display = 'block';
      btn.disabled = false; btn.style.opacity = '1';
    }
  }
}

function useSlot(start, end) {
  document.getElementById('start-time').value = new Date(start).toISOString().slice(0,16);
  document.getElementById('end-time').value   = new Date(end).toISOString().slice(0,16);
  document.getElementById('conflict-alert').style.display = 'none';
  document.getElementById('submit-btn').disabled = false;
  document.getElementById('submit-btn').style.opacity = '1';
}

async function submitBooking() {
  const facilityId = document.getElementById('facility-select').value;
  const startTime  = document.getElementById('start-time').value;
  const endTime    = document.getElementById('end-time').value;
  const purpose    = document.getElementById('purpose').value;
  const attendance = document.getElementById('attendance').value;
  if (!facilityId || !startTime || !endTime || !purpose || !attendance) {
    document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please fill in all required fields.</div>';
    document.getElementById('form-alert').style.display = 'block';
    return;
  }
  const payload = {
    facility: parseInt(facilityId),
    start_time: new Date(startTime).toISOString(),
    end_time:   new Date(endTime).toISOString(),
    purpose: purpose,
    expected_attendance: parseInt(attendance),
    notes: document.getElementById('notes').value,
    is_priority: false,
    priority_reason: '',
  };
  if (selectedZoneId) payload.zone = selectedZoneId;
  const pc = document.getElementById('is-priority');
  if (pc && pc.checked) {
    payload.is_priority     = true;
    payload.priority_reason = document.getElementById('priority-reason').value;
  }
  const btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.textContent = 'Submitting...';
  const res = await API.post('/bookings/', payload);
  if (res) {
    const data = await res.json();
    if (res.ok) {
      window.location.href = '/bookings/?success=1';
    } else {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-send me-1"></i> Submit Request';
      document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>' + JSON.stringify(data) + '</div>';
      document.getElementById('form-alert').style.display = 'block';
    }
  }
}

loadFacilities();
</script>
{% endblock %}
"""

# ─── WRITE ALL FILES ─────────────────────────────────────────────
files = {
    'templates/bookings/list.html': bookings_list,
    'templates/bookings/new.html':  bookings_new,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Written: ' + path)

print('All templates written successfully')
