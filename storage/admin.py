from django.contrib import admin
from .models import Item, Batch, Raw, Consignment
from analytics.models import FinancialEntry
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Item,SimpleHistoryAdmin)
admin.site.register(Batch,SimpleHistoryAdmin)
admin.site.register(Raw,SimpleHistoryAdmin)
admin.site.register(FinancialEntry,SimpleHistoryAdmin)
admin.site.register(Consignment)


# استبدل analytics بمجلد الـ App بتاع المالية عندك


# دالة سحرية عشان تظهر "تاريخ" أي موديل في جدول منفصل
def register_with_history(model):
    # 1. تسجيل الموديل الأصلي (لو مش متسجل قبل كدة)
    try:
        admin.site.register(model, SimpleHistoryAdmin)
    except admin.sites.AlreadyRegistered:
        pass

    # 2. الوصول لموديل الهيستوري الخفي
    history_model = model.history.model

    # 3. "إجبار" دجانجو على تغيير الاسم اللي بيظهر في القائمة
    # حطينا مسافة قبل الاسم عشان المسافة بتترتب أبجدياً قبل الحروف، فيظهر تحت الموديل علطول
    history_model._meta.verbose_name_plural = f" {model._meta.verbose_name} History Log"
    history_model._meta.verbose_name = f" {model._meta.verbose_name} History Log"

    @admin.register(history_model)
    class GlobalHistoryAdmin(admin.ModelAdmin):
        list_display = ('history_date', 'history_user', 'history_type', 'history_object')
        list_filter = ('history_user', 'history_type', 'history_date')

        def has_add_permission(self, request): return False

        def has_change_permission(self, request, obj=None): return False

        def has_delete_permission(self, request, obj=None): return False

# طبق الدالة دي على كل الموديلات اللي عايز تراقبها في جدول لوحده
register_with_history(Item)
register_with_history(Batch)
register_with_history(Raw)
register_with_history(FinancialEntry)
