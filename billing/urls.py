from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),
    
    # Gestión de facturas
    path('invoices/', views.invoices, name='invoices'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/<int:pk>/edit/', views.edit_invoice, name='edit_invoice'),
    path('invoices/<int:invoice_pk>/add-item/', views.add_invoice_item, name='add_invoice_item'),
    path('invoices/bulk-create/', views.bulk_invoice, name='bulk_invoice'),
    
    # Gestión de pagos
    path('payments/', views.payments, name='payments'),
    path('payments/export/', views.export_payments, name='export_payments'),
    path('invoices/<int:invoice_pk>/create-payment/', views.create_payment, name='create_payment'),
    
    # Gestión de servicios
    path('services/', views.services, name='services'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/<int:pk>/edit/', views.edit_service, name='edit_service'),
    
    # Reclamos de seguros
    path('invoices/<int:invoice_pk>/create-claim/', views.create_insurance_claim, name='create_insurance_claim'),
    
    # API endpoints
    path('api/services/<int:pk>/price/', views.api_service_price, name='api_service_price'),
    path('api/invoices/<int:pk>/totals/', views.api_invoice_totals, name='api_invoice_totals'),
]