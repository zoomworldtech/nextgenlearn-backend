from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomLoginForm


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
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required 

def dashboard_view(request):
    user = request.user

    if user.role == 'student':
        return render(request, 'accounts/student_dashboard.html', {'user': user})

    elif user.role == 'lecturer':
        return render(request, 'accounts/lecturer_dashboard.html', {'user': user})

    elif user.role == 'admin':
        return render(request, 'accounts/admin_dashboard.html', {'user': user})

    else:
        return HttpResponse("Invalid role. Contact admin.")

# admin with roles
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser

def is_admin(user):
    return user.role == 'admin'

@user_passes_test(is_admin)
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})

# for crud edit
from django.shortcuts import get_object_or_404

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
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

# will remove json if error occurs lol zoom work
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            email = data.get('email')
            role = data.get('role', 'student')
            password1 = data.get('password1')
            password2 = data.get('password2')

            if not all([username, email, password1, password2]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            if password1 != password2:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists.'}, status=400)

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role
            )
            return JsonResponse({'message': 'User created successfully.'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)



@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': f'Login successful as {user.role}.'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
