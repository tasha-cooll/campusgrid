from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json


def login_view(request):
    if request.user.is_authenticated:
        return redirect('ui:calendar')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(
                    request, 'Your account is pending activation by the administrator.')
                return render(request, 'auth/login.html')
            login(request, user)
            if user.must_change_password:
                return render(request, 'auth/login_redirect.html', {
                    'username': username,
                    'password': password,
                    'redirect_to': '/change-password/',
                })
            return render(request, 'auth/login_redirect.html', {
                'username': username,
                'password': password,
                'redirect_to': '/calendar/',
            })
        messages.error(
            request, 'Invalid credentials. Please check your ID and password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('ui:login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('ui:calendar')
    if request.method == 'POST':
        institutional_id = request.POST.get(
            'institutional_id', '').strip().upper()
        username = institutional_id
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'requester')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        from accounts.models import CustomUser, Role

        # Validation
        if not institutional_id:
            messages.error(request, 'Student ID or Staff ID is required.')
            return render(request, 'auth/signup.html')

        if not email:
            messages.error(request, 'Email address is required.')
            return render(request, 'auth/signup.html')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/signup.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'auth/signup.html')

        if CustomUser.objects.filter(institutional_id=institutional_id).exists():
            messages.error(request, 'An account with this ID already exists.')
            return render(request, 'auth/signup.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(
                request, 'An account with this email already exists.')
            return render(request, 'auth/signup.html')

        if role not in ['requester', 'approver', 'admin']:
            role = 'requester'

        # Requesters are active immediately
        # Approvers and Admins need activation
        is_active = role == 'requester'

        user = CustomUser.objects.create_user(
            username=username,
            institutional_id=institutional_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role,
            password=password,
            is_active=is_active,
            must_change_password=False,
        )

        if is_active:
            messages.success(
                request, 'Account created successfully. You can now sign in.')
        else:
            messages.success(
                request, 'Account created. Your account requires administrator approval before you can sign in. Please wait for activation.')

        return redirect('ui:login')

    return render(request, 'auth/signup.html')


@login_required(login_url='/')
def calendar_view(request):
    return render(request, 'calendar/index.html', {
        'user': request.user,
        'page': 'calendar'
    })


@login_required(login_url='/')
def dashboard_view(request):
    return render(request, 'dashboard/index.html', {
        'user': request.user,
        'page': 'dashboard'
    })


@login_required(login_url='/')
def bookings_view(request):
    return render(request, 'bookings/list.html', {
        'user': request.user,
        'page': 'bookings'
    })


@login_required(login_url='/')
def new_booking_view(request):
    from facilities.models import Facility
    import json

    facilities_raw = Facility.objects.filter(
        is_active=True).prefetch_related('zones', 'recurring_blocks')
    facilities = []
    for f in facilities_raw:
        facilities.append({
            'id':          f.id,
            'name':        f.name,
            'location':    f.location,
            'capacity':    f.capacity,
            'zones_json':  json.dumps([{'id': z.id, 'name': z.name, 'capacity': z.capacity} for z in f.zones.filter(is_active=True)]),
            'blocks_json': json.dumps([{'label': b.label, 'day_name': b.get_day_of_week_display(), 'start_time': str(b.start_time)[:5], 'end_time': str(b.end_time)[:5]} for b in f.recurring_blocks.filter(is_active=True)]),
        })

    return render(request, 'bookings/new.html', {
        'user':       request.user,
        'page':       'bookings',
        'facilities': facilities,
    })


@login_required(login_url='/')
def approvals_view(request):
    if request.user.role not in ['approver', 'admin']:
        return redirect('ui:calendar')
    return render(request, 'approvals/queue.html', {
        'user': request.user,
        'page': 'approvals'
    })


@login_required(login_url='/')
def facilities_view(request):
    return render(request, 'facilities/list.html', {
        'user': request.user,
        'page': 'facilities'
    })


@login_required(login_url='/')
def reports_view(request):
    if request.user.role not in ['approver', 'admin']:
        return redirect('ui:calendar')
    return render(request, 'reports/index.html', {
        'user': request.user,
        'page': 'reports'
    })


def change_password_view(request):
    from django.contrib.auth import update_session_auth_hash
    forced = request.user.must_change_password if request.user.is_authenticated else False

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '')
        new_password2 = request.POST.get('new_password2', '')
        current_password = request.POST.get('current_password', '')

        if new_password != new_password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/change_password.html', {'forced': forced})

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'auth/change_password.html', {'forced': forced})

        if not forced:
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return render(request, 'auth/change_password.html', {'forced': forced})

        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Password changed successfully.')
        return redirect('ui:calendar')

    return render(request, 'auth/change_password.html', {
        'user':   request.user,
        'page':   'settings',
        'forced': forced
    })


@login_required(login_url='/')
def users_view(request):
    if request.user.role != 'admin':
        return redirect('ui:calendar')
    return render(request, 'users/list.html', {
        'user': request.user,
        'page': 'users'
    })


@login_required(login_url='/')
def booking_confirmation_view(request):
    return render(request, 'bookings/confirmation.html', {
        'user': request.user,
        'page': 'bookings'
    })


@login_required(login_url='/')
def notifications_view(request):
    return render(request, 'notifications/list.html', {
        'user': request.user,
        'page': 'notifications'
    })


def custom_404_view(request, exception):
    return render(request, '404.html', {
        'user': request.user,
    }, status=404)
