#!/usr/bin/env python
"""
团队密码管理系统 v2.0.0
Django管理脚本

用于执行Django管理命令，如：
- python manage.py runserver
- python manage.py migrate
- python manage.py createsuperuser
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_passwords.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
	
    main()