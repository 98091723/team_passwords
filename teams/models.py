from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Team(models.Model):
    """团队模型"""
    name = models.CharField(max_length=100, verbose_name='团队名称')
    description = models.TextField(blank=True, verbose_name='团队描述')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams', verbose_name='所有者')
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams', verbose_name='成员')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '团队'
        verbose_name_plural = '团队'

class TeamMembership(models.Model):
    """团队成员关系模型"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('member', '成员'),
        ('viewer', '查看者'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='团队')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member', verbose_name='角色')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    
    class Meta:
        unique_together = ['user', 'team']
        verbose_name = '团队成员'
        verbose_name_plural = '团队成员'

class TeamInvite(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invites', verbose_name='团队')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites', verbose_name='邀请人')
    email = models.EmailField(blank=True, null=True, verbose_name='受邀邮箱')
    code = models.CharField(max_length=64, unique=True, verbose_name='邀请码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='邀请时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    accepted = models.BooleanField(default=False, verbose_name='已接受')
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_invites', verbose_name='受邀用户')

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.team.name} 邀请({self.email or self.code})"

    class Meta:
        verbose_name = '团队邀请'
        verbose_name_plural = '团队邀请'