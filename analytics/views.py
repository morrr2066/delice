import time
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from analytics.models import FinancialEntry
from storage.models import Item


# Create your views here.
def analytics_view(request):
    return render(request,'analytics/analytics.html')

def inputs(request):
    return render(request,'analytics/inputs.html')

def outputs(request):
    return render(request,'analytics/outputs.html')


def add_financialentry(request):
    items = Item.objects.all()
    if request.method=="POST":
        source = request.POST.get('source')
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        location = request.POST.get('location')
        notes = request.POST.get('notes',"")
        try:
            item = Item.objects.get(id=item_id)
            amount = float(price) * int(quantity)
            item.quantity -= int(quantity)
            item.save()

            FinancialEntry.objects.create(
                date=timezone.now().date(),
                entry_type='INCOME',
                source=source,
                amount = amount,
                quantity=quantity,
                item_name=item.name,
                location=location,
                notes=notes,
                added_by=request.user
            )
            msg = "Entry added successfully!"
            return HttpResponse(msg)

        except Exception as e:
            print(e)
            return HttpResponse(f"الخطأ هو: {e}")

    return render(request,'analytics/inputs.html',{'items':items})

def analytics_table(request):
    entries = FinancialEntry.objects.all().order_by('-id')  # الجديد من فوق
    return render(request,'analytics/analytics-table.html',{'entries':entries})

def delete_financial_entry(request, entry_id):
    entry = FinancialEntry.objects.get(id=entry_id)
    entry.delete()
    return redirect('analytics') # أو الاسم اللي انت مثبته للـ URL


def outputs(request):
    if request.method=="POST":
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        location = request.POST.get('location')
        notes = request.POST.get('notes',"")
        try:
            FinancialEntry.objects.create(
                date=timezone.now().date(),
                entry_type='EXPENSE',
                source=source,
                amount = amount,
                location=location,
                notes=notes,
                added_by=request.user
            )
            msg = "Entry added successfully!"
            return HttpResponse(msg)
        except Exception as e:
            print(e)
            return HttpResponse(f"الخطأ هو: {e}")

    return render(request,'analytics/outputs.html')



from django.db.models import Sum, F


def reports(request):
    items = Item.objects.all()

    # الحسبة دي بتضرب الكمية في السعر لكل صف وتجمعهم كلهم في خبطة واحدة
    total_value = items.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0  # الـ or 0 عشان لو الجدول فاضي ميرجعش None

    return render(request, 'analytics/reports.html', {
        'items': items,
        'total_stock_value': total_value
    })
