
var selectedZoneId = null;
var urlParams      = new URLSearchParams(window.location.search);

document.addEventListener('DOMContentLoaded', function() {
  var pc = document.getElementById('is-priority');
  if (pc) {
    pc.addEventListener('change', function() {
      document.getElementById('priority-reason').style.display = this.checked ? 'block' : 'none';
    });
  }

  var preSelected = urlParams.get('facility');
  if (preSelected) {
    var sel = document.getElementById('facility-select');
    if (sel) { sel.value = preSelected; if (sel.value === preSelected) onFacilityChange(); }
  }

  if (urlParams.get('date') && urlParams.get('hour')) {
    var dt   = urlParams.get('date');
    var hr   = urlParams.get('hour').padStart(2,'0');
    var endH = String(parseInt(hr)+2).padStart(2,'0');
    document.getElementById('start-time').value = dt + 'T' + hr + ':00';
    document.getElementById('end-time').value   = dt + 'T' + endH + ':00';
  }
});

function onFacilityChange() {
  var sel     = document.getElementById('facility-select');
  var opt     = sel.options[sel.selectedIndex];
  var infoBox = document.getElementById('facility-info');
  var zSec    = document.getElementById('zone-section');
  var zOpts   = document.getElementById('zone-options');
  selectedZoneId = null;
  document.getElementById('zone-id').value = '';
  if (!sel.value) { infoBox.style.display='none'; zSec.style.display='none'; return; }
  var loc    = opt.getAttribute('data-location');
  var cap    = opt.getAttribute('data-capacity');
  var zones  = JSON.parse(opt.getAttribute('data-zones')  || '[]');
  var blocks = JSON.parse(opt.getAttribute('data-blocks') || '[]');
  var info   = '<i class="bi bi-geo-alt me-1"></i>' + loc + ' &nbsp;&middot;&nbsp; <i class="bi bi-people me-1"></i>' + cap + ' capacity';
  if (blocks.length) {
    info += '<div style="margin-top:6px;color:var(--accent-amber);">';
    blocks.forEach(function(b) { info += '<i class="bi bi-lock me-1"></i>' + b.label + ' every ' + b.day_name + ' ' + b.start_time + '-' + b.end_time + '<br/>'; });
    info += '</div>';
  }
  infoBox.innerHTML = info; infoBox.style.display = 'block';
  if (zones.length) {
    var zh = '<button type="button" onclick="selectZone(null,this)" class="zone-btn" style="background:rgba(201,168,76,0.15);border:1px solid var(--accent);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--accent);cursor:pointer;font-weight:600;">Entire facility</button>';
    zones.forEach(function(z) { zh += '<button type="button" onclick="selectZone('+z.id+',this)" class="zone-btn" style="background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;padding:6px 14px;font-size:0.8rem;color:var(--text-muted);cursor:pointer;">'+z.name+' <span style="font-size:0.72rem;">(cap: '+z.capacity+')</span></button>'; });
    zOpts.innerHTML = zh; zSec.style.display = 'block';
  } else { zSec.style.display = 'none'; }
  checkConflict();
}

function selectZone(zoneId, btn) {
  selectedZoneId = zoneId;
  document.getElementById('zone-id').value = zoneId || '';
  document.querySelectorAll('.zone-btn').forEach(function(b) { b.style.background='var(--bg-primary)'; b.style.borderColor='var(--border)'; b.style.color='var(--text-muted)'; b.style.fontWeight='normal'; });
  btn.style.background='rgba(201,168,76,0.15)'; btn.style.borderColor='var(--accent)'; btn.style.color='var(--accent)'; btn.style.fontWeight='600';
  checkConflict();
}

var conflictTimer;
function checkConflict() { clearTimeout(conflictTimer); conflictTimer = setTimeout(doConflictCheck, 600); }

async function doConflictCheck() {
  var fid  = document.getElementById('facility-select').value;
  var st   = document.getElementById('start-time').value;
  var et   = document.getElementById('end-time').value;
  if (!fid || !st || !et) return;
  var payload = { facility_id: parseInt(fid), start_time: new Date(st).toISOString(), end_time: new Date(et).toISOString() };
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
      btn.disabled = true; btn.style.opacity = '0.5';
    } else if (data.alternative_slots && data.alternative_slots.length) {
      html += '<div style="margin-top:10px;font-size:0.82rem;"><strong>Available alternatives:</strong><div style="margin-top:8px;display:grid;gap:6px;">';
      data.alternative_slots.forEach(function(slot) {
        var s = new Date(slot.start_time).toLocaleString('en-KE',{weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
        var e = new Date(slot.end_time).toLocaleTimeString('en-KE',{hour:'2-digit',minute:'2-digit'});
        html += '<button type="button" onclick="useSlot(' + JSON.stringify(slot.start_time) + ',' + JSON.stringify(slot.end_time) + ')" style="background:rgba(201,168,76,0.08);border:1px solid var(--accent);border-radius:4px;color:var(--accent);padding:6px 12px;font-size:0.8rem;cursor:pointer;text-align:left;"><i class="bi bi-clock me-1"></i>' + s + ' - ' + e + '</button>';
      });
      html += '</div></div>'; btn.disabled = true; btn.style.opacity = '0.5';
    }
    html += '</div>'; alertEl.innerHTML = html; alertEl.style.display = 'block';
  } else {
    alertEl.innerHTML = '<div class="cg-alert cg-alert-success"><i class="bi bi-check-circle me-2"></i>' + data.message + '</div>';
    alertEl.style.display = 'block'; btn.disabled = false; btn.style.opacity = '1';
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
  var fid  = document.getElementById('facility-select').value;
  var st   = document.getElementById('start-time').value;
  var et   = document.getElementById('end-time').value;
  var pur  = document.getElementById('purpose').value;
  var att  = document.getElementById('attendance').value;
  if (!fid || !st || !et || !pur || !att) {
    document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>Please fill in all required fields.</div>';
    document.getElementById('form-alert').style.display = 'block';
    return;
  }
  var payload = { facility: parseInt(fid), start_time: new Date(st).toISOString(), end_time: new Date(et).toISOString(), purpose: pur, expected_attendance: parseInt(att), notes: document.getElementById('notes').value, is_priority: false, priority_reason: '' };
  if (selectedZoneId) payload.zone = selectedZoneId;
  var pc = document.getElementById('is-priority');
  if (pc && pc.checked) { payload.is_priority = true; payload.priority_reason = document.getElementById('priority-reason').value; }
  var btn      = document.getElementById('submit-btn');
  btn.disabled = true;
  btn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Submitting...';
  var res = await API.post('/bookings/', payload);
  if (res) {
    var data = await res.json();
    if (res.ok) {
      btn.innerHTML        = '<i class="bi bi-check-circle me-1"></i> Submitted';
      btn.style.background = '#2A6B4A';
      btn.style.color      = '#F0F4FF';
      btn.style.opacity    = '1';
      setTimeout(function() { window.location.href = '/bookings/confirm/?id=' + data.id; }, 1500);
    } else {
      btn.disabled  = false;
      btn.innerHTML = '<i class="bi bi-send me-1"></i> Submit Request';
      document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>' + (data.detail || JSON.stringify(data)) + '</div>';
      document.getElementById('form-alert').style.display = 'block';
    }
  }
}
