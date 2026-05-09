content = """\
{% extends 'base.html' %}

{% block auth_content %}
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-primary);width:100%;padding:24px 0;">
  <div style="width:100%;max-width:480px;padding:24px;">

    <div style="text-align:center;margin-bottom:32px;">
      <div style="font-size:2.2rem;font-weight:800;color:var(--accent);letter-spacing:-1px;">
        Campus<span style="color:var(--text-primary);">Grid</span>
      </div>
      <div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:2px;">
        University of Eastern Africa Baraton
      </div>
    </div>

    <div class="cg-card">
      <h5 style="font-size:1.1rem;font-weight:600;margin-bottom:4px;">Create Account</h5>
      <p style="font-size:0.82rem;color:var(--text-muted);margin-bottom:24px;">
        Fill in your details to register for the facility booking system.
      </p>

      {% if messages %}
        {% for message in messages %}
          <div class="cg-alert cg-alert-info">
            <i class="bi bi-info-circle me-2"></i>{{ message }}
          </div>
        {% endfor %}
      {% endif %}

      <form method="POST" action="/signup/">
        {% csrf_token %}
        <div style="display:grid;gap:14px;">

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div>
              <label class="cg-label">First Name</label>
              <input type="text" name="first_name" class="cg-input" placeholder="First name" required/>
            </div>
            <div>
              <label class="cg-label">Last Name</label>
              <input type="text" name="last_name" class="cg-input" placeholder="Last name" required/>
            </div>
          </div>

          <div>
            <label class="cg-label">Student ID / Staff ID</label>
            <input type="text" name="institutional_id" class="cg-input"
                   placeholder="e.g. SGATWI2311" required
                   style="text-transform:uppercase;"
                   oninput="this.value = this.value.toUpperCase()"/>
            <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px;">
              This will be your login username. Use your official institutional ID.
            </div>
          </div>

          <div>
            <label class="cg-label">Email Address</label>
            <input type="email" name="email" class="cg-input" placeholder="your@email.com" required/>
          </div>

          <div>
            <label class="cg-label">Phone Number <span style="color:var(--text-muted);font-size:0.75rem;">(optional)</span></label>
            <input type="text" name="phone" class="cg-input" placeholder="e.g. 0712345678"/>
          </div>

          <div>
            <label class="cg-label">Account Type</label>
            <select name="role" class="cg-input" id="role-select" onchange="updateRoleNote()">
              <option value="requester">Student / Club Leader (Requester)</option>
              <option value="approver">Sports Director (Approver)</option>
              <option value="admin">Administrator</option>
            </select>
            <div id="role-note" style="margin-top:6px;font-size:0.75rem;padding:8px 10px;border-radius:6px;background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);color:#86EFAC;">
              <i class="bi bi-info-circle me-1"></i>
              Your account will be active immediately after registration.
            </div>
          </div>

          <div>
            <label class="cg-label">Password</label>
            <input type="password" name="password" class="cg-input"
                   placeholder="Minimum 8 characters" required minlength="8"/>
          </div>

          <div>
            <label class="cg-label">Confirm Password</label>
            <input type="password" name="password2" class="cg-input"
                   placeholder="Re-enter your password" required/>
          </div>

        </div>

        <button type="submit" class="btn-cg-primary" style="width:100%;padding:12px;margin-top:20px;">
          Create Account <i class="bi bi-arrow-right ms-1"></i>
        </button>
      </form>

      <p style="text-align:center;margin-top:16px;font-size:0.82rem;color:var(--text-muted);">
        Already have an account?
        <a href="/" style="color:var(--accent);text-decoration:none;">Sign in</a>
      </p>
    </div>

    <p style="text-align:center;font-size:0.72rem;color:var(--text-muted);margin-top:24px;">
      CampusGrid &middot; UEAB Extracurricular Facility Booking &middot; 2026
    </p>
  </div>
</div>

<script>
function updateRoleNote() {
  var role = document.getElementById('role-select').value;
  var note = document.getElementById('role-note');
  if (role === 'requester') {
    note.style.background    = 'rgba(34,197,94,0.08)';
    note.style.borderColor   = 'rgba(34,197,94,0.2)';
    note.style.color         = '#86EFAC';
    note.innerHTML = '<i class="bi bi-check-circle me-1"></i>Your account will be active immediately after registration.';
  } else {
    note.style.background    = 'rgba(244,162,97,0.08)';
    note.style.borderColor   = 'rgba(244,162,97,0.2)';
    note.style.color         = '#FCD34D';
    note.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Your account will require administrator approval before you can sign in.';
  }
}
</script>
{% endblock %}
"""

with open('templates/auth/signup.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('Signup template written successfully')
