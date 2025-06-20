from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import PasswordEntry
from teams.models import Team, TeamMembership
from utils.crypto import CryptoManager
import os
import json
import re
from logs.models import OperationLog

@login_required
def password_list(request):
    """密码列表"""
    # 检查用户权限
    is_super_admin = request.user.is_super_admin
    
    if is_super_admin:
        # 超级管理员可以查看所有密码
        personal_passwords = PasswordEntry.objects.filter(team__isnull=True).order_by('-updated_at')
        team_passwords = PasswordEntry.objects.filter(team__isnull=False).order_by('-updated_at')
        all_teams = Team.objects.all()
    else:
        # 普通用户只能查看自己的个人密码和所在团队的密码
        personal_passwords = PasswordEntry.objects.filter(owner=request.user, team__isnull=True).order_by('-updated_at')
        user_teams = Team.objects.filter(members=request.user)
        team_passwords = PasswordEntry.objects.filter(team__in=user_teams).order_by('-updated_at')
        all_teams = user_teams
    
    context = {
        'personal_passwords': personal_passwords,
        'team_passwords': team_passwords,
        'teams': all_teams,
        'is_super_admin': is_super_admin,
    }
    return render(request, 'passwords/dashboard.html', context)

@login_required
def add_password(request):
    """添加密码"""
    if request.method == 'POST':
        title = request.POST.get('title')
        website = request.POST.get('website', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        notes = request.POST.get('notes', '')
        team_id = request.POST.get('team')
        
        # 验证必填字段
        if not all([title, username, password]):
            messages.error(request, '请填写所有必填字段')
            return render(request, 'passwords/add_password.html', {
                'teams': Team.objects.filter(members=request.user)
            })
        
        # 处理团队分配
        team = None
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            # 检查用户是否为团队成员
            if not team.members.filter(id=request.user.id).exists():
                messages.error(request, '您不是该团队成员')
                return redirect('dashboard')
        
        # 生成盐值和加密密码
        salt = os.urandom(32)
        key = CryptoManager.derive_key(request.user.username, salt)
        encrypted_password = CryptoManager.encrypt_data(password, key)
        
        # 创建密码条目
        PasswordEntry.objects.create(
            title=title,
            website=website,
            username=username,
            encrypted_password=encrypted_password,
            notes=notes,
            owner=request.user,
            team=team,
            salt=salt
        )
        
        messages.success(request, '密码添加成功')
        return redirect('dashboard')
    
    context = {
        'teams': Team.objects.filter(members=request.user)
    }
    return render(request, 'passwords/add_password.html', context)

@login_required
def edit_password(request, password_id):
    """编辑密码"""
    password_entry = get_object_or_404(PasswordEntry, id=password_id)
    
    # 检查权限
    can_edit = False
    is_super_admin = request.user.is_super_admin
    
    if is_super_admin:
        # 超级管理员可以编辑所有密码
        can_edit = True
    elif password_entry.team:
        # 团队密码：检查是否为团队管理员或密码所有者
        try:
            membership = TeamMembership.objects.get(team=password_entry.team, user=request.user)
            if membership.role == 'admin' or password_entry.owner == request.user:
                can_edit = True
        except TeamMembership.DoesNotExist:
            pass
    else:
        # 个人密码：只有所有者可以编辑
        if password_entry.owner == request.user:
            can_edit = True
    
    if not can_edit:
        messages.error(request, '您没有权限编辑此密码')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        website = request.POST.get('website', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        notes = request.POST.get('notes', '')
        team_id = request.POST.get('team')
        
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
            return render(request, 'passwords/edit_password.html', {
                'password_entry': password_entry,
                'teams': Team.objects.filter(members=request.user) if not is_super_admin else Team.objects.all(),
                'decrypted_password': CryptoManager.decrypt_data(password_entry.encrypted_password, 
                                                               CryptoManager.derive_key(password_entry.owner.username, password_entry.salt)),
                'is_super_admin': is_super_admin
            })
        
        # 处理团队分配
        team = None
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            # 检查用户是否为团队成员（超级管理员除外）
            if not is_super_admin and not team.members.filter(id=request.user.id).exists():
                messages.error(request, '您不是该团队成员')
                return redirect('dashboard')
        
        # 如果密码发生变化，重新加密
        if password != CryptoManager.decrypt_data(password_entry.encrypted_password, 
                                                CryptoManager.derive_key(password_entry.owner.username, password_entry.salt)):
            salt = os.urandom(32)
            key = CryptoManager.derive_key(request.user.username, salt)
            encrypted_password = CryptoManager.encrypt_data(password, key)
            password_entry.salt = salt
            password_entry.encrypted_password = encrypted_password
        
        # 更新密码条目
        password_entry.title = title
        password_entry.website = website
        password_entry.username = username
        password_entry.notes = notes
        password_entry.team = team
        password_entry.save()
        
        messages.success(request, '密码更新成功')
        return redirect('view_password', password_id=password_entry.id)
    
    # 解密密码用于编辑
    key = CryptoManager.derive_key(password_entry.owner.username, password_entry.salt)
    decrypted_password = CryptoManager.decrypt_data(password_entry.encrypted_password, key)
    
    context = {
        'password_entry': password_entry,
        'decrypted_password': decrypted_password,
        'teams': Team.objects.filter(members=request.user) if not is_super_admin else Team.objects.all(),
        'is_super_admin': is_super_admin
    }
    return render(request, 'passwords/edit_password.html', context)

@login_required
def view_password(request, password_id):
    """查看密码详情"""
    password_entry = get_object_or_404(PasswordEntry, id=password_id)
    can_view = False
    is_super_admin = request.user.is_super_admin
    if is_super_admin:
        can_view = True
    elif password_entry.team:
        if password_entry.team.members.filter(id=request.user.id).exists():
            can_view = True
    else:
        if password_entry.owner == request.user:
            can_view = True
    result = '失败'
    if not can_view:
        messages.error(request, '您没有权限查看此密码')
        OperationLog.objects.create(
            user=request.user,
            op_type='view',
            object_repr=f"{password_entry.title} (ID:{password_entry.id})",
            detail='无权限查看',
            ip=request.META.get('REMOTE_ADDR'),
            result='失败',
        )
        return redirect('dashboard')
    # 解密密码
    key = CryptoManager.derive_key(password_entry.owner.username, password_entry.salt)
    decrypted_password = CryptoManager.decrypt_data(password_entry.encrypted_password, key)
    OperationLog.objects.create(
        user=request.user,
        op_type='view',
        object_repr=f"{password_entry.title} (ID:{password_entry.id})",
        detail='查看密码',
        ip=request.META.get('REMOTE_ADDR'),
        result='成功',
    )
    context = {
        'password_entry': password_entry,
        'decrypted_password': decrypted_password,
        'is_super_admin': is_super_admin,
    }
    return render(request, 'passwords/view_password.html', context)

@login_required
@require_http_methods(["POST"])
def delete_password(request, password_id):
    """删除密码"""
    password_entry = get_object_or_404(PasswordEntry, id=password_id)
    can_delete = False
    is_super_admin = request.user.is_super_admin
    if is_super_admin:
        can_delete = True
    elif password_entry.team:
        try:
            membership = TeamMembership.objects.get(team=password_entry.team, user=request.user)
            if membership.role == 'admin' or password_entry.owner == request.user:
                can_delete = True
        except TeamMembership.DoesNotExist:
            pass
    else:
        if password_entry.owner == request.user:
            can_delete = True
    result = '失败'
    if not can_delete:
        messages.error(request, '您没有权限删除此密码')
        OperationLog.objects.create(
            user=request.user,
            op_type='delete',
            object_repr=f"{password_entry.title} (ID:{password_entry.id})",
            detail='无权限删除',
            ip=request.META.get('REMOTE_ADDR'),
            result='失败',
        )
        return redirect('dashboard')
    object_desc = f"{password_entry.title} (ID:{password_entry.id})"
    try:
        password_entry.delete()
        messages.success(request, '密码删除成功')
        result = '成功'
    except Exception as e:
        messages.error(request, '密码删除失败')
        result = f'失败:{str(e)}'
    OperationLog.objects.create(
        user=request.user,
        op_type='delete',
        object_repr=object_desc,
        detail='删除密码',
        ip=request.META.get('REMOTE_ADDR'),
        result=result,
    )
    return redirect('dashboard')

@login_required
def generate_password(request):
    """生成强密码API"""
    length = int(request.GET.get('length', 16))
    include_symbols = request.GET.get('symbols', 'true').lower() == 'true'
    
    password = CryptoManager.generate_password(length, include_symbols)
    
    return JsonResponse({'password': password})