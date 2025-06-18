from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from utils.crypto import CryptoManager
import os

User = get_user_model()

def setup_super_admin(request):
    """设置超级管理员（首次登录）"""
    # 检查是否已有超级管理员
    if User.objects.filter(is_super_admin=True).exists():
        return redirect('login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        if password != confirm_password:
            messages.error(request, '密码确认不匹配')
            return render(request, 'accounts/setup_super_admin.html')
        
        if len(password) < 8:
            messages.error(request, '密码长度至少8位')
            return render(request, 'accounts/setup_super_admin.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'accounts/setup_super_admin.html')
        
        # 创建超级管理员
        salt = os.urandom(32)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_super_admin=True,
            salt=salt
        )
        
        messages.success(request, '超级管理员创建成功，请登录')
        return redirect('login')
    
    return render(request, 'accounts/setup_super_admin.html')

def user_login(request):
    """用户登录"""
    # 检查是否需要设置超级管理员
    if not User.objects.filter(is_super_admin=True).exists():
        return redirect('setup_super_admin')
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if next_url and isinstance(next_url, str) and next_url.startswith('/'):
                return redirect(next_url)
            else:
                return redirect('dashboard')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'accounts/login.html', {'next': next_url})

@login_required
def register_user(request):
    """注册新用户（需要管理员权限）"""
    if not request.user.is_super_admin:
        messages.error(request, '只有超级管理员可以创建新用户')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'accounts/register.html')
        
        salt = os.urandom(32)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            salt=salt
        )
        
        messages.success(request, f'用户 {username} 创建成功')
        return redirect('user_list')
    
    return render(request, 'accounts/register.html')

@login_required
def user_list(request):
    """用户列表"""
    if not request.user.is_super_admin:
        messages.error(request, '权限不足')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})