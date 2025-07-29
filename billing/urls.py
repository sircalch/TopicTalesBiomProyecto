from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.index, name='index'),
    path('invoices/', views.invoices, name='invoices'),
    path('payments/', views.payments, name='payments'),
    path('create-invoice/', views.create_invoice, name='create_invoice'),
]