#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_passwords.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    user = User.objects.get(username='yunda_98091723')
    print(f"✅ 用户存在: {user.username}")
    print(f"是否激活: {user.is_active}")
    print(f"是否超级管理员: {user.is_super_admin}")
    print(f"最后登录: {user.last_login}")
    print(f"创建时间: {user.date_joined}")
    print(f"邮箱: {user.email}")
    
    # 测试密码验证
    from django.contrib.auth import authenticate
    test_user = authenticate(username='yunda_98091723', password='%aaNdQYB3Xz:at6')
    if test_user:
        print("✅ 密码验证成功")
    else:
        print("❌ 密码验证失败")
        
except User.DoesNotExist:
    print("❌ 用户不存在")
except Exception as e:
    print(f"❌ 检查用户时出错: {e}") 