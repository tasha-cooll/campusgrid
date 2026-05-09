content = """\
{% extends 'base.html' %}
{% block title %}Reports{% endblock %}
{% block page_title %}Reports &amp; Analytics{% endblock %}

{% block content %}
<div class="d-flex gap-3 align-items-center mb-4">
  <select id="month-select" onchange="loadReports()" style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:8px;color:var(--text-primary);padding:6px 12px;font-size:0.85rem;">
    <option value="1">January</option><option value="2">February</option>
    <option value="3">March</option><option value="4">April</option>
    <option value="5" selected>May</option><option value="6">June</option>
    <option value="7">July</option><option value="8">August</option>
    <option value="9">September</option><option value="10">October</option>
    <option value="11">November</option><option value="12">December</option>
  </select>
  <select id="year-select" onchange="loadReports()" style="background:var(--bg-secondary);border:1px solid var(--border);border-radius:8px;color:var(--text-primary);padding:6px 12px;font-size:0.85rem;">
    <option value="2026" selected>2026</option>
    <option value="2027">2027</option>
  </select>
</div>
<div id="reports-content">
  <div style="text-align:center;padding:40px;color:var(--text-muted);">
    <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
    <p style="margin-top:8px;">Loading reports...</p>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadReports() {
  const month = document.getElementById('month-select').value;
  const year  = document.getElementById('year-select').value;
  const container = document.getElementById('reports-content');
  const [utilRes, conflictRes] = await Promise.all([
    API.get('/reports/utilization/?month=' + month + '&year=' + year),
    API.get('/reports/conflicts/?month=' + month + '&year=' + year),
  ]);
  if (!utilRes || !utilRes.ok) return;
  const util     = await utilRes.json();
  const conflict = conflictRes && conflictRes.ok ? await conflictRes.json() : null;
  let html = '<div style="display:grid;gap:20px;">';
  html += '<div class="cg-card"><div class="cg-card-title">Facility Utilization</div>';
  html += '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;margin-top:12px;">';
  html += '<thead><tr style="border-bottom:1px solid var(--border);color:var(--text-muted);font-size:0.75rem;text-transform:uppercase;">';
  html += '<th style="padding:8px 12px;text-align:left;">Facility</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Total</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Approved</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Pending</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Rejected</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Displaced</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Conflicts</th>';
  html += '<th style="padding:8px 12px;text-align:center;">Hours</th>';
  html += '</tr></thead><tbody>';
  util.facilities.forEach(function(f) {
    html += '<tr style="border-bottom:1px solid var(--border);">';
    html += '<td style="padding:10px 12px;font-weight:500;">' + f.facility + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;">' + f.total_bookings + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;color:#22C55E;">' + f.approved + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;color:#F4A261;">' + f.pending + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;color:#EF4444;">' + f.rejected + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;color:#FF6B35;">' + f.displaced + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;color:#F4A261;">' + f.conflicts + '</td>';
    html += '<td style="padding:10px 12px;text-align:center;">' + f.total_hours_booked + 'h</td>';
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  if (conflict) {
    html += '<div class="cg-card"><div class="cg-card-title">Conflict Summary</div>';
    html += '<div style="display:flex;align-items:center;gap:24px;margin:16px 0;">';
    html += '<div style="text-align:center;"><div style="font-size:2.5rem;font-weight:700;color:#F4A261;">' + conflict.total_conflicts + '</div>';
    html += '<div style="font-size:0.78rem;color:var(--text-muted);">Total Conflicts</div></div>';
    html += '<div style="flex:1;display:grid;gap:8px;">';
    Object.entries(conflict.by_facility).forEach(function(entry) {
      const facility = entry[0]; const count = entry[1];
      html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:var(--bg-primary);border-radius:8px;font-size:0.82rem;">';
      html += '<span>' + facility + '</span><span style="color:#F4A261;font-weight:600;">' + count + ' conflict' + (count !== 1 ? 's' : '') + '</span></div>';
    });
    html += '</div></div></div>';
  }
  html += '</div>';
  container.innerHTML = html;
}
loadReports();
</script>
{% endblock %}
"""

with open('templates/reports/index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Reports template written successfully')
