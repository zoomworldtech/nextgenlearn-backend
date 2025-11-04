from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from django.core.paginator import Paginator
import json


# ------------------ Homepage ------------------ #
def home(request):
    return render(request, 'accounts/home.html')


# ------------------ Authentication Views ------------------ #
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------ Dashboard Views ------------------ #
@login_required
def dashboard_view(request):
    user = request.user

    if user.role == 'student':
        return render(request, 'accounts/student_dashboard.html', {'user': user})
    elif user.role == 'lecturer':
        return render(request, 'accounts/lecturer_dashboard.html', {'user': user})
    elif user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return HttpResponse("Invalid role. Contact admin.")


# ------------------ Admin Dashboard & Management ------------------ #
def is_admin(user):
    return user.role == 'admin'


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main dashboard view for admins"""
    total_users = CustomUser.objects.count()
    total_students = CustomUser.objects.filter(role='student').count()
    total_lecturers = CustomUser.objects.filter(role='lecturer').count()
    total_admins = CustomUser.objects.filter(role='admin').count()

    # Search by name or email
    search_query = request.GET.get('search', '')
    users_list = CustomUser.objects.all()
    if search_query:
        users_list = users_list.filter(
            first_name__icontains=search_query
        ) | users_list.filter(
            last_name__icontains=search_query
        ) | users_list.filter(
            email__icontains=search_query
        )

    # Pagination (20 users per page)
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_admins': total_admins,
        'users': users_page,
        'search_query': search_query,
    }

    return render(request, 'accounts/admin_dashboard.html', context)


@user_passes_test(is_admin)
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})


@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.save()
        return redirect('manage_users')
    return render(request, 'accounts/edit_user.html', {'user': user})


@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('manage_users')


# ------------------ JSON API for Frontend ------------------ #
@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            role = data.get('role', 'student')
            password1 = data.get('password1')
            password2 = data.get('password2')

            if not all([first_name, last_name, email, password1, password2]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)
            if password1 != password2:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists.'}, status=400)

            user = CustomUser.objects.create_user(
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            return JsonResponse({'message': 'User created successfully.'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if not all([email, password]):
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': f'Login successful as {user.role}.'}, status=200)

            return JsonResponse({'error': 'Invalid email or password.'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def approve_courses(request):
    if request.user.role != 'admin':
        return HttpResponse("Access Denied")

    pending_courses = []  # Replace with Course.objects.filter(status='pending')
    return render(request, 'accounts/approve_courses.html', {'pending_courses': pending_courses})


@login_required
def approve_courses(request):
    if request.user.role != 'admin':
        return HttpResponse("Access Denied")
    pending_courses = []  # Later replace with Course.objects.filter(status='pending')
    return render(request, 'accounts/approve_courses.html', {'pending_courses': pending_courses})

@login_required
def approve_results(request):
    if request.user.role != 'admin':
        return HttpResponse("Access Denied")
    pending_results = []  # Replace with Result.objects.filter(status='pending')
    return render(request, 'accounts/approve_results.html', {'pending_results': pending_results})

@login_required
def approve_payments(request):
    if request.user.role != 'admin':
        return HttpResponse("Access Denied")
    pending_payments = []  # Replace with Payment.objects.filter(status='pending')
    return render(request, 'accounts/approve_payments.html', {'pending_payments': pending_payments})

