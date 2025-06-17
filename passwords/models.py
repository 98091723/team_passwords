from django.db import models
from django.contrib.auth import get_user_model
from teams.models import Team
import base64

User = get_user_model()

class PasswordEntry(models.Model):
    """密码条目模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    website = models.URLField(blank=True, verbose_name='网站')
    username = models.CharField(max_length=100, verbose_name='用户名')
    encrypted_password = models.BinaryField(verbose_name='加密密码')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    # 所有者信息
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries', verbose_name='所有者')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, verbose_name='所属团队')
    
    # 加密相关
    salt = models.BinaryField(max_length=32, verbose_name='盐值')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.title} ({self.username})"
    
    class Meta:
        verbose_name = '密码条目'
        verbose_name_plural = '密码条目'
        ordering = ['-updated_at']