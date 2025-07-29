from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required  
def index(request):
    return render(request, 'billing/index.html', {'title': 'Facturación'})

@login_required
def invoices(request):
    return render(request, 'billing/invoices.html', {'title': 'Facturas'})

@login_required
def payments(request):
    return render(request, 'billing/payments.html', {'title': 'Pagos'})

@login_required
def create_invoice(request):
    return render(request, 'billing/create_invoice.html', {'title': 'Crear Factura'})

