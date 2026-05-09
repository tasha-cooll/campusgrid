content = """\
{% extends 'base.html' %}
{% block title %}New Booking{% endblock %}
{% block page_title %}New Booking Request{% endblock %}

{% block content %}
<div style="max-width:640px;">
  <div class="cg-card">
    <h5 style="font-size:1rem;font-weight:600;margin-bottom:4px;">Submit a Booking Request</h5>
    <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">
      Select a facility, zone and time. The system will automatically check for conflicts.
    </p>
    <div id="form-alert" style="display:none;"></div>
    <div id="conflict-alert" style="display:none;"></div>
    <div style="display:grid;gap:16px;">
      <div>
        <label class="cg-label">Facility</label>
        <select class="cg-input" id="facility-select" onchange="loadZones()">
          <option value="">Select a facility...</option>
        </select>
      </div>
      <div>
        <label class="cg-label">Zone <span style="color:var(--text-muted);font-size:0.75rem;">(optional)</span></label>
        <select class="cg-input" id="zone-select">
          <option value="">Entire facility</option>
        </select>
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
        <input type="text" class="cg-input" id="purpose" placeholder="e.g. Basketball practice"/>
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
const params = new URLSearchParams(window.location.search);
if (params.get('date') && params.get('hour')) {
  const date = params.get('date');
  const hour = params.get('hour').padStart(2,'0');
  const endH = String(parseInt(hour) + 2).padStart(2,'0');
  document.getElementById('start-time').value = date + 'T' + hour + ':00';
  document.getElementById('end-time').value   = date + 'T' + endH + ':00';
}

const priorityCheck = document.getElementById('is-priority');
if (priorityCheck) {
  priorityCheck.addEventListener('change', function() {
    document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
  });
}

async function loadFacilities() {
  const res = await API.get('/facilities/');
  if (res && res.ok) {
    const data = await res.json();
    const sel  = document.getElementById('facility-select');
    data.forEach(function(f) {
      const opt = document.createElement('option');
      opt.value = f.id;
      opt.textContent = f.name;
      sel.appendChild(opt);
    });
    if (params.get('facility')) sel.value = params.get('facility');
  }
}

async function loadZones() {
  const facilityId = document.getElementById('facility-select').value;
  const sel = document.getElementById('zone-select');
  sel.innerHTML = '<option value="">Entire facility</option>';
  if (!facilityId) return;
  const res = await API.get('/facilities/' + facilityId + '/zones/');
  if (res && res.ok) {
    const data = await res.json();
    data.forEach(function(z) {
      const opt = document.createElement('option');
      opt.value = z.id;
      opt.textContent = z.name + ' (capacity: ' + z.capacity + ')';
      sel.appendChild(opt);
    });
  }
  checkConflict();
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
  const zoneId = document.getElementById('zone-select').value;
  if (zoneId) payload.zone_id = parseInt(zoneId);
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
  const toLocal = function(iso) { return new Date(iso).toISOString().slice(0,16); };
  document.getElementById('start-time').value = toLocal(start);
  document.getElementById('end-time').value   = toLocal(end);
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
  const zoneId = document.getElementById('zone-select').value;
  if (zoneId) payload.zone = parseInt(zoneId);
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

with open('templates/bookings/new.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('New booking template written successfully')
