import os

def w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('Written: ' + path)

# ── base.html — remove inline JS, load campusgrid.js instead ────
# Find the inline API/loadNotifCount script block in base.html
# and replace it with a static file reference
base = open('templates/base.html', encoding='utf-8').read()

old_script = base[base.find('<script src="https://cdn.jsdelivr.net/npm/bootstrap'):base.find('{% block extra_scripts %}')]

new_script = """<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
{% load static %}
<script src="{% static 'js/campusgrid.js' %}"></script>
"""

base = base.replace(old_script, new_script)
w('templates/base.html', base)

# ── reports/index.html — clean template, load reports.js ─────────
w('templates/reports/index.html', """\
{% extends 'base.html' %}
{% load static %}
{% block title %}Reports{% endblock %}
{% block page_title %}Reports and Analytics{% endblock %}

{% block extra_styles %}
@media print {
  .sidebar, .topbar, .no-print { display: none !important; }
  .main-content { margin-left: 0 !important; }
  body { background: white !important; color: black !important; }
  .cg-card { border: 1px solid #ccc !important; background: white !important; page-break-inside: avoid; }
  .cg-table th, .cg-table td { color: black !important; border-color: #ccc !important; }
  .print-header { display: block !important; }
}
.print-header { display: none; }
{% endblock %}

{% block content %}
<div class="print-header" style="margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid #C9A84C;">
  <h2 style="margin:0;font-family:'Playfair Display',serif;">CampusGrid - Facility Utilization Report</h2>
  <p style="font-size:0.85rem;color:#666;">University of Eastern Africa Baraton</p>
  <p id="print-period" style="font-size:0.85rem;"></p>
</div>

<div class="no-print d-flex justify-content-between align-items-center mb-4">
  <div style="display:flex;gap:8px;">
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
      <i class="bi bi-printer me-1"></i> Print
    </button>
    <button onclick="exportCSV()" class="btn-cg-primary" style="font-size:0.82rem;">
      <i class="bi bi-download me-1"></i> Export CSV
    </button>
  </div>
</div>

<div id="reports-content">
  <div style="display:grid;gap:12px;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
      <div class="skeleton" style="height:80px;border-radius:6px;"></div>
      <div class="skeleton" style="height:80px;border-radius:6px;"></div>
      <div class="skeleton" style="height:80px;border-radius:6px;"></div>
      <div class="skeleton" style="height:80px;border-radius:6px;"></div>
    </div>
    <div class="skeleton" style="height:280px;border-radius:6px;"></div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{% static 'js/reports.js' %}"></script>
{% endblock %}
""")

# ── bookings/new.html — clean template, load booking_form.js ─────
w('templates/bookings/new.html', """\
{% extends 'base.html' %}
{% load static %}
{% block title %}New Booking{% endblock %}
{% block page_title %}New Booking Request{% endblock %}

{% block content %}
<div style="max-width:640px;">
  <div class="cg-card">
    <h5 style="font-family:'Playfair Display',serif;font-size:1.2rem;font-weight:600;margin-bottom:4px;">Submit a Booking Request</h5>
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
      <div style="padding:16px;background:rgba(123,40,40,0.08);border:1px solid rgba(123,40,40,0.2);border-radius:6px;">
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
<script src="{% static 'js/booking_form.js' %}"></script>
{% endblock %}
""")

print('Clean templates written. Now update settings.py STATICFILES_DIRS.')