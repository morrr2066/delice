from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('inputs/',views.inputs,name='inputs'),
    path('inputs/add_financial_entry/', views.add_financialentry, name='add_financial_entry'),
    path('analytics-table/', views.analytics_table, name='analytics-table'),
    path('delete-entry/<int:entry_id>/', views.delete_financial_entry, name='delete_entry'),
    path('outputs/', views.outputs, name='outputs'),
    path('reports/', views.reports, name='reports'),
    path('shopify/webhook/', views.shopify_webhook, name='shopify_webhook'),
]