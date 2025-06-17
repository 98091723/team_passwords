from django.contrib.auth.models import AbstractUser
from django.db import models
import os

class CustomUser(AbstractUser):
    """扩展用户模型"""
    is_super_admin = models.BooleanField(default=False, verbose_name='超级管理员')
    salt = models.BinaryField(max_length=32, default=None, null=True, verbose_name='盐值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def save(self, *args, **kwargs):
        if not self.salt:
            self.salt = os.urandom(32)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'