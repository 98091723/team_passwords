from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from utils.crypto import CryptoManager
import os
import re

User = get_user_model()

def setup_super_admin(request):
    """设置超级管理员（首次登录）"""
    # 只允许数据库没有任何超级管理员时访问
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
    # 只在没有超级管理员时跳转到setup页面
    if not User.objects.filter(is_super_admin=True).exists():
        return redirect('setup_super_admin')
    
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # 只允许next_url为/开头的路径
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
        
        # 强密码校验
        def is_strong_password(pw):
            if len(pw) < 8:
                return False
            if not re.search(r'[A-Z]', pw):
                return False
            if not re.search(r'[a-z]', pw):
                return False
            if not re.search(r'\d', pw):
                return False
            if not re.search(r'[^A-Za-z0-9]', pw):
                return False
            return True
        if not is_strong_password(password):
            messages.error(request, '密码必须至少8位，包含大写字母、小写字母、数字和特殊字符')
            return render(request, 'accounts/register.html')
        
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