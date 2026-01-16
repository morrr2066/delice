from django.db import models
from simple_history.models import HistoricalRecords
from analytics.models import FinancialEntry
from django.utils import timezone

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True,blank=False)
    details = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(max_length=10,blank=True)
    SKU = models.CharField(max_length=4,unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}"

    def save(self,*args,**kwargs):
        if not self.SKU:
            last_item = Item.objects.order_by('-id').first()
            if last_item:
                self.SKU = str(int(last_item.SKU)+1).zfill(4)
            else:
                self.SKU = "0001"
        super().save(*args,**kwargs)

    @property
    def total_cost(self):
        item_formula = self.formula_set.all()
        total = sum(x.quantity_needed * x.raw_material.cost for x in item_formula)
        return total



class Batch(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='batches')
    quantity = models.IntegerField()
    batch_no = models.CharField(max_length=8,unique=True)
    production_date = models.DateField(blank=False)
    expiry_date = models.DateField(blank=False)
    cost = models.PositiveIntegerField(blank=True)
    details = models.TextField(blank=True)
    history = HistoricalRecords(verbose_name="z_Batch History")

    def __str__(self):
        return f"{self.item} - {self.batch_no}"

    def save(self, user=None, *args, **kwargs):
        # 1. توليد رقم الباتش وتحديث كمية الصنف (بما إنه جديد دايماً)
        last_batch = Batch.objects.order_by('-id').first()
        if last_batch:
            self.batch_no = str(int(last_batch.batch_no) + 1).zfill(8)
        else:
            self.batch_no = "00000001"

        # زيادة الكمية في جدول الـ Item
        self.item.quantity += self.quantity
        self.item.save()

        # 2. حفظ الباتش نفسه في الداتابيز
        super().save(*args, **kwargs)

        # 3. تسجيل "المصروف" في المالية فوراً
        from .models import FinancialEntry
        FinancialEntry.objects.create(
            date=timezone.now().date(),
            entry_type='EXPENSE',
            source=f"Batch: {self.batch_no}",
            amount=self.cost,
            quantity=self.quantity,
            item_name=self.item.name,
            location='BATCH',
            notes='No notes',
            added_by=user  # الـ user اللي جايلنا "معدية" من الـ View
        )

    @property
    def item_cost_inbatch(self):
        if self.quantity and self.quantity > 0:
            return round(self.cost / self.quantity, 2)
        else:
            return 0

    @property
    def item_price(self):
        return self.item.price


from django.db import models

class Raw(models.Model):
    state = models.CharField(max_length=50,blank=False)
    name = models.CharField(max_length=300,unique=True,blank=False)
    unit = models.CharField(max_length=100,blank=False)
    cost = models.FloatField(max_length=50,blank=False)
    details = models.CharField(max_length=500,blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name}"


class Formula(models.Model):
    # أول حاجة: بنقول للسطر ده "أنت تبع أنهي منتج؟"
    # الـ ForeignKey هنا معناها إننا بنشاور على الـ Item
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    # تاني حاجة: بنقول للسطر ده "أنت هتاخد أنهي خامة من المخزن؟"
    # هنا بنشاور على الـ Raw
    raw_material = models.ForeignKey(Raw, on_delete=models.PROTECT)

    # تالت حاجة: "هتاخد كمية قد إيه من الخامة دي؟"
    quantity_needed = models.FloatField()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.item} Formula"

    @property
    def item_cost(self):
        return self.quantity_needed * self.raw_material.cost

