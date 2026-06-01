content = """\
{% extends 'base.html' %}
{% block title %}Reports{% endblock %}
{% block page_title %}Reports &amp; Analytics{% endblock %}

{% block extra_styles %}
@media print {
  .sidebar, .topbar, .no-print { display: none !important; }
  .main-content { margin-left: 0 !important; }
  body { background: white !important; color: black !important; }
  .cg-card { border: 1px solid #ccc !important; background: white !important; }
  .cg-table th, .cg-table td { color: black !important; border-color: #ccc !important; }
  .print-header { display: block !important; }
}
.print-header { display: none; }
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4 no-print">
  <div style="display:flex;gap:8px;align-items:center;">
    <select id="month-select" onchange="loadReports()" class="cg-input" style="width:auto;padding:6px 12px;">
      <option value="1">January</option><option value="2">February</option>
      <option value="3">March</option><option value="4">April</option>
      <option value="5" selected>May</option><option value="6">June</option>
      <option value="7">July</option><option value="8">August</option>
      <option value="9">September</option><option value="10">October</option>
      <option value="11">November</option><option value="12">December</option>
    </select>
    <select id="year-select" onchange="loadReports()" class="cg-input" style="width:auto;padding:6px 12px;">
      <option value="2026" selected>2026</option>
      <option value="2027">2027</option>
    </select>
  </div>
  <div style="display:flex;gap:8px;">
    <button onclick="window.print()" class="btn-cg-outline" style="font-size:0.82rem;">
      <i class="bi bi-printer me-1"></i> Print Report
    </button>
    <button onclick="exportCSV()" class="btn-cg-primary" style="font-size:0.82rem;">
      <i class="bi bi-download me-1"></i> Export CSV
    </button>
  </div>
</div>

<div class="print-header" style="margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid #333;">
  <h2 style="margin:0;font-size:1.4rem;">CampusGrid — Facility Utilization Report</h2>
  <p style="margin:4px 0 0 0;font-size:0.85rem;color:#666;">University of Eastern Africa Baraton</p>
  <p id="print-period" style="margin:4px 0 0 0;font-size:0.85rem;"></p>
</div>

<div id="reports-content">
  <div style="display:grid;gap:8px;">
    <div class="skeleton" style="height:200px;"></div>
    <div class="skeleton" style="height:120px;"></div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
var reportData = null;
var conflictData = null;
const MONTHS = ['','January','February','March','April','May','June','July','August','September','October','November','December'];

async function loadReports() {
  const month = document.getElementById('month-select').value;
  const year  = document.getElementById('year-select').value;
  const container = document.getElementById('reports-content');
  const printPeriod = document.getElementById('print-period');
  if (printPeriod) printPeriod.textContent = 'Period: ' + MONTHS[parseInt(month)] + ' ' + year;

  const [utilRes, conflictRes] = await Promise.all([
    API.get('/reports/utilization/?month=' + month + '&year=' + year),
    API.get('/reports/conflicts/?month=' + month + '&year=' + year),
  ]);

  if (!utilRes || !utilRes.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load report data.</div>';
    return;
  }

  reportData   = await utilRes.json();
  conflictData = conflictRes && conflictRes.ok ? await conflictRes.json() : null;

  let html = '<div style="display:grid;gap:20px;">';

  // Summary stats row
  if (reportData.facilities && reportData.facilities.length) {
    var totalBookings = 0, totalApproved = 0, totalHours = 0, totalConflicts = 0;
    reportData.facilities.forEach(function(f) {
      totalBookings  += f.total_bookings;
      totalApproved  += f.approved;
      totalHours     += parseFloat(f.total_hours_booked);
      totalConflicts += f.conflicts;
    });
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">';
    html += statBox('Total Bookings', totalBookings, 'bi-journal-bookmark', 'rgba(201,168,76,0.15)', 'var(--accent)');
    html += statBox('Approved', totalApproved, 'bi-check-circle', 'rgba(42,107,74,0.15)', '#6BAB8A');
    html += statBox('Hours Booked', totalHours.toFixed(1) + 'h', 'bi-clock', 'rgba(30,75,143,0.15)', '#7BA7DC');
    html += statBox('Conflicts', totalConflicts, 'bi-shield-exclamation', 'rgba(184,134,11,0.15)', 'var(--accent)');
    html += '</div>';
  }

  // Utilization table
  html += '<div class="cg-card">';
  html += '<div class="cg-card-title">Facility Utilization &mdash; ' + MONTHS[parseInt(month)] + ' ' + year + '</div>';
  html += '<table class="cg-table" id="utilization-table"><thead><tr>';
  html += '<th>Facility</th><th>Total</th><th>Approved</th><th>Pending</th><th>Rejected</th><th>Displaced</th><th>Conflicts</th><th>Hours</th>';
  html += '</tr></thead><tbody>';
  reportData.facilities.forEach(function(f) {
    html += '<tr>';
    html += '<td style="font-weight:500;">' + f.facility + '</td>';
    html += '<td style="text-align:center;">' + f.total_bookings + '</td>';
    html += '<td style="text-align:center;color:#6BAB8A;">' + f.approved + '</td>';
    html += '<td style="text-align:center;color:var(--accent);">' + f.pending + '</td>';
    html += '<td style="text-align:center;color:#C4827A;">' + f.rejected + '</td>';
    html += '<td style="text-align:center;color:#C49A6C;">' + f.displaced + '</td>';
    html += '<td style="text-align:center;color:var(--accent);">' + f.conflicts + '</td>';
    html += '<td style="text-align:center;">' + f.total_hours_booked + 'h</td>';
    html += '</tr>';
  });
  html += '</tbody></table></div>';

  // Conflict summary
  if (conflictData && conflictData.total_conflicts > 0) {
    html += '<div class="cg-card">';
    html += '<div class="cg-card-title">Conflict Summary</div>';
    html += '<div style="display:flex;align-items:center;gap:24px;margin-top:12px;">';
    html += '<div style="text-align:center;padding:16px 24px;background:rgba(184,134,11,0.08);border:1px solid rgba(184,134,11,0.2);border-radius:6px;">';
    html += '<div style="font-family:\'Playfair Display\',serif;font-size:2.5rem;font-weight:700;color:var(--accent);">' + conflictData.total_conflicts + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;">Total Conflicts</div></div>';
    html += '<div style="flex:1;display:grid;gap:8px;">';
    Object.entries(conflictData.by_facility).forEach(function(entry) {
      html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--bg-secondary);border-radius:4px;font-size:0.84rem;">';
      html += '<span>' + entry[0] + '</span>';
      html += '<span style="color:var(--accent);font-weight:600;">' + entry[1] + ' conflict' + (entry[1] !== 1 ? 's' : '') + '</span></div>';
    });
    html += '</div></div></div>';
  }

  html += '</div>';
  container.innerHTML = html;
}

function statBox(label, value, icon, bg, color) {
  return '<div style="background:var(--card-bg);border:1px solid var(--border);border-radius:6px;padding:14px 16px;display:flex;align-items:center;gap:12px;">' +
    '<div style="width:38px;height:38px;border-radius:6px;background:' + bg + ';display:flex;align-items:center;justify-content:center;">' +
    '<i class="bi ' + icon + '" style="color:' + color + ';font-size:1rem;"></i></div>' +
    '<div><div style="font-family:\'Playfair Display\',serif;font-size:1.6rem;font-weight:700;color:' + color + ';line-height:1;">' + value + '</div>' +
    '<div style="font-size:0.73rem;color:var(--text-muted);margin-top:2px;">' + label + '</div></div></div>';
}

function exportCSV() {
  if (!reportData || !reportData.facilities) return;
  const month = document.getElementById('month-select').value;
  const year  = document.getElementById('year-select').value;
  var csv = 'Facility,Total Bookings,Approved,Pending,Rejected,Displaced,Conflicts,Hours Booked\n';
  reportData.facilities.forEach(function(f) {
    csv += f.facility + ',' + f.total_bookings + ',' + f.approved + ',' + f.pending + ',' + f.rejected + ',' + f.displaced + ',' + f.conflicts + ',' + f.total_hours_booked + '\n';
  });
  var blob = new Blob([csv], { type: 'text/csv' });
  var url  = URL.createObjectURL(blob);
  var a    = document.createElement('a');
  a.href   = url;
  a.download = 'CampusGrid_Report_' + MONTHS[parseInt(month)] + '_' + year + '.csv';
  a.click();
  URL.revokeObjectURL(url);
}

loadReports();
</script>
{% endblock %}
"""

with open('templates/reports/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Reports template written successfully')
