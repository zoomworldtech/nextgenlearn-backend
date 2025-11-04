from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect
from django.contrib.auth import logout


# ------------------ Normal Web Views ------------------ #

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
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard_view(request):
    user = request.user
    role = getattr(user, 'role', None)

    if role == 'student':
        return render(request, 'accounts/student_dashboard.html', {'user': user})
    elif role == 'lecturer':
        return render(request, 'accounts/lecturer_dashboard.html', {'user': user})
    elif role == 'admin':
        return render(request, 'accounts/admin_dashboard.html', {'user': user})
    else:
        return HttpResponse("Invalid role. Contact admin.")


# ------------------ Admin CRUD Views ------------------ #

def is_admin(user):
    return user.role == 'admin'


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
    """Handle registration from frontend via JSON"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            role = data.get('role', 'student')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validation
            if not all([first_name, last_name, email, password1, password2]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            if password1 != password2:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists.'}, status=400)

            # Create user
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


    """Handle login from frontend via JSON"""
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



from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Accounts app!")
