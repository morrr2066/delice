from django.contrib import admin
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # الخانات اللي هتخليك تشوف (مين، عمل إيه، فين، والساعة كام)
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'get_change_message')
    list_filter = ('user', 'action_flag', 'content_type')
    search_fields = ('object_repr', 'change_message')

    # عشان تمنع أي حد حتى لو Admin إنه يعدل في السجلات دي (للمصداقية)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

