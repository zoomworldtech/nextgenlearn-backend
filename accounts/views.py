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

