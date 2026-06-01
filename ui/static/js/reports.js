
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
  var blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
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
