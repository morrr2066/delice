import base64
import hashlib
import hmac
import json
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from analytics.models import FinancialEntry, Location
from storage.models import Item

# Create your views here.
def analytics_view(request):
    return render(request,'analytics/analytics.html')

def inputs(request):
    items=Item.objects.all()
    locations=Location.objects.all()
    return render(request,'analytics/inputs.html',{'items':items,'locations':locations})

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
            qty_int = int(quantity)
            if qty_int <= 0:
                return HttpResponse("Quantity must be > 0", status=400)

            unit_price = Decimal(price)
            amount = unit_price * qty_int

            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=item_id)
                if item.quantity < qty_int:
                    return HttpResponse("Not enough stock", status=400)

                item.quantity -= qty_int
                item.save(update_fields=["quantity"])

                FinancialEntry.objects.create(
                    date=timezone.now().date(),
                    entry_type='INCOME',
                    source=source or "Manual sale",
                    amount=amount,
                    quantity=qty_int,
                    item_name=item.name,
                    location_id=location_id or None,
                    notes=notes,
                    added_by=request.user
                )
            msg = "Entry added successfully!"
            return HttpResponse(msg)

        except (Item.DoesNotExist, ValueError, InvalidOperation) as e:
            print(e)
            return HttpResponse("Invalid input", status=400)
        except Exception as e:
            print(e)
            return HttpResponse("Unexpected error", status=500)

    return render(request,'analytics/inputs.html',{'items':items,'locations':locations})

def analytics_table(request):
    entries = FinancialEntry.objects.all().order_by('-id')  # الجديد من فوق
    return render(request,'analytics/analytics-table.html',{'entries':entries})

def delete_financial_entry(request, entry_id):
    entry = get_object_or_404(FinancialEntry, id=entry_id)
    entry.delete()
    return redirect('analytics') # أو الاسم اللي انت مثبته للـ URL


def outputs(request):
    locations = Location.objects.all()
    if request.method=="POST":
        amount = request.POST.get('amount')
        source = request.POST.get('source')
        location_id = request.POST.get('location_id')
        notes = request.POST.get('notes',"")
        try:
            amount_dec = Decimal(amount)
            FinancialEntry.objects.create(
                date=timezone.now().date(),
                entry_type='EXPENSE',
                source=source or "Manual expense",
                amount=amount_dec,
                location_id=location_id or None,
                notes=notes,
                added_by=request.user
            )
            msg = "Entry added successfully!"
            return HttpResponse(msg)
        except (InvalidOperation,) as e:
            print(e)
            return HttpResponse("Invalid amount", status=400)
        except Exception as e:
            print(e)
            return HttpResponse("Unexpected error", status=500)

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
    if request.method == 'GET':
        # Simple health-check endpoint so you can quickly verify the URL is reachable.
        return HttpResponse("OK", status=200)

    if request.method == 'POST':
        try:
            print("📩 Shopify webhook received")
            
            # HMAC verification (optional for testing, but recommended for production)
            webhook_secret = os.getenv("SHOPIFY_WEBHOOK_SECRET")
            their_hmac = request.headers.get("X-Shopify-Hmac-Sha256", "")
            
            if webhook_secret and their_hmac:
                # Verify HMAC if secret is configured
                digest = hmac.new(webhook_secret.encode("utf-8"), request.body, hashlib.sha256).digest()
                our_hmac = base64.b64encode(digest).decode("utf-8")
                if not hmac.compare_digest(our_hmac, their_hmac):
                    print("❌ Shopify webhook HMAC mismatch - webhook rejected")
                    return HttpResponse(status=401)
                print("✅ HMAC verification passed")
            else:
                # Skip HMAC verification if secret not set (for testing only)
                if not webhook_secret:
                    print("⚠️  WARNING: SHOPIFY_WEBHOOK_SECRET not set - skipping HMAC verification (INSECURE!)")
                else:
                    print("⚠️  WARNING: No HMAC header received - skipping verification")

            data = json.loads(request.body)
            print(f"📦 Webhook data keys: {list(data.keys())}")
            
            bot_user, _ = User.objects.get_or_create(username='Shopify API')

            amount_raw = data.get('total_price')
            order_number = data.get('order_number') or data.get('number') or 'Unknown'
            print(f"💰 Order #{order_number}, Amount: {amount_raw}")
            
            # شوبيفاي بيبعت التاريخ كدة: 2026-01-19T18:28:11+02:00
            # هناخد أول 10 حروف بس عشان الـ DateField (YYYY-MM-DD)
            raw_date = data.get('created_at')
            order_date = date.fromisoformat(raw_date[:10]) if raw_date else timezone.now().date()

            amount = Decimal(str(amount_raw or "0"))
            online_loc, _ = Location.objects.get_or_create(name='Online')

            # 2. تسجيل العملية المالية
            FinancialEntry.objects.create(
                date=order_date,
                entry_type='INCOME',  # طبعاً أوردر شوبيفاي يعني إيراد
                source='Shopify',  # المصدر ثابت عشان نعرف ده جاي منين
                amount=amount,
                item_name=f"Order #{order_number}",
                notes=f"Automated entry By Shopify",
                added_by=bot_user,
                location=online_loc,
            )

            print(f"✅ Financial Entry Created for Order #{order_number} - Amount: {amount}")
            return HttpResponse(status=200)

        except (json.JSONDecodeError, InvalidOperation, ValueError) as e:
            print(f"❌ Error: {e}")
            return HttpResponse(status=400)
        except Exception as e:
            print(f"❌ Error: {e}")
            return HttpResponse(status=400)

    return HttpResponse(status=405)
