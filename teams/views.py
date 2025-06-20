from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership
from passwords.models import PasswordEntry
from logs.models import OperationLog
from django.views.decorators.http import require_POST

User = get_user_model()

@login_required
def team_list(request):
    """团队列表"""
    owned_teams = Team.objects.filter(owner=request.user)
    member_teams = Team.objects.filter(members=request.user).exclude(owner=request.user)
    
    context = {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
    }
    return render(request, 'teams/team_list.html', context)

@login_required
def create_team(request):
    """创建团队"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if Team.objects.filter(name=name, owner=request.user).exists():
            messages.error(request, '团队名称已存在')
            return render(request, 'teams/create_team.html')
        
        team = Team.objects.create(
            name=name,
            description=description,
            owner=request.user
        )
        
        # 将创建者添加为管理员成员
        TeamMembership.objects.create(
            user=request.user,
            team=team,
            role='admin'
        )
        
        messages.success(request, f'团队 "{name}" 创建成功')
        return redirect('team_detail', team_id=team.id)
    
    return render(request, 'teams/create_team.html')

@login_required
def team_detail(request, team_id):
    """团队详情"""
    team = get_object_or_404(Team, id=team_id)
    
    # 检查权限
    if not team.members.filter(id=request.user.id).exists():
        messages.error(request, '您不是该团队成员')
        return redirect('team_list')
    
    memberships = TeamMembership.objects.filter(team=team).select_related('user')
    user_membership = TeamMembership.objects.get(team=team, user=request.user)
    
    # 获取团队密码
    team_passwords = PasswordEntry.objects.filter(team=team).order_by('-updated_at')
    
    context = {
        'team': team,
        'memberships': memberships,
        'user_role': user_membership.role,
        'is_admin': user_membership.role == 'admin' or team.owner == request.user,
        'team_passwords': team_passwords,
    }
    return render(request, 'teams/team_detail.html', context)

@login_required
def add_member(request, team_id):
    """添加团队成员"""
    team = get_object_or_404(Team, id=team_id)
    
    # 检查权限
    try:
        membership = TeamMembership.objects.get(team=team, user=request.user)
        if membership.role != 'admin' and team.owner != request.user:
            messages.error(request, '只有管理员可以添加成员')
            OperationLog.objects.create(
                user=request.user,
                op_type='team',
                object_repr=f"{team.name} (ID:{team.id})",
                detail='无权限添加成员',
                ip=request.META.get('REMOTE_ADDR'),
                result='失败',
            )
            return redirect('team_detail', team_id=team_id)
    except TeamMembership.DoesNotExist:
        messages.error(request, '您不是该团队成员')
        OperationLog.objects.create(
            user=request.user,
            op_type='team',
            object_repr=f"{team.name} (ID:{team.id})",
            detail='无权限添加成员',
            ip=request.META.get('REMOTE_ADDR'),
            result='失败',
        )
        return redirect('team_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'member')
        
        try:
            user = User.objects.get(username=username)
            if TeamMembership.objects.filter(team=team, user=user).exists():
                messages.error(request, '用户已是团队成员')
                OperationLog.objects.create(
                    user=request.user,
                    op_type='team',
                    object_repr=f"{team.name} (ID:{team.id})",
                    detail=f'添加成员失败：{username}已是团队成员',
                    ip=request.META.get('REMOTE_ADDR'),
                    result='失败',
                )
            else:
                TeamMembership.objects.create(
                    team=team,
                    user=user,
                    role=role
                )
                messages.success(request, f'用户 {username} 已添加到团队')
                OperationLog.objects.create(
                    user=request.user,
                    op_type='team',
                    object_repr=f"{team.name} (ID:{team.id})",
                    detail=f'添加成员：{username}，角色：{role}',
                    ip=request.META.get('REMOTE_ADDR'),
                    result='成功',
                )
        except User.DoesNotExist:
            messages.error(request, '用户不存在')
            OperationLog.objects.create(
                user=request.user,
                op_type='team',
                object_repr=f"{team.name} (ID:{team.id})",
                detail=f'添加成员失败：{username}不存在',
                ip=request.META.get('REMOTE_ADDR'),
                result='失败',
            )
        
        return redirect('team_detail', team_id=team_id)
    
    context = {'team': team}
    return render(request, 'teams/add_member.html', context)

@login_required
@require_POST
def remove_member(request, team_id, user_id):
    team = get_object_or_404(Team, id=team_id)
    try:
        membership = TeamMembership.objects.get(team=team, user=request.user)
        if membership.role != 'admin' and team.owner != request.user:
            messages.error(request, '只有管理员可以移除成员')
            OperationLog.objects.create(
                user=request.user,
                op_type='team',
                object_repr=f"{team.name} (ID:{team.id})",
                detail='无权限移除成员',
                ip=request.META.get('REMOTE_ADDR'),
                result='失败',
            )
            return redirect('team_detail', team_id=team_id)
    except TeamMembership.DoesNotExist:
        messages.error(request, '您不是该团队成员')
        OperationLog.objects.create(
            user=request.user,
            op_type='team',
            object_repr=f"{team.name} (ID:{team.id})",
            detail='无权限移除成员',
            ip=request.META.get('REMOTE_ADDR'),
            result='失败',
        )
        return redirect('team_list')
    try:
        user = User.objects.get(id=user_id)
        if user == team.owner:
            messages.error(request, '不能移除团队所有者')
            OperationLog.objects.create(
                user=request.user,
                op_type='team',
                object_repr=f"{team.name} (ID:{team.id})",
                detail='尝试移除所有者',
                ip=request.META.get('REMOTE_ADDR'),
                result='失败',
            )
        else:
            TeamMembership.objects.filter(team=team, user=user).delete()
            messages.success(request, f'成员 {user.username} 已被移除')
            OperationLog.objects.create(
                user=request.user,
                op_type='team',
                object_repr=f"{team.name} (ID:{team.id})",
                detail=f'移除成员：{user.username}',
                ip=request.META.get('REMOTE_ADDR'),
                result='成功',
            )
    except User.DoesNotExist:
        messages.error(request, '用户不存在')
        OperationLog.objects.create(
            user=request.user,
            op_type='team',
            object_repr=f"{team.name} (ID:{team.id})",
            detail='移除成员失败：用户不存在',
            ip=request.META.get('REMOTE_ADDR'),
            result='失败',
        )
    return redirect('team_detail', team_id=team_id)