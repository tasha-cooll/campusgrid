content = """\
{% extends 'base.html' %}
{% block title %}Calendar{% endblock %}
{% block page_title %}Weekly Calendar{% endblock %}

{% block extra_styles %}
.week-grid {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-secondary);
}
.grid-header {
  background: var(--bg-sidebar);
  padding: 12px 8px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
  font-weight: 600;
}
.grid-header.today-col { color: var(--accent); background: rgba(46,117,182,0.1); }
.time-cell {
  padding: 0 8px;
  height: 60px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: flex-start;
  padding-top: 6px;
  font-size: 0.72rem;
  color: var(--text-muted);
  border-right: 1px solid var(--border);
  background: var(--bg-sidebar);
}
.day-cell {
  height: 60px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  position: relative;
  cursor: pointer;
  transition: background 0.1s;
}
.day-cell:hover { background: rgba(46,117,182,0.05); }
.day-cell.today-col { background: rgba(46,117,182,0.04); }
.event-block {
  position: absolute;
  left: 2px; right: 2px;
  border-radius: 6px;
  padding: 3px 6px;
  font-size: 0.7rem;
  font-weight: 500;
  overflow: hidden;
  cursor: pointer;
  z-index: 10;
  white-space: nowrap;
  text-overflow: ellipsis;
  border-left: 3px solid;
}
.week-nav { display: flex; align-items: center; gap: 12px; }
.week-nav button {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  padding: 6px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: border-color 0.15s;
}
.week-nav button:hover { border-color: var(--accent); }
.facility-filter {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  padding: 6px 12px;
  font-size: 0.85rem;
}
#event-modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  align-items: center;
  justify-content: center;
}
#event-modal-overlay.show { display: flex; }
.event-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  width: 100%;
  max-width: 440px;
  position: relative;
}
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div class="week-nav">
    <button onclick="changeWeek(-1)"><i class="bi bi-chevron-left"></i></button>
    <span id="week-label" style="font-size:0.9rem;font-weight:600;min-width:220px;text-align:center;"></span>
    <button onclick="changeWeek(1)"><i class="bi bi-chevron-right"></i></button>
    <button onclick="goToToday()" style="font-size:0.75rem;">Today</button>
  </div>
  <div class="d-flex gap-2 align-items-center">
    <select class="facility-filter" id="facility-select" onchange="loadEvents()">
      <option value="">All Facilities</option>
    </select>
    <a href="/bookings/new/" class="btn-cg-primary">
      <i class="bi bi-plus-lg me-1"></i> New Booking
    </a>
  </div>
</div>

<div class="d-flex gap-3 mb-3" style="font-size:0.75rem;">
  <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#2E75B6;margin-right:4px;"></span>Approved</span>
  <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#F4A261;margin-right:4px;"></span>Pending</span>
  <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#FF6B35;margin-right:4px;"></span>Displaced</span>
  <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#8B0000;margin-right:4px;"></span>Priority</span>
</div>

<div class="week-grid" id="calendar-grid"></div>

<div id="event-modal-overlay">
  <div class="event-modal">
    <button onclick="closeModal()" style="position:absolute;top:16px;right:16px;background:none;border:none;color:var(--text-muted);font-size:1.2rem;cursor:pointer;">
      <i class="bi bi-x-lg"></i>
    </button>
    <div id="modal-content"></div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
const HOURS = Array.from({length: 14}, (_, i) => i + 7);
const DAYS  = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
const TZ    = 'Africa/Nairobi';
let currentWeekStart = getWeekStart(new Date());
let allEvents = [];

function getWeekStart(date) {
  const d = new Date(date);
  d.setDate(d.getDate() - d.getDay());
  d.setHours(0,0,0,0);
  return d;
}

function changeWeek(dir) {
  currentWeekStart.setDate(currentWeekStart.getDate() + dir * 7);
  loadEvents();
}

function goToToday() {
  currentWeekStart = getWeekStart(new Date());
  loadEvents();
}

function formatDate(date) {
  return date.toLocaleDateString('en-KE', {month:'short', day:'numeric', timeZone: TZ});
}

function getLocalDateStr(date) {
  return date.toLocaleDateString('en-KE', {timeZone: TZ, year:'numeric', month:'2-digit', day:'2-digit'});
}

function getLocalHour(date) {
  const str = date.toLocaleTimeString('en-KE', {timeZone: TZ, hour: '2-digit', hour12: false});
  return parseInt(str.split(':')[0]);
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
  }
}

async function loadEvents() {
  const month      = currentWeekStart.getMonth() + 1;
  const year       = currentWeekStart.getFullYear();
  const facilityId = document.getElementById('facility-select').value;
  let url = '/reports/calendar/?month=' + month + '&year=' + year;
  if (facilityId) url += '&facility_id=' + facilityId;
  try {
    const res = await API.get(url);
    if (res && res.ok) {
      const data = await res.json();
      allEvents  = data.events || [];
      renderGrid();
    }
  } catch(e) { renderGrid(); }
}

function safeStr(str) {
  return String(str).replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
}

function renderGrid() {
  const grid      = document.getElementById('calendar-grid');
  const today     = new Date();
  const weekDates = Array.from({length:7}, function(_, i) {
    const d = new Date(currentWeekStart);
    d.setDate(d.getDate() + i);
    return d;
  });

  document.getElementById('week-label').textContent =
    formatDate(weekDates[0]) + ' \u2014 ' + formatDate(weekDates[6]) + ', ' + weekDates[0].getFullYear();

  let html = '<div class="grid-header" style="border-right:1px solid var(--border);"></div>';

  weekDates.forEach(function(d) {
    const isToday = getLocalDateStr(d) === getLocalDateStr(today);
    html += '<div class="grid-header' + (isToday ? ' today-col' : '') + '" style="border-right:1px solid var(--border);">';
    html += '<div>' + DAYS[d.getDay()] + '</div>';
    html += '<div style="font-size:1rem;font-weight:700;">' + d.getDate() + '</div>';
    html += '</div>';
  });

  HOURS.forEach(function(hour) {
    html += '<div class="time-cell">' + hour + ':00</div>';
    weekDates.forEach(function(d) {
      const isToday    = getLocalDateStr(d) === getLocalDateStr(today);
      const dateIso    = d.toISOString().split('T')[0];
      const cellEvents = allEvents.filter(function(ev) {
        const evStart = new Date(ev.start);
        return getLocalDateStr(evStart) === getLocalDateStr(d) && getLocalHour(evStart) === hour;
      });

      let evHtml = '';
      cellEvents.forEach(function(ev) {
        const color    = ev.color || '#2E75B6';
        const safeTitle = safeStr(ev.title);
        evHtml += '<div class="event-block" ';
        evHtml += 'style="background:' + color + '22;border-left-color:' + color + ';color:' + color + ';" ';
        evHtml += 'onclick="showEventDetail(' + ev.id + ')" ';
        evHtml += 'title="' + safeTitle + '">' + safeTitle + '</div>';
      });

      html += '<div class="day-cell' + (isToday ? ' today-col' : '') + '" ';
      html += 'onclick="handleCellClick(' + "'" + dateIso + "'," + hour + ')" ';
      html += 'style="border-right:1px solid var(--border);">' + evHtml + '</div>';
    });
  });

  grid.innerHTML = html;
}

function handleCellClick(dateStr, hour) {
  window.location.href = '/bookings/new/?date=' + dateStr + '&hour=' + hour;
}

function showEventDetail(eventId) {
  const ev = allEvents.find(function(e) { return e.id === eventId; });
  if (!ev) return;
  const start    = new Date(ev.start);
  const end      = new Date(ev.end);
  const color    = ev.color || '#2E75B6';
  const priority = ev.is_priority ? '<span class="status-badge badge-priority ms-2">Priority</span>' : '';

  const startStr = start.toLocaleString('en-KE', {
    timeZone: TZ, weekday:'short', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'
  });
  const endStr = end.toLocaleTimeString('en-KE', {timeZone: TZ, hour:'2-digit', minute:'2-digit'});

  document.getElementById('modal-content').innerHTML =
    '<div style="border-left:4px solid ' + color + ';padding-left:16px;margin-bottom:20px;">' +
      '<h5 style="font-size:1rem;font-weight:700;margin-bottom:4px;">' + ev.title + '</h5>' +
      '<span class="status-badge badge-' + ev.status + '">' + ev.status + '</span>' + priority +
    '</div>' +
    '<div style="display:grid;gap:12px;font-size:0.85rem;">' +
      '<div><span style="color:var(--text-muted);">Facility</span>' +
        '<div style="font-weight:500;margin-top:2px;">' + ev.facility + '</div></div>' +
      '<div><span style="color:var(--text-muted);">Zone</span>' +
        '<div style="font-weight:500;margin-top:2px;">' + ev.zone + '</div></div>' +
      '<div><span style="color:var(--text-muted);">Time</span>' +
        '<div style="font-weight:500;margin-top:2px;">' + startStr + ' \u2014 ' + endStr + '</div></div>' +
    '</div>';

  document.getElementById('event-modal-overlay').classList.add('show');
}

function closeModal() {
  document.getElementById('event-modal-overlay').classList.remove('show');
}

document.getElementById('event-modal-overlay').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

loadFacilities();
loadEvents();
</script>
{% endblock %}
"""

with open('templates/calendar/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print('Calendar template written successfully')
