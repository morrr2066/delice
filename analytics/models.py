from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class FinancialEntry(models.Model):

    TYPES = [('INCOME','Income'),('EXPENSE','Expense')]


    #  الخانات الأساسية (موجودة في كل الحالات)

    # 1. التاريخ
    date = models.DateField()
    # 2. نوع الحركة (مصروف ولا إيراد)
    entry_type = models.CharField(max_length=10,choices=TYPES)
    # 3. المصدر (Rent, Shopify, Meta Ads, etc.)
    source = models.CharField(max_length=100)
    # 4. خانة الفلوس
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # 5. خانة عدد القطع (اختيارية - تملأ في حالة البيع او إرتجاع)
    quantity = models.PositiveIntegerField(null=True,blank=True)

    # 6. تفاصيل إضافية (اختياري - اسم المنتج أو ملاحظات)
    item_name = models.CharField(max_length=100, null=True, blank=True)

    location = models.CharField(max_length=200,null=True,blank=True)

    notes = models.TextField(null=True, blank=True)

    # 7. مين اللي عمل الأكشن ودوره
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='financial_actions')




    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # مسحنا كل الأكواد اللي بتسحب الجروب والـ role
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} ({self.amount})"

#                       date     type     source     amount     quantity     item-name    location     notes    (automated) x[not needed]

# owner           :    (date)    type    (source)  x[amount]  x[quantity]  x[item-name]  x[location] x[notes]

#staff            :    (date)    type    (source)  x[amount]  x[quantity]  x[item-name]  x[location] x[notes]

#stock controller :    (date)   (type)   (source)   (amount)    quantity     item-name    location   x[notes]

#medical rep      :    (date)   (type)   (source)   (amount)    quantity     item-name    location   x[notes]

#shopify          :    (date)   (type)   (source)   (amount)   (quantity)   (item-name)  (location)   (notes)

#meta             :    (date)   (type)   (source)   (amount)   (quantity)   (item-name)  (location)   (notes)

#----------------------------------------------------------------------------------------------------------------------------------------------

# owner           :    (date)    type      (owner)  x[amount]    x[quantity]  x[item-name]  x[location]  x[notes]

#staff            :    (date)    type      (staff)  x[amount]    x[quantity]  x[item-name]  x[location]  x[notes]

#stock controller :    (date)   (income)     (sc)    (qty*item)    quantity     item-name     location   x[notes]

#medical rep      :    (date)   (income)    (mrep)   (qty*item)    quantity     item-name     location   x[notes]

#shopify          :    (date)   (income)   (shopify)   (amount)   (quantity)   (item-name)    (online)    (notes)

#meta             :    (date)   (expense)   (meta)   x[amount]    (quantity)   x[item-name]   (online)    (notes)
