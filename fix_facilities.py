content = """\
{% extends 'base.html' %}
{% block title %}Facilities{% endblock %}
{% block page_title %}Facilities{% endblock %}

{% block content %}
<div id="facilities-content">
  <div style="text-align:center;padding:40px;color:var(--text-muted);">
    <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
    <p style="margin-top:8px;">Loading facilities...</p>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadFacilities() {
  const res = await API.get('/facilities/');
  const container = document.getElementById('facilities-content');
  if (!res || !res.ok) return;
  const data = await res.json();
  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-building" style="font-size:2.5rem;"></i><p style="margin-top:12px;">No facilities available.</p></div>';
    return;
  }
  let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;">';
  data.forEach(function(f) {
    html += '<div class="cg-card">';
    html += '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">';
    html += '<div><div style="font-size:1rem;font-weight:600;">' + f.name + '</div>';
    html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-top:2px;"><i class="bi bi-geo-alt me-1"></i>' + f.location + '</div></div>';
    html += '<span style="background:rgba(34,197,94,0.15);color:#22C55E;padding:3px 8px;border-radius:20px;font-size:0.7rem;font-weight:600;">Active</span></div>';
    html += '<div style="display:flex;gap:16px;font-size:0.82rem;color:var(--text-muted);margin-bottom:12px;">';
    html += '<span><i class="bi bi-people me-1"></i>' + f.capacity + ' capacity</span>';
    html += '<span><i class="bi bi-grid me-1"></i>' + f.zones.length + ' zone' + (f.zones.length !== 1 ? 's' : '') + '</span></div>';
    if (f.zones.length) {
      html += '<div style="margin-bottom:12px;"><div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Zones</div>';
      html += '<div style="display:flex;flex-wrap:wrap;gap:6px;">';
      f.zones.forEach(function(z) {
        html += '<span style="background:rgba(46,117,182,0.1);color:#93C5FD;padding:2px 8px;border-radius:20px;font-size:0.72rem;">' + z.name + ' (' + z.capacity + ')</span>';
      });
      html += '</div></div>';
    }
    if (f.recurring_blocks.length) {
      html += '<div style="margin-bottom:12px;"><div style="font-size:0.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Recurring Blocks</div>';
      f.recurring_blocks.forEach(function(b) {
        html += '<div style="font-size:0.78rem;color:var(--accent-gold);"><i class="bi bi-lock me-1"></i>' + b.label + ' \u2014 every ' + b.day_name + ' ' + b.start_time + '\u2013' + b.end_time + '</div>';
      });
      html += '</div>';
    }
    html += '<a href="/bookings/new/?facility=' + f.id + '" class="btn-cg-outline" style="display:block;text-align:center;text-decoration:none;font-size:0.82rem;padding:8px;"><i class="bi bi-plus-circle me-1"></i> Book this facility</a>';
    html += '</div>';
  });
  html += '</div>';
  container.innerHTML = html;
}
loadFacilities();
</script>
{% endblock %}
"""

with open('templates/facilities/list.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Facilities template written successfully')
