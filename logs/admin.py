from django.contrib import admin
from .models import OperationLog

@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'op_type', 'object_repr', 'ip', 'result', 'created_at')
    search_fields = ('user__username', 'object_repr', 'detail', 'ip')
    list_filter = ('op_type', 'result', 'created_at')
    date_hierarchy = 'created_at' 