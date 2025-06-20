from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class OperationLog(models.Model):
    OP_TYPE_CHOICES = [
        ('view', '查看'),
        ('add', '添加'),
        ('edit', '编辑'),
        ('delete', '删除'),
        ('export', '导出'),
        ('team', '团队变更'),
        ('login', '登录'),
        ('other', '其它'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    op_type = models.CharField(max_length=20, choices=OP_TYPE_CHOICES, verbose_name='操作类型')
    object_repr = models.CharField(max_length=255, verbose_name='对象描述')
    detail = models.TextField(blank=True, verbose_name='详情')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    result = models.CharField(max_length=20, verbose_name='结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_op_type_display()}] {self.user} {self.object_repr} {self.result}" 