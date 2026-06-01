import os

content = """\
{% extends 'base.html' %}
{% block title %}New Booking{% endblock %}
{% block page_title %}New Booking Request{% endblock %}

{% block content %}
<div style="max-width:640px;">
  <div class="cg-card">
    <h5 style="font-family:'EB Garamond',serif;font-size:1.3rem;margin-bottom:4px;">Submit a Booking Request</h5>
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
          {% for facility in facilities %}
          <option value="{{ facility.id }}"
            data-capacity="{{ facility.capacity }}"
            data-location="{{ facility.location }}"
            data-zones="{{ facility.zones_json }}"
            data-blocks="{{ facility.blocks_json }}">
            {{ facility.name }} (capacity: {{ facility.capacity }})
          </option>
          {% endfor %}
        </select>
        <div id="facility-info" style="display:none;margin-top:8px;padding:10px 12px;background:rgba(201,168,76,0.06);border:1px solid rgba(201,168,76,0.15);border-radius:4px;font-size:0.82rem;color:var(--text-muted);"></div>
      </div>

      <div id="zone-section" style="display:none;">
        <label class="cg-label">Zone <span style="color:var(--text-muted);font-size:0.72rem;">(optional)</span></label>
        <div id="zone-options" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:4px;"></div>
        <input type="hidden" id="zone-id" value=""/>
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
        <label class="cg-label">Additional Notes <span style="color:var(--text-muted);font-size:0.72rem;">(optional)</span></label>
        <textarea class="cg-input" id="notes" rows="3" placeholder="Any additional information..."></textarea>
      </div>

      {% if user.role == 'admin' %}
      <div style="padding:16px;background:rgba(139,58,58,0.08);border:1px solid rgba(139,58,58,0.2);border-radius:6px;">
        <label style="display:flex;align-items:center;gap:10px;cursor:pointer;">
          <input type="checkbox" id="is-priority" style="width:16px;height:16px;accent-color:#8B3A3A;"/>
          <span style="font-size:0.875rem;font-weight:500;color:#D4908A;">Priority Booking</span>
        </label>
        <p style="font-size:0.78rem;color:var(--text-muted);margin-top:6px;margin-bottom:12px;">
          Priority bookings displace existing bookings. Use only for official university events.
        </p>
        <input type="text" class="cg-input" id="priority-reason"
               placeholder="Reason e.g. Graduation Ceremony" style="display:none;"/>
      </div>
      {% endif %}
    </div>

    <div style="display:flex;gap:12px;margin-top:24px;">
      <button class="btn-cg-primary" id="submit-btn" onclick="submitBooking()">
        <i class="bi bi-send me-1"></i> Submit Request
      </button>
      <a href="/calendar/" class="btn-cg-outline">Cancel</a>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
var selectedZoneId = null;
var isSubmitting   = false;
var urlParams      = new URLSearchParams(window.location.search);

// Pre-fill date/time from calendar click
if (urlParams.get('date') && urlParams.get('hour')) {
  var d    = urlParams.get('date');
  var h    = urlParams.get('hour').padStart(2, '0');
  var endH = String(parseInt(h) + 2).padStart(2, '0');
  document.getElementById('start-time').value = d + 'T' + h + ':00';
  document.getElementById('end-time').value   = d + 'T' + endH + ':00';
}

// Pre-select facility from URL
var preSelected = urlParams.get('facility');
if (preSelected) {
  var sel = document.getElementById('facility-select');
  sel.value = preSelected;
  if (sel.value) onFacilityChange();
}

// Priority checkbox
var pc = document.getElementById('is-priority');
if (pc) {
  pc.addEventListener('change', function() {
    document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
  });
}

function onFacilityChange() {
  var sel      = document.getElementById('facility-select');
  var opt      = sel.options[sel.selectedIndex];
  var infoBox  = document.getElementById('facility-info');
  var zoneSec  = document.getElementById('zone-section');
  var zoneOpts = document.getElementById('zone-options');
  selectedZoneId = null;
  document.getElementById('zone-id').value = '';

  if (!sel.value) {
    infoBox.style.display = 'none';
    zoneSec.style.display = 'none';
    return;
  }

  var loc    = opt.getAttribute('data-location') || '';
  var cap    = opt.getAttribute('data-capacity') || '';
  var zones  = [];
  var blocks = [];

  try { zones  = JSON.parse(opt.getAttribute('data-zones')  || '[]'); } catch(e) {}
  try { blocks = JSON.parse(opt.getAttribute('data-blocks') || '[]'); } catch(e) {}

  var info = '<i class="bi bi-geo-alt me-1"></i>' + loc + ' &nbsp;&middot;&nbsp; <i class="bi bi-people me-1"></i>' + cap + ' capacity';
  if (blocks.length) {
    info += '<div style="margin-top:6px;color:var(--accent-amber);">';
    blocks.forEach(function(b) {
      info += '<i class="bi bi-lock me-1"></i>' + b.label + ' every ' + b.day_name + ' ' + b.start_time + '\u2013' + b.end_time + '<br/>';
    });
    info += '</div>';
  }
  infoBox.innerHTML     = info;
  infoBox.style.display = 'block';

  if (zones.length) {
    var zh = '<button type="button" onclick="selectZone(null,this)" class="zone-btn" style="background:rgba(201,168,76,0.15);border:1px solid var(--accent);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--accent);cursor:pointer;font-weight:600;">Entire facility</button>';
    zones.forEach(function(z) {
      zh += '<button type="button" onclick="selectZone(' + z.id + ',this)" class="zone-btn" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--text-muted);cursor:pointer;">';
      zh += z.name + ' <span style="font-size:0.7rem;">(cap: ' + z.capacity + ')</span></button>';
    });
    zoneOpts.innerHTML    = zh;
    zoneSec.style.display = 'block';
  } else {
    zoneSec.style.display = 'none';
  }
  checkConflict();
}

function selectZone(zoneId, btn) {
  selectedZoneId = zoneId;
  document.getElementById('zone-id').value = zoneId || '';
  document.querySelectorAll('.zone-btn').forEach(function(b) {
    b.style.background  = 'var(--bg-primary)';
    b.style.borderColor = 'var(--border)';
    b.style.color       = 'var(--text-muted)';
    b.style.fontWeight  = 'normal';
  });
  btn.style.background  = 'rgba(201,168,76,0.15)';
  btn.style.borderColor = 'var(--accent)';
  btn.style.color       = 'var(--accent)';
  btn.style.fontWeight  = '600';
  checkConflict();
}

var conflictTimer;
function checkConflict() {
  clearTimeout(conflictTimer);
  conflictTimer = setTimeout(_doCheck, 700);
}

async function _doCheck() {
  var fid   = document.getElementById('facility-select').value;
  var start = document.getElementById('start-time').value;
  var end   = document.getElementById('end-time').value;
  if (!fid || !start || !end) return;

  var payload = {
    facility_id: parseInt(fid),
    start_time:  new Date(start).toISOString(),
    end_time:    new Date(end).toISOString()
  };
  if (selectedZoneId) payload.zone_id = selectedZoneId;

  var alertEl = document.getElementById('conflict-alert');
  var btn     = document.getElementById('submit-btn');

  try {
    var res  = await API.post('/bookings/check-conflict/', payload);
    if (!res) return;
    var data = await res.json();

    if (!data.available) {
      var html = '<div class="cg-alert cg-alert-warning"><strong><i class="bi bi-exclamation-triangle me-2"></i>' + data.message + '</strong>';
      if (data.reason === 'recurring_block') {
        html += '<div style="margin-top:8px;font-size:0.82rem;">Blocked by: <strong>' + data.blocked_by + '</strong> every ' + data.day + ' ' + data.time + '</div>';
        btn.disabled = true;
        btn.style.opacity = '0.5';
      } else if (data.alternative_slots && data.alternative_slots.length) {
        html += '<div style="margin-top:10px;font-size:0.82rem;"><strong>Available alternatives:</strong><div style="margin-top:8px;display:grid;gap:6px;">';
        data.alternative_slots.forEach(function(slot) {
          var s = new Date(slot.start_time).toLocaleString('en-KE', {weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
          var e = new Date(slot.end_time).toLocaleTimeString('en-KE', {hour:'2-digit',minute:'2-digit'});
          html += '<button type="button" onclick="useSlot(\'' + slot.start_time + '\',\'' + slot.end_time + '\')" style="background:rgba(201,168,76,0.08);border:1px solid var(--accent);border-radius:4px;color:var(--accent);padding:6px 12px;font-size:0.8rem;cursor:pointer;text-align:left;"><i class="bi bi-clock me-1"></i>' + s + ' \u2014 ' + e + '</button>';
        });
        html += '</div></div>';
        btn.disabled = true;
        btn.style.opacity = '0.5';
      }
      html += '</div>';
      alertEl.innerHTML = html;
      alertEl.style.display = 'block';
    } else {
      alertEl.innerHTML = '<div class="cg-alert cg-alert-success"><i class="bi bi-check-circle me-2"></i>' + data.message + '</div>';
      alertEl.style.display = 'block';
      btn.disabled = false;
      btn.style.opacity = '1';
    }
  } catch(e) {}
}

function useSlot(start, end) {
  document.getElementById('start-time').value = new Date(start).toISOString().slice(0,16);
  document.getElementById('end-time').value   = new Date(end).toISOString().slice(0,16);
  document.getElementById('conflict-alert').style.display = 'none';
  document.getElementById('submit-btn').disabled    = false;
  document.getElementById('submit-btn').style.opacity = '1';
}

async function submitBooking() {
  if (isSubmitting) return;

  var fid        = document.getElementById('facility-select').value;
  var startVal   = document.getElementById('start-time').value;
  var endVal     = document.getElementById('end-time').value;
  var purpose    = document.getElementById('purpose').value.trim();
  var attendance = document.getElementById('attendance').value;
  var notes      = document.getElementById('notes').value;
  var alertEl    = document.getElementById('form-alert');
  var btn        = document.getElementById('submit-btn');

  // Validation
  if (!fid) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please select a facility.</div>';
    alertEl.style.display = 'block';
    return;
  }
  if (!startVal || !endVal) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please select start and end date and time.</div>';
    alertEl.style.display = 'block';
    return;
  }
  if (!purpose) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please enter the purpose of the booking.</div>';
    alertEl.style.display = 'block';
    return;
  }
  if (!attendance || parseInt(attendance) < 1) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please enter expected attendance.</div>';
    alertEl.style.display = 'block';
    return;
  }

  var startISO = new Date(startVal).toISOString();
  var endISO   = new Date(endVal).toISOString();

  if (new Date(endISO) <= new Date(startISO)) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>End time must be after start time.</div>';
    alertEl.style.display = 'block';
    return;
  }

  var payload = {
    facility:            parseInt(fid),
    start_time:          startISO,
    end_time:            endISO,
    purpose:             purpose,
    expected_attendance: parseInt(attendance),
    notes:               notes,
    is_priority:         false,
    priority_reason:     ''
  };

  if (selectedZoneId) payload.zone = selectedZoneId;

  var priorityCheck = document.getElementById('is-priority');
  if (priorityCheck && priorityCheck.checked) {
    payload.is_priority     = true;
    payload.priority_reason = document.getElementById('priority-reason').value;
  }

  // Lock button
  isSubmitting      = true;
  btn.disabled      = true;
  btn.innerHTML     = '<i class="bi bi-hourglass-split me-1"></i> Submitting...';
  btn.style.opacity = '0.7';
  alertEl.style.display = 'none';

  try {
    var res = await API.post('/bookings/', payload);

    if (!res) {
      throw new Error('No response from server');
    }

    var data = await res.json();

    if (res.ok) {
      window.location.href = '/bookings/confirm/?id=' + data.id;
    } else {
      var errMsg = 'Submission failed.';
      if (data.conflict) {
        errMsg = data.conflict.message || errMsg;
      } else if (data.detail) {
        errMsg = data.detail;
      } else if (typeof data === 'object') {
        var keys = Object.keys(data);
        if (keys.length > 0) errMsg = JSON.stringify(data[keys[0]]);
      }
      alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>' + errMsg + '</div>';
      alertEl.style.display = 'block';
      isSubmitting      = false;
      btn.disabled      = false;
      btn.innerHTML     = '<i class="bi bi-send me-1"></i> Submit Request';
      btn.style.opacity = '1';
    }
  } catch(err) {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Network error. Please check your connection and try again.</div>';
    alertEl.style.display = 'block';
    isSubmitting      = false;
    btn.disabled      = false;
    btn.innerHTML     = '<i class="bi bi-send me-1"></i> Submit Request';
    btn.style.opacity = '1';
  }
}
</script>
{% endblock %}
"""

os.makedirs('templates/bookings', exist_ok=True)
with open('templates/bookings/new.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Booking form written successfully')
