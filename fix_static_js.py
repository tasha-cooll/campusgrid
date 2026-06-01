import os


def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Written: ' + path)


# ── campusgrid.js — shared across all pages ──────────────────────
w('ui/static/js/campusgrid.js', """
var API = {
  baseURL: '/api',
  getToken: function() { return localStorage.getItem('cg_access_token'); },
  clearTokens: function() {
    localStorage.removeItem('cg_access_token');
    localStorage.removeItem('cg_refresh_token');
  },
  request: async function(method, endpoint, data) {
    var headers = { 'Content-Type': 'application/json' };
    var token = this.getToken();
    if (token) headers['Authorization'] = 'Bearer ' + token;
    var config = { method: method, headers: headers };
    if (data) config.body = JSON.stringify(data);
    var res = await fetch(this.baseURL + endpoint, config);
    if (res.status === 401) {
      var refreshed = await this.refreshToken();
      if (refreshed) return this.request(method, endpoint, data);
      this.clearTokens();
      if (!window._redirecting) {
        window._redirecting = true;
        window.location.href = '/';
      }
      return null;
    }
    return res;
  },
  refreshToken: async function() {
    var refresh = localStorage.getItem('cg_refresh_token');
    if (!refresh) return false;
    var res = await fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refresh })
    });
    if (res.ok) {
      var data = await res.json();
      localStorage.setItem('cg_access_token', data.access);
      return true;
    }
    return false;
  },
  get:    function(ep)      { return this.request('GET',    ep, null); },
  post:   function(ep, d)   { return this.request('POST',   ep, d); },
  patch:  function(ep, d)   { return this.request('PATCH',  ep, d); },
  delete: function(ep)      { return this.request('DELETE', ep, null); }
};

function showToast(message, type) {
  var existing = document.getElementById('cg-toast');
  if (existing) existing.remove();
  var color = type === 'error' ? '#7B2828' : '#C9A84C';
  var icon  = type === 'error' ? 'bi-exclamation-circle-fill' : 'bi-check-circle-fill';
  var toast = document.createElement('div');
  toast.id  = 'cg-toast';
  toast.style.cssText = 'position:fixed;bottom:28px;right:28px;background:#0F1A30;border:1px solid ' + color + ';border-left:4px solid ' + color + ';color:#F0F4FF;padding:14px 20px;border-radius:6px;font-size:0.875rem;font-family:Inter,sans-serif;z-index:9999;max-width:360px;box-shadow:0 8px 32px rgba(0,0,0,0.4);display:flex;align-items:center;gap:12px;opacity:0;transform:translateY(12px);transition:all 0.3s ease';
  toast.innerHTML = '<i class="bi ' + icon + '" style="color:' + color + ';font-size:1.1rem;flex-shrink:0;"></i><span>' + message + '</span>';
  document.body.appendChild(toast);
  setTimeout(function() { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 10);
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
  }, 3500);
}

async function loadNotifCount() {
  try {
    var res = await API.get('/notifications/unread-count/');
    if (res && res.ok) {
      var data = await res.json();
      var badge = document.getElementById('notif-badge');
      if (badge) {
        badge.textContent   = data.unread_count > 0 ? data.unread_count : '';
        badge.style.display = data.unread_count > 0 ? 'flex' : 'none';
      }
      var pb = document.getElementById('pending-count-badge');
      if (pb) {
        var ar = await API.get('/approvals/pending/');
        if (ar && ar.ok) {
          var ad = await ar.json();
          pb.textContent   = ad.count > 0 ? ad.count : '';
          pb.style.display = ad.count > 0 ? 'inline' : 'none';
        }
      }
    }
  } catch(e) {}
}

document.addEventListener('DOMContentLoaded', function() {
  if (document.querySelector('.sidebar')) {
    loadNotifCount();
    setInterval(loadNotifCount, 60000);
  }
});
""")

# ── reports.js ───────────────────────────────────────────────────
w('ui/static/js/reports.js', """
var reportData   = null;
var conflictData = null;
var barChart     = null;
var donutChart   = null;
var MONTHS = ['','January','February','March','April','May','June','July','August','September','October','November','December'];
var GOLD   = '#C9A84C';
var GREEN  = '#4A7C59';
var RED    = '#7B2828';
var AMBER  = '#B8860B';
var ORANGE = '#8B4513';

async function loadReports() {
  var month     = document.getElementById('month-select').value;
  var year      = document.getElementById('year-select').value;
  var container = document.getElementById('reports-content');
  var pp        = document.getElementById('print-period');
  if (pp) pp.textContent = 'Period: ' + MONTHS[parseInt(month)] + ' ' + year;

  container.innerHTML = '<div style="display:grid;gap:12px;"><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;"><div class="skeleton" style="height:80px;border-radius:6px;"></div><div class="skeleton" style="height:80px;border-radius:6px;"></div><div class="skeleton" style="height:80px;border-radius:6px;"></div><div class="skeleton" style="height:80px;border-radius:6px;"></div></div><div class="skeleton" style="height:280px;border-radius:6px;"></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;"><div class="skeleton" style="height:260px;border-radius:6px;"></div><div class="skeleton" style="height:260px;border-radius:6px;"></div></div><div class="skeleton" style="height:200px;border-radius:6px;"></div></div>';

  var utilRes     = await API.get('/reports/utilization/?month=' + month + '&year=' + year);
  var conflictRes = await API.get('/reports/conflicts/?month='   + month + '&year=' + year);

  if (!utilRes || !utilRes.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load report data. Status: ' + (utilRes ? utilRes.status : 'no response') + '</div>';
    return;
  }

  reportData   = await utilRes.json();
  conflictData = (conflictRes && conflictRes.ok) ? await conflictRes.json() : null;
  var facs     = reportData.facilities || [];

  if (!facs.length) {
    container.innerHTML = '<div class="cg-alert cg-alert-info">No booking data found for ' + MONTHS[parseInt(month)] + ' ' + year + '. Add some bookings first.</div>';
    return;
  }

  var totB = 0, totA = 0, totP = 0, totR = 0, totH = 0, totC = 0, totD = 0;
  facs.forEach(function(f) { totB += f.total_bookings; totA += f.approved; totP += f.pending; totR += f.rejected; totD += f.displaced; totH += parseFloat(f.total_hours_booked); totC += f.conflicts; });

  var html = '<div style="display:grid;gap:20px;">';
  html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;">';
  html += sbox('Total Bookings', totB, 'bi-journal-bookmark', 'rgba(201,168,76,0.15)', GOLD);
  html += sbox('Approved', totA, 'bi-check-circle', 'rgba(74,124,89,0.15)', GREEN);
  html += sbox('Hours Booked', totH.toFixed(1) + 'h', 'bi-clock', 'rgba(30,75,143,0.15)', '#7BA7DC');
  html += sbox('Conflicts', totC, 'bi-shield-exclamation', 'rgba(184,134,11,0.15)', AMBER);
  html += '</div>';

  html += '<div class="cg-card"><div class="cg-card-title">Booking Status by Facility</div><div style="position:relative;height:260px;margin-top:12px;"><canvas id="barChart"></canvas></div></div>';

  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">';
  html += '<div class="cg-card"><div class="cg-card-title">Overall Booking Breakdown</div><div style="position:relative;height:220px;margin-top:12px;"><canvas id="donutChart"></canvas></div><div id="donut-legend" style="display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;justify-content:center;font-size:0.75rem;"></div></div>';

  html += '<div class="cg-card"><div class="cg-card-title">Conflict Summary</div>';
  if (conflictData && conflictData.total_conflicts > 0) {
    html += '<div style="margin-top:12px;text-align:center;padding:16px;background:rgba(184,134,11,0.08);border:1px solid rgba(184,134,11,0.2);border-radius:6px;margin-bottom:14px;"><div style="font-size:2.8rem;font-weight:700;color:' + GOLD + ';line-height:1;">' + conflictData.total_conflicts + '</div><div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-top:4px;">Total Conflicts</div></div><div style="display:grid;gap:8px;">';
    Object.entries(conflictData.by_facility).forEach(function(e) {
      var pct = Math.round((e[1] / conflictData.total_conflicts) * 100);
      html += '<div style="font-size:0.82rem;"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span>' + e[0] + '</span><span style="color:' + GOLD + ';font-weight:600;">' + e[1] + '</span></div><div style="height:4px;background:var(--border);border-radius:2px;"><div style="height:4px;width:' + pct + '%;background:' + GOLD + ';border-radius:2px;"></div></div></div>';
    });
    html += '</div></div>';
  } else {
    html += '<div style="text-align:center;padding:40px;color:var(--text-muted);"><i class="bi bi-shield-check" style="font-size:2.5rem;color:' + GREEN + ';"></i><p style="margin-top:12px;font-size:0.85rem;">No conflicts this period.</p></div>';
  }
  html += '</div></div>';

  html += '<div class="cg-card"><div class="cg-card-title">Detailed Utilization Table</div><div style="overflow-x:auto;margin-top:12px;"><table class="cg-table"><thead><tr><th>Facility</th><th style="text-align:center;">Total</th><th style="text-align:center;">Approved</th><th style="text-align:center;">Pending</th><th style="text-align:center;">Rejected</th><th style="text-align:center;">Displaced</th><th style="text-align:center;">Conflicts</th><th style="text-align:center;">Hours</th><th style="text-align:center;">Rate</th></tr></thead><tbody>';
  facs.forEach(function(f) {
    var rate = f.total_bookings > 0 ? Math.round((f.approved / f.total_bookings) * 100) : 0;
    var rc   = rate >= 70 ? GREEN : (rate >= 40 ? AMBER : RED);
    html += '<tr><td style="font-weight:500;">' + f.facility + '</td><td style="text-align:center;font-weight:600;">' + f.total_bookings + '</td><td style="text-align:center;color:' + GREEN + ';">' + f.approved + '</td><td style="text-align:center;color:' + GOLD + ';">' + f.pending + '</td><td style="text-align:center;color:' + RED + ';">' + f.rejected + '</td><td style="text-align:center;color:' + ORANGE + ';">' + f.displaced + '</td><td style="text-align:center;color:' + AMBER + ';">' + f.conflicts + '</td><td style="text-align:center;">' + f.total_hours_booked + 'h</td><td style="text-align:center;"><span style="color:' + rc + ';font-weight:600;">' + rate + '%</span></td></tr>';
  });
  html += '</tbody></table></div></div></div>';
  container.innerHTML = html;

  setTimeout(function() { renderBarChart(facs); renderDonutChart(totA, totP, totR, totD); }, 150);
}

function renderBarChart(facs) {
  if (barChart) { barChart.destroy(); barChart = null; }
  var ctx = document.getElementById('barChart');
  if (!ctx || !window.Chart) return;
  barChart = new window.Chart(ctx, {
    type: 'bar',
    data: {
      labels: facs.map(function(f) { return f.facility; }),
      datasets: [
        { label: 'Approved',  data: facs.map(function(f) { return f.approved;  }), backgroundColor: 'rgba(74,124,89,0.75)',  borderColor: 'rgba(74,124,89,1)',  borderWidth: 1, borderRadius: 3 },
        { label: 'Pending',   data: facs.map(function(f) { return f.pending;   }), backgroundColor: 'rgba(201,168,76,0.75)', borderColor: 'rgba(201,168,76,1)', borderWidth: 1, borderRadius: 3 },
        { label: 'Rejected',  data: facs.map(function(f) { return f.rejected;  }), backgroundColor: 'rgba(123,40,40,0.75)',  borderColor: 'rgba(123,40,40,1)',  borderWidth: 1, borderRadius: 3 },
        { label: 'Displaced', data: facs.map(function(f) { return f.displaced; }), backgroundColor: 'rgba(139,69,19,0.75)',  borderColor: 'rgba(139,69,19,1)',  borderWidth: 1, borderRadius: 3 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend:  { labels: { color: '#E8DCC8', font: { size: 11 }, boxWidth: 12 } },
        tooltip: { backgroundColor: '#111D35', titleColor: '#C9A84C', bodyColor: '#E8DCC8', borderColor: '#1E2D4A', borderWidth: 1 }
      },
      scales: {
        x: { ticks: { color: '#8A9BBF', font: { size: 11 } }, grid: { color: 'rgba(30,45,74,0.5)' } },
        y: { beginAtZero: true, ticks: { color: '#8A9BBF', font: { size: 11 }, stepSize: 1 }, grid: { color: 'rgba(30,45,74,0.5)' } }
      }
    }
  });
}

function renderDonutChart(approved, pending, rejected, displaced) {
  if (donutChart) { donutChart.destroy(); donutChart = null; }
  var ctx = document.getElementById('donutChart');
  if (!ctx || !window.Chart) return;
  var labels = ['Approved', 'Pending', 'Rejected', 'Displaced'];
  var values = [approved, pending, rejected, displaced];
  var colors = ['rgba(74,124,89,0.85)', 'rgba(201,168,76,0.85)', 'rgba(123,40,40,0.85)', 'rgba(139,69,19,0.85)'];
  donutChart = new window.Chart(ctx, {
    type: 'doughnut',
    data: { labels: labels, datasets: [{ data: values, backgroundColor: colors, borderColor: '#111D35', borderWidth: 2, hoverOffset: 6 }] },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '68%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111D35', titleColor: '#C9A84C', bodyColor: '#E8DCC8',
          callbacks: { label: function(c) { var t = c.dataset.data.reduce(function(a,b){return a+b;},0); var p = t>0?Math.round((c.parsed/t)*100):0; return ' '+c.label+': '+c.parsed+' ('+p+'%)'; } }
        }
      }
    }
  });
  var legend = document.getElementById('donut-legend');
  if (legend) {
    legend.innerHTML = '';
    var total = values.reduce(function(a,b){return a+b;},0);
    labels.forEach(function(l,i) {
      var pct = total>0?Math.round((values[i]/total)*100):0;
      legend.innerHTML += '<div style="display:flex;align-items:center;gap:5px;"><div style="width:10px;height:10px;border-radius:2px;background:'+colors[i]+';flex-shrink:0;"></div><span style="color:var(--text-muted);">'+l+' <strong style="color:var(--text-primary);">'+pct+'%</strong></span></div>';
    });
  }
}

function sbox(label, val, icon, bg, color) {
  return '<div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:14px 16px;display:flex;align-items:center;gap:12px;"><div style="width:40px;height:40px;border-radius:6px;background:'+bg+';display:flex;align-items:center;justify-content:center;flex-shrink:0;"><i class="bi '+icon+'" style="color:'+color+';font-size:1rem;"></i></div><div><div style="font-size:1.7rem;font-weight:700;color:'+color+';line-height:1;">'+val+'</div><div style="font-size:0.72rem;color:var(--text-muted);margin-top:3px;text-transform:uppercase;letter-spacing:0.5px;">'+label+'</div></div></div>';
}

function exportCSV() {
  if (!reportData || !reportData.facilities) return;
  var month = document.getElementById('month-select').value;
  var year  = document.getElementById('year-select').value;
  var rows  = ['Facility,Total,Approved,Pending,Rejected,Displaced,Conflicts,Hours,Rate'];
  reportData.facilities.forEach(function(f) {
    var rate = f.total_bookings > 0 ? Math.round((f.approved/f.total_bookings)*100) : 0;
    rows.push([f.facility,f.total_bookings,f.approved,f.pending,f.rejected,f.displaced,f.conflicts,f.total_hours_booked,rate+'%'].join(','));
  });
  var blob = new Blob([rows.join('\\n')], { type: 'text/csv;charset=utf-8;' });
  var url  = URL.createObjectURL(blob);
  var a    = document.createElement('a');
  a.href   = url;
  a.download = 'CampusGrid_' + MONTHS[parseInt(month)] + '_' + year + '.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', function() {
  var s    = document.createElement('script');
  s.src    = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
  s.onload = function() { loadReports(); };
  s.onerror = function() {
    document.getElementById('reports-content').innerHTML = '<div class="cg-alert cg-alert-error">Chart library failed to load. Check your internet connection.</div>';
  };
  document.head.appendChild(s);
});
""")

# ── booking_form.js ──────────────────────────────────────────────
w('ui/static/js/booking_form.js', """
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
      btn.innerHTML     = '<i class="bi bi-check-circle me-1"></i> Booking Successful';
      btn.style.background = '#2A6B4A';
      showToast('Booking submitted successfully. Awaiting approval from the Sports Director.');
      setTimeout(function() { window.location.href = '/bookings/confirm/?id=' + data.id; }, 2200);
    } else {
      btn.disabled  = false;
      btn.innerHTML = '<i class="bi bi-send me-1"></i> Submit Request';
      document.getElementById('form-alert').innerHTML = '<div class="cg-alert cg-alert-error"><i class="bi bi-exclamation-circle me-2"></i>' + (data.detail || JSON.stringify(data)) + '</div>';
      document.getElementById('form-alert').style.display = 'block';
    }
  }
}
""")

print('All static JS files written successfully.')
print('Now run: python fix_clean_templates.py')
