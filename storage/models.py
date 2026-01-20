from django.db import models
from simple_history.models import HistoricalRecords
from analytics.models import FinancialEntry,Location
from django.utils import timezone
from django.db import transaction

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True,blank=False)
    details = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
    cost = models.PositiveIntegerField(default=0)
    details = models.TextField(blank=True)
    history = HistoricalRecords(verbose_name="z_Batch History")

    def __str__(self):
        return f"{self.item} - {self.batch_no}"

    def save(self, user=None, *args, **kwargs):
        creating = self.pk is None

        with transaction.atomic():
            if creating and not self.batch_no:
                last_batch = Batch.objects.select_for_update().order_by('-id').first()
                if last_batch and last_batch.batch_no.isdigit():
                    self.batch_no = str(int(last_batch.batch_no) + 1).zfill(8)
                else:
                    self.batch_no = "00000001"

            if creating:
                item = Item.objects.select_for_update().get(pk=self.item_id)
                item.quantity += int(self.quantity or 0)
                item.save(update_fields=["quantity"])

            super().save(*args, **kwargs)

            if creating:
                default_loc, _ = Location.objects.get_or_create(name="BATCH")
                FinancialEntry.objects.create(
                    date=timezone.now().date(),
                    entry_type='EXPENSE',
                    source=f"Batch: {self.batch_no}",
                    amount=self.cost,
                    quantity=self.quantity,
                    item_name=self.item.name,
                    location=default_loc,
                    notes='No notes',
                    added_by=user
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


class Raw(models.Model):
    state = models.CharField(max_length=50,blank=False)
    name = models.CharField(max_length=300,unique=True,blank=False)
    unit = models.CharField(max_length=100,blank=False)
    cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
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


class Consignment(models.Model):
    # ربط بالصنف وباللوكيشن (التاجر)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # الكميات
    total_quantity = models.PositiveIntegerField(default=0, help_text="الكمية الكلية اللي استلمها")
    sold_quantity = models.PositiveIntegerField(default=0, help_text="الكمية اللي باعها وسددها")

    # السعر
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="سعر القطعة المتفق عليه")

    # التواريخ
    start_date = models.DateField(auto_now_add=True)
    last_settlement_date = models.DateField(null=True, blank=True)

    @property
    def remaining_quantity(self):
        # خانة "وهمية" بتحسب الفرق بين اللي خده واللي باعه أوتوماتيك
        return self.total_quantity - self.sold_quantity

    def __str__(self):
        return f"{self.item.name} at {self.location.name}"
