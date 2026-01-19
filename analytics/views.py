import time
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from analytics.models import FinancialEntry,Location
from storage.models import Item
from django.db.models import Sum, F
from datetime import datetime
from django.contrib.auth.models import User

# Create your views here.
def analytics_view(request):
    return render(request,'analytics/analytics.html')

def inputs(request):
    return render(request,'analytics/inputs.html')

def outputs(request):
    return render(request,'analytics/outputs.html')


def add_financialentry(request):
    items = Item.objects.all()
    locations = Location.objects.all()
    if request.method=="POST":
        source = request.POST.get('source')
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        location_id = request.POST.get('location_id')
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
                location_id=location_id,
                notes=notes,
                added_by=request.user
            )
            msg = "Entry added successfully!"
            return HttpResponse(msg)

        except Exception as e:
            print(e)
            return HttpResponse(f"الخطأ هو: {e}")

    return render(request,'analytics/inputs.html',{'items':items,'locations':locations})

def analytics_table(request):
    entries = FinancialEntry.objects.all().order_by('-id')  # الجديد من فوق
    return render(request,'analytics/analytics-table.html',{'entries':entries})

def delete_financial_entry(request, entry_id):
    entry = FinancialEntry.objects.get(id=entry_id)
    entry.delete()
    return redirect('analytics') # أو الاسم اللي انت مثبته للـ URL


def outputs(request):
    locations = Location.objects.all()
    if request.method=="POST":
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        location = request.POST.get('location_id')
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

    return render(request,'analytics/outputs.html',{'locations':locations})





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


@csrf_exempt
def shopify_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            bot_user = User.objects.filter(username='Shopify API').first()
            # 1. سحب البيانات اللي محتاجينها للـ Financial Entry
            amount = data.get('total_price')
            order_number = data.get('order_number')
            # شوبيفاي بيبعت التاريخ كدة: 2026-01-19T18:28:11+02:00
            # هناخد أول 10 حروف بس عشان الـ DateField (YYYY-MM-DD)
            raw_date = data.get('created_at')
            order_date = raw_date[:10] if raw_date else datetime.now().date()

            # 2. تسجيل العملية المالية
            FinancialEntry.objects.create(
                date=order_date,
                entry_type='INCOME',  # طبعاً أوردر شوبيفاي يعني إيراد
                source='Shopify',  # المصدر ثابت عشان نعرف ده جاي منين
                amount=amount,
                item_name=f"Order #{order_number}",
                notes=f"Automated entry By Shopify",
                added_by=bot_user,
                location=Location.objects.get(name='Online'),
            )

            print(f"✅ Financial Entry Created for Order #{order_number}")
            return HttpResponse(status=200)

        except Exception as e:
            print(f"❌ Error: {e}")
            return HttpResponse(status=400)

    return HttpResponse(status=405)
