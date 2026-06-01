import os

content = """\
{% extends 'base.html' %}
{% block title %}New Booking{% endblock %}
{% block page_title %}New Booking Request{% endblock %}

{% block content %}
<div style="max-width:640px;">
  <div class="cg-card">
    <h5 style="font-family:'EB Garamond',serif;font-size:1.2rem;font-weight:600;margin-bottom:4px;">Submit a Booking Request</h5>
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
        <input type="text" class="cg-input" id="purpose" placeholder="e.g. Basketball practice"/>
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
        <input type="text" class="cg-input" id="priority-reason" placeholder="Reason e.g. Graduation Ceremony" style="display:none;"/>
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
var urlParams = new URLSearchParams(window.location.search);

var priorityCheck = document.getElementById('is-priority');
if (priorityCheck) {
  priorityCheck.addEventListener('change', function() {
    document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
  });
}

var preSelected = urlParams.get('facility');
if (preSelected) {
  var sel = document.getElementById('facility-select');
  sel.value = preSelected;
  if (sel.value === preSelected) {
    onFacilityChange();
  }
}

if (urlParams.get('date') && urlParams.get('hour')) {
  var dt   = urlParams.get('date');
  var hr   = urlParams.get('hour').padStart(2, '0');
  var endH = String(parseInt(hr) + 2).padStart(2, '0');
  document.getElementById('start-time').value = dt + 'T' + hr + ':00';
  document.getElementById('end-time').value   = dt + 'T' + endH + ':00';
}

function onFacilityChange() {
  var sel      = document.getElementById('facility-select');
  var opt      = sel.options[sel.selectedIndex];
  var infoBox  = document.getElementById('facility-info');
  var zonesSec = document.getElementById('zone-section');
  var zoneOpts = document.getElementById('zone-options');
  selectedZoneId = null;
  document.getElementById('zone-id').value = '';

  if (!sel.value) {
    infoBox.style.display  = 'none';
    zonesSec.style.display = 'none';
    return;
  }

  var loc    = opt.getAttribute('data-location');
  var cap    = opt.getAttribute('data-capacity');
  var zones  = JSON.parse(opt.getAttribute('data-zones')  || '[]');
  var blocks = JSON.parse(opt.getAttribute('data-blocks') || '[]');

  var info = '<i class="bi bi-geo-alt me-1"></i>' + loc + ' &nbsp;&middot;&nbsp; <i class="bi bi-people me-1"></i>' + cap + ' capacity';
  if (blocks.length) {
    info += '<div style="margin-top:6px;color:var(--accent-amber);">';
    for (var i = 0; i < blocks.length; i++) {
      info += '<i class="bi bi-lock me-1"></i>' + blocks[i].label + ' every ' + blocks[i].day_name + ' ' + blocks[i].start_time + '\u2013' + blocks[i].end_time + '<br/>';
    }
    info += '</div>';
  }
  infoBox.innerHTML     = info;
  infoBox.style.display = 'block';

  if (zones.length) {
    var zh = '<button type="button" onclick="selectZone(null,this)" class="zone-btn" style="background:rgba(201,168,76,0.15);border:1px solid var(--accent);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--accent);cursor:pointer;font-weight:600;">Entire facility</button>';
    for (var j = 0; j < zones.length; j++) {
      zh += '<button type="button" onclick="selectZone(' + zones[j].id + ',this)" class="zone-btn" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--text-muted);cursor:pointer;">' + zones[j].name + ' <span style="font-size:0.72rem;">(cap: ' + zones[j].capacity + ')</span></button>';
    }
    zoneOpts.innerHTML     = zh;
    zonesSec.style.display = 'block';
  } else {
    zonesSec.style.display = 'none';
  }
  checkConflict();
}

function selectZone(zoneId, btn) {
  selectedZoneId = zoneId;
  document.getElementById('zone-id').value = zoneId || '';
  var btns = document.querySelectorAll('.zone-btn');
  for (var i = 0; i < btns.length; i++) {
    btns[i].style.background  = 'var(--bg-primary)';
    btns[i].style.borderColor = 'var(--border)';
    btns[i].style.color       = 'var(--text-muted)';
    btns[i].style.fontWeight  = 'normal';
  }
  btn.style.background  = 'rgba(201,168,76,0.15)';
  btn.style.borderColor = 'var(--accent)';
  btn.style.color       = 'var(--accent)';
  btn.style.fontWeight  = '600';
  checkConflict();
}

var conflictTimer;
function checkConflict() {
  clearTimeout(conflictTimer);
  conflictTimer = setTimeout(doConflictCheck, 600);
}

async function doConflictCheck() {
  var facilityId = document.getElementById('facility-select').value;
  var startTime  = document.getElementById('start-time').value;
  var endTime    = document.getElementById('end-time').value;
  if (!facilityId || !startTime || !endTime) return;

  var payload = {
    facility_id: parseInt(facilityId),
    start_time:  new Date(startTime).toISOString(),
    end_time:    new Date(endTime).toISOString()
  };
  if (selectedZoneId) payload.zone_id = selectedZoneId;

  var res     = await API.post('/bookings/check-conflict/', payload);
  var alertEl = document.getElementById('conflict-alert');
  var btn     = document.getElementById('submit-btn');
  if (!res || !res.ok) return;

  var data = await res.json();
  if (!data.available) {
    var html = '<div class="cg-alert cg-alert-warning"><strong><i class="bi bi-exclamation-triangle me-2"></i>' + data.message + '</strong>';
    if (data.reason === 'recurring_block') {
      html += '<div style="margin-top:8px;font-size:0.82rem;">Blocked by: <strong>' + data.blocked_by + '</strong> every ' + data.day + ' ' + data.time + '</div>';
      btn.disabled = true;
      btn.style.opacity = '0.5';
    } else if (data.alternative_slots && data.alternative_slots.length) {
      html += '<div style="margin-top:10px;font-size:0.82rem;"><strong>Available alternatives:</strong><div style="margin-top:8px;display:grid;gap:6px;">';
      for (var k = 0; k < data.alternative_slots.length; k++) {
        var s = new Date(data.alternative_slots[k].start_time).toLocaleString('en-KE', {weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
        var e = new Date(data.alternative_slots[k].end_time).toLocaleTimeString('en-KE', {hour:'2-digit',minute:'2-digit'});
        html += '<button type="button" onclick="useSlot(' + JSON.stringify(data.alternative_slots[k].start_time) + ',' + JSON.stringify(data.alternative_slots[k].end_time) + ')" style="background:rgba(201,168,76,0.08);border:1px solid var(--accent);border-radius:4px;color:var(--accent);padding:6px 12px;font-size:0.8rem;cursor:pointer;text-align:left;"><i class="bi bi-clock me-1"></i>' + s + ' \u2014 ' + e + '</button>';
      }
      html += '</div></div>';
      btn.disabled = true;
      btn.style.opacity = '0.5';
    }
    html += '</div>';
    alertEl.innerHTML     = html;
    alertEl.style.display = 'block';
  } else {
    alertEl.innerHTML     = '<div class="cg-alert cg-alert-success"><i class="bi bi-check-circle me-2"></i>' + data.message + '</div>';
    alertEl.style.display = 'block';
    btn.disabled          = false;
    btn.style.opacity     = '1';
  }
}

function useSlot(start, end) {
  document.getElementById('start-time').value   = new Date(start).toISOString().slice(0, 16);
  document.getElementById('end-time').value     = new Date(end).toISOString().slice(0, 16);
  document.getElementById('conflict-alert').style.display = 'none';
  document.getElementById('submit-btn').disabled    = false;
  document.getElementById('submit-btn').style.opacity = '1';
}

async function submitBooking() {
  var facilityId = document.getElementById('facility-select').value;
  var startTime  = document.getElementById('start-time').value;
  var endTime    = document.getElementById('end-time').value;
  var purpose    = document.getElementById('purpose').value;
  var attendance = document.getElementById('attendance').value;

  if (!facilityId || !startTime || !endTime || !purpose || !attendance) {
    document.getElementById('form-alert').innerHTML     = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please fill in all required fields.</div>';
    document.getElementById('form-alert').style.display = 'block';
    return;
  }

  var payload = {
    facility:            parseInt(facilityId),
    start_time:          new Date(startTime).toISOString(),
    end_time:            new Date(endTime).toISOString(),
    purpose:             purpose,
    expected_attendance: parseInt(attendance),
    notes:               document.getElementById('notes').value,
    is_priority:         false,
    priority_reason:     ''
  };

  if (selectedZoneId) payload.zone = selectedZoneId;

  var pc = document.getElementById('is-priority');
  if (pc && pc.checked) {
    payload.is_priority     = true;
    payload.priority_reason = document.getElementById('priority-reason').value;
  }

  var btn       = document.getElementById('submit-btn');
  btn.disabled  = true;
  btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Submitting...';

  var res = await API.post('/bookings/', payload);
  if (res) {
    var data = await res.json();
    if (res.ok) {
      window.location.href = '/bookings/confirm/?id=' + data.id;
    } else {
      btn.disabled  = false;
      btn.innerHTML = '<i class="bi bi-send me-1"></i> Submit Request';
      var errMsg = data.detail || JSON.stringify(data);
      document.getElementById('form-alert').innerHTML     = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>' + errMsg + '</div>';
      document.getElementById('form-alert').style.display = 'block';
    }
  }
}
</script>
{% endblock %}
"""

with open('templates/bookings/new.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Booking form written successfully')
