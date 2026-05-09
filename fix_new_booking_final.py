content = """\
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
        <div id="facility-info" style="display:none;margin-top:8px;padding:10px 12px;background:rgba(46,117,182,0.08);border:1px solid rgba(46,117,182,0.2);border-radius:8px;font-size:0.82rem;color:var(--text-muted);"></div>
      </div>

      <div id="zone-section" style="display:none;">
        <label class="cg-label">Zone <span style="color:var(--text-muted);font-size:0.75rem;">(optional)</span></label>
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
        <input type="text" class="cg-input" id="priority-reason"
               placeholder="Reason e.g. Graduation Ceremony" style="display:none;"/>
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
var selectedZoneId = null;
var params = new URLSearchParams(window.location.search);

// Pre-select facility from URL param — works immediately since options
// are rendered server-side by Django, no async needed
var preSelected = params.get('facility');
if (preSelected) {
  var sel = document.getElementById('facility-select');
  sel.value = preSelected;
  if (sel.value === preSelected) {
    onFacilityChange();
  }
}

// Pre-fill date/time from calendar click
if (params.get('date') && params.get('hour')) {
  var date = params.get('date');
  var hour = params.get('hour').padStart(2,'0');
  var endH = String(parseInt(hour) + 2).padStart(2,'0');
  document.getElementById('start-time').value = date + 'T' + hour + ':00';
  document.getElementById('end-time').value   = date + 'T' + endH + ':00';
}

var priorityCheck = document.getElementById('is-priority');
if (priorityCheck) {
  priorityCheck.addEventListener('change', function() {
    document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
  });
}

function onFacilityChange() {
  var sel      = document.getElementById('facility-select');
  var option   = sel.options[sel.selectedIndex];
  var infoBox  = document.getElementById('facility-info');
  var zoneSection = document.getElementById('zone-section');
  var zoneOptions = document.getElementById('zone-options');
  selectedZoneId  = null;
  document.getElementById('zone-id').value = '';

  if (!sel.value) {
    infoBox.style.display     = 'none';
    zoneSection.style.display = 'none';
    return;
  }

  var location = option.getAttribute('data-location');
  var capacity = option.getAttribute('data-capacity');
  var zones    = JSON.parse(option.getAttribute('data-zones') || '[]');
  var blocks   = JSON.parse(option.getAttribute('data-blocks') || '[]');

  var infoHtml = '<i class="bi bi-geo-alt me-1"></i>' + location;
  infoHtml += ' &nbsp;&middot;&nbsp; <i class="bi bi-people me-1"></i>' + capacity + ' capacity';
  if (blocks.length) {
    infoHtml += '<div style="margin-top:6px;color:#F4A261;">';
    blocks.forEach(function(b) {
      infoHtml += '<i class="bi bi-lock me-1"></i>' + b.label + ' every ' + b.day_name + ' ' + b.start_time + '\u2013' + b.end_time + '<br/>';
    });
    infoHtml += '</div>';
  }
  infoBox.innerHTML     = infoHtml;
  infoBox.style.display = 'block';

  if (zones.length) {
    var zonesHtml = '<button type="button" onclick="selectZone(null, this)" class="zone-btn" style="background:rgba(46,117,182,0.15);border:1px solid var(--accent);border-radius:8px;padding:6px 14px;font-size:0.8rem;color:var(--accent);cursor:pointer;font-weight:500;">Entire facility</button>';
    zones.forEach(function(z) {
      zonesHtml += '<button type="button" onclick="selectZone(' + z.id + ', this)" class="zone-btn" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:8px;padding:6px 14px;font-size:0.8rem;color:var(--text-muted);cursor:pointer;">';
      zonesHtml += z.name + ' <span style="font-size:0.72rem;">(cap: ' + z.capacity + ')</span></button>';
    });
    zoneOptions.innerHTML     = zonesHtml;
    zoneSection.style.display = 'block';
  } else {
    zoneSection.style.display = 'none';
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
  btn.style.background  = 'rgba(46,117,182,0.15)';
  btn.style.borderColor = 'var(--accent)';
  btn.style.color       = 'var(--accent)';
  btn.style.fontWeight  = '500';
  checkConflict();
}

var conflictTimer;
function checkConflict() {
  clearTimeout(conflictTimer);
  conflictTimer = setTimeout(_doConflictCheck, 600);
}

async function _doConflictCheck() {
  var facilityId = document.getElementById('facility-select').value;
  var startTime  = document.getElementById('start-time').value;
  var endTime    = document.getElementById('end-time').value;
  if (!facilityId || !startTime || !endTime) return;
  var payload = {
    facility_id: parseInt(facilityId),
    start_time:  new Date(startTime).toISOString(),
    end_time:    new Date(endTime).toISOString(),
  };
  if (selectedZoneId) payload.zone_id = selectedZoneId;
  var res   = await API.post('/bookings/check-conflict/', payload);
  var alertEl = document.getElementById('conflict-alert');
  var btn   = document.getElementById('submit-btn');
  if (res && res.ok) {
    var data = await res.json();
    if (!data.available) {
      var html = '<div class="cg-alert cg-alert-warning"><strong><i class="bi bi-exclamation-triangle me-2"></i>' + data.message + '</strong>';
      if (data.reason === 'recurring_block') {
        html += '<div style="margin-top:8px;font-size:0.82rem;">Blocked by: <strong>' + data.blocked_by + '</strong> every ' + data.day + ' ' + data.time + '</div>';
        btn.disabled = true; btn.style.opacity = '0.5';
      } else if (data.alternative_slots) {
        html += '<div style="margin-top:10px;font-size:0.82rem;"><strong>Available alternatives:</strong><div style="margin-top:8px;display:grid;gap:6px;">';
        data.alternative_slots.forEach(function(slot) {
          var s = new Date(slot.start_time).toLocaleString('en-KE', {weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
          var e = new Date(slot.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
          html += '<button type="button" onclick="useSlot(\'' + slot.start_time + '\',\'' + slot.end_time + '\')" style="background:rgba(46,117,182,0.1);border:1px solid var(--accent);border-radius:6px;color:var(--accent);padding:6px 12px;font-size:0.8rem;cursor:pointer;text-align:left;"><i class="bi bi-clock me-1"></i>' + s + ' \u2014 ' + e + '</button>';
        });
        html += '</div></div>';
        btn.disabled = true; btn.style.opacity = '0.5';
      }
      html += '</div>';
      alertEl.innerHTML = html; alertEl.style.display = 'block';
    } else {
      alertEl.innerHTML = '<div class="cg-alert cg-alert-success"><i class="bi bi-check-circle me-2"></i>' + data.message + '</div>';
      alertEl.style.display = 'block';
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
  var facilityId = document.getElementById('facility-select').value;
  var startTime  = document.getElementById('start-time').value;
  var endTime    = document.getElementById('end-time').value;
  var purpose    = document.getElementById('purpose').value;
  var attendance = document.getElementById('attendance').value;
  if (!facilityId || !startTime || !endTime || !purpose || !attendance) {
    document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please fill in all required fields.</div>';
    document.getElementById('form-alert').style.display = 'block';
    return;
  }
  var payload = {
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
  var pc = document.getElementById('is-priority');
  if (pc && pc.checked) {
    payload.is_priority     = true;
    payload.priority_reason = document.getElementById('priority-reason').value;
  }
  var btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.textContent = 'Submitting...';
  var res = await API.post('/bookings/', payload);
  if (res) {
    var data = await res.json();
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
</script>
{% endblock %}
"""

with open('templates/bookings/new.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('New booking template written successfully')
