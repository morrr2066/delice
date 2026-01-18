from django.contrib.auth.decorators import permission_required
from django.shortcuts import render , redirect, get_object_or_404
from .models import Item,Batch,Raw,Formula
from django.http import HttpResponse
from analytics.models import Location


def storage_view(request):
    return render(request, 'storage/storage.html')

@permission_required('storage.view_item', raise_exception=True)
def item_view(request):
    items = Item.objects.all()
    return render(request,'storage/items.html',{"items":items})

@permission_required('storage.view_batch', raise_exception=True)
def batch_view(request):
    batches = Batch.objects.all()
    items = Item.objects.all()
    return render(request,'storage/batches.html',{"batches":batches , "items":items})

@permission_required('storage.view_raw', raise_exception=True)
def raw_view(request):
    raws = Raw.objects.all()
    return render(request,'storage/raws.html',{"raws":raws})


@permission_required('storage.add_item', raise_exception=True)
def add_item(request):
       if request.method=="POST":
        name=request.POST.get("name")
        price=request.POST.get("price")
        details=request.POST.get("details","")
        try:
            Item.objects.create(name=name,price=price,details=details)
            msg = f"Item {name} created successfully!"
        except:
            msg = f"Item {name} already exists"
        return HttpResponse(msg)

@permission_required('storage.add_batch', raise_exception=True)
def add_batch(request):
    if request.method=='POST':
        item_id = request.POST.get("item")  # ده string
        item = Item.objects.get(id=item_id)  # كده بقى object
        quantity = int(request.POST.get("batch_quantity"))
        production_date = request.POST.get("production_date")
        expiry_date = request.POST.get("expiry_date")
        cost = request.POST.get("cost")
        details = request.POST.get("details")


        try:
            batch = Batch(item=item,quantity=quantity,production_date=production_date,expiry_date=expiry_date,cost=cost,details=details)
            batch.save(user=request.user)
            msg = f"{item} Batch created successfully!"
        except Exception as e:
            msg = "Unexpected error occurred!"
            print(e)

        return HttpResponse(msg)

    return redirect('storage')

@permission_required('storage.add_raw', raise_exception=True)
def add_raw(request):
    if request.method == "POST":
        state = request.POST.get("state")
        name = request.POST.get("name")
        unit = request.POST.get("unit")
        cost = request.POST.get("cost")
        details = request.POST.get("details", "")
        try:
            Raw.objects.create(state=state,name=name,unit=unit,cost=cost,details=details)
            msg = f" {name} created successfully!"
        except Exception as e:
            msg = f" {name} already exists"
            print(e)
        return HttpResponse(msg)

@permission_required('storage.view_formula', raise_exception=True)
def formulas(request):
    items = Item.objects.all()
    raw_materials = Raw.objects.all()

    selected_item_id = request.GET.get('item_id')
    selected_item = None
    formula_details = None

    if selected_item_id:
        selected_item = Item.objects.get(id=selected_item_id)
        formula_details = Formula.objects.filter(item=selected_item)
    return render(request , 'storage/formulas.html',{
        'items':items ,
        'raw_materials':raw_materials ,
        'selected_item':selected_item ,
        'formula_details':formula_details ,
    })

@permission_required('storage.add_formula', raise_exception=True)
def add_ingredient(request,item_id):
    item = Item.objects.get(id=item_id)
    all_raw_materials = Raw.objects.all()

    if request.method == "POST":
        raw_id = request.POST.get('raw_material_id')
        qty = request.POST.get('quantity')
        try:
            Formula.objects.create(item=item,raw_material_id=raw_id,quantity_needed=qty)
        except Exception as e:
            print(e)
        return redirect(f'/storage/formulas/?item_id={item.id}')

    return render(request, 'storage/add_ingredient.html', {
        'item': item,
        'all_raw_materials': all_raw_materials
    })

@permission_required('storage.delete_formula', raise_exception=True)
def delete_ingredient(request, formula_id):
    # بنجيب السطر اللي اليوزر داس عليه
    entry = Formula.objects.get(id=formula_id)
    item_id = entry.item.id  # بنحفظ رقم المنتج عشان نرجعله تاني

    entry.delete()  # المسح الفعلي

    # الرجوع لنفس الصفحة بنفس الـ ID عشان الجدول يفضل مفتوح
    return redirect(f'/storage/formulas/?item_id={item_id}')

@permission_required('storage.delete_item', raise_exception=True)
def delete_item(request, item_id):
    # بنجيب السطر اللي اليوزر داس عليه
    item_action = Item.objects.get(id=item_id)

    item_action.delete()  # المسح الفعلي

    # الرجوع لنفس الصفحة بنفس الـ ID عشان الجدول يفضل مفتوح
    return redirect(f'/storage/storage/?item_id={item_id}')

@permission_required('storage.delete_batch', raise_exception=True)
def delete_batch(request, batch_id):
    # بنجيب السطر اللي اليوزر داس عليه
    batch_action = Batch.objects.get(id=batch_id)

    item = batch_action.item
    item.quantity -= batch_action.quantity
    item.save()

    batch_action.delete()

    # الرجوع لنفس الصفحة بنفس الـ ID عشان الجدول يفضل مفتوح
    return redirect(f'/storage/storage/?item_id={batch_id}')

@permission_required('storage.delete_raw', raise_exception=True)
def delete_raw(request, raw_id):
    # بنجيب السطر اللي اليوزر داس عليه
    raw_action = Raw.objects.get(id=raw_id)

    raw_action.delete()  # المسح الفعلي

    # الرجوع لنفس الصفحة بنفس الـ ID عشان الجدول يفضل مفتوح
    return redirect(f'/storage/storage/?item_id={raw_id}')

def lab(request):
    return render(request,'storage/lab.html')

def add_location(request):
    locations = Location.objects.all()
    if request.method == "POST":
        name = request.POST.get('location_name')
        if name:
            try:
                Location.objects.create(name=name)
                msg = f"Location {name} created successfully!"
                return HttpResponse(msg)
            except Exception as e:
                print(e)
                msg = f"Error {e} occurred"
                return HttpResponse(msg)
    return render(request, 'storage/add_location.html',{'locations':locations})


def delete_location(request, location_id):
    # بنجيب اللوكيشن أو نرجع 404 لو مش موجود
    location = get_object_or_404(Location, id=location_id)
    name = location.name

    try:
        location.delete()
        return HttpResponse(f"Location '{name}' deleted successfully!")
    except Exception as e:
        return HttpResponse(f"Error: Cannot delete location because it might be linked to other data. ({e})")

