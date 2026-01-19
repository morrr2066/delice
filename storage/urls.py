from django.urls import path
from . import views

urlpatterns = [
    path('storage/', views.storage_view, name='storage'),
    path('storage/items/',views.item_view,name='storage-items'),
    path('storage/batches', views.batch_view, name='storage-batches'),
    path('storage/raws/', views.raw_view, name='storage-raws'),
    path('add-item/',views.add_item,name='add_item'),
    path('add-batch',views.add_batch,name='add_batch'),
    path('add-raw/', views.add_raw, name='add_raw'),
    path('formulas/',views.formulas,name='formulas'),
    path('add-ingredient/<int:item_id>/', views.add_ingredient, name='add_ingredient'),
    path('delete-ingredient/<int:formula_id>/', views.delete_ingredient, name='delete_ingredient'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('delete-batch/<int:batch_id>/', views.delete_batch, name='delete_batch'),
    path('delete-raw/<int:raw_id>/', views.delete_raw, name='delete_raw'),
    path('lab/',views.lab,name='lab'),
    path('storage/add_location/',views.add_location,name='add_location'),
    path('location/delete/<int:location_id>/', views.delete_location, name='delete_location'),
    path('consignment/add/', views.add_consignment, name='add_consignment'),
    path('consignment/settle/<int:consignment_id>/', views.settle_consignment, name='settle_consignment'),
    path('consignment/return/<int:consignment_id>/', views.return_consignment, name='return_consignment'),
]
