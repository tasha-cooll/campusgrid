content = """\
{% extends 'base.html' %}
{% block title %}My Bookings{% endblock %}
{% block page_title %}My Bookings{% endblock %}

{% block content %}
{% if request.GET.success %}
<div class="cg-alert cg-alert-success mb-4">
  <i class="bi bi-check-circle me-2"></i>Booking submitted successfully. It is now pending approval.
</div>
{% endif %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div style="font-size:0.85rem;color:var(--text-muted);">Your booking history and upcoming reservations.</div>
  <a href="/bookings/new/" class="btn-cg-primary"><i class="bi bi-plus-lg me-1"></i> New Booking</a>
</div>
<div class="cg-card">
  <div id="bookings-list">
    <div style="text-align:center;padding:40px;color:var(--text-muted);">
      <i class="bi bi-hourglass-split" style="font-size:2rem;"></i>
      <p style="margin-top:8px;">Loading your bookings...</p>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
async function loadBookings() {
  const res = await API.get('/bookings/');
  const container = document.getElementById('bookings-list');
  if (!res || !res.ok) {
    container.innerHTML = '<div class="cg-alert cg-alert-error">Failed to load bookings.</div>';
    return;
  }
  const data = await res.json();
  if (!data.length) {
    container.innerHTML = '<div style="text-align:center;padding:48px;color:var(--text-muted);"><i class="bi bi-calendar-x" style="font-size:2.5rem;"></i><p style="margin-top:12px;">No bookings yet.</p><a href="/bookings/new/" class="btn-cg-primary" style="margin-top:12px;">Make your first booking</a></div>';
    return;
  }
  let html = '<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">';
  html += '<thead><tr style="border-bottom:1px solid var(--border);color:var(--text-muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px;">';
  html += '<th style="padding:10px 12px;text-align:left;">Facility / Zone</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Date &amp; Time</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Purpose</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Status</th>';
  html += '<th style="padding:10px 12px;text-align:left;">Actions</th>';
  html += '</tr></thead><tbody>';
  data.forEach(function(b) {
    const startDate = new Date(b.start_time).toLocaleDateString('en-KE', {weekday:'short', month:'short', day:'numeric'});
    const startTime = new Date(b.start_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    const endTime   = new Date(b.end_time).toLocaleTimeString('en-KE', {hour:'2-digit', minute:'2-digit'});
    html += '<tr style="border-bottom:1px solid var(--border);">';
    html += '<td style="padding:12px;"><div style="font-weight:500;">' + b.facility_detail.name + '</div>';
    html += '<div style="font-size:0.75rem;color:var(--text-muted);">' + (b.zone_name || 'Entire facility') + '</div>';
    if (b.is_priority) html += '<span class="status-badge badge-priority" style="margin-top:4px;display:inline-block;">Priority</span>';
    html += '</td>';
    html += '<td style="padding:12px;"><div>' + startDate + '</div><div style="color:var(--text-muted);font-size:0.78rem;">' + startTime + ' \u2014 ' + endTime + '</div></td>';
    html += '<td style="padding:12px;">' + b.purpose + '</td>';
    html += '<td style="padding:12px;"><span class="status-badge badge-' + b.status + '">' + b.status_display + '</span></td>';
    html += '<td style="padding:12px;">';
    if (b.status === 'pending') {
      html += '<button onclick="cancelBooking(' + b.id + ')" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#EF4444;border-radius:6px;padding:4px 10px;font-size:0.75rem;cursor:pointer;">Cancel</button>';
    } else {
      html += '\u2014';
    }
    html += '</td></tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

async function cancelBooking(id) {
  if (!confirm('Are you sure you want to cancel this booking?')) return;
  const res = await API.delete('/bookings/' + id + '/');
  if (res && res.ok) loadBookings();
}

loadBookings();
</script>
{% endblock %}
"""

with open('templates/bookings/list.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Bookings list template written successfully')
