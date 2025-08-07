from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
import json

from .models import Service, Invoice, InvoiceItem, Payment, InsuranceClaim
from .forms import (
    ServiceForm, InvoiceForm, InvoiceItemForm, PaymentForm, 
    InsuranceClaimForm, InvoiceFilterForm, PaymentFilterForm, BulkInvoiceForm
)
from patients.models import Patient

@login_required  
def index(request):
    """Dashboard principal de facturación"""
    # Estadísticas generales
    stats = {
        'total_invoices': Invoice.objects.count(),
        'pending_invoices': Invoice.objects.filter(status='sent').count(),
        'overdue_invoices': Invoice.objects.filter(
            status='sent',
            due_date__lt=timezone.now().date()
        ).count(),
        'total_revenue': Invoice.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'pending_payments': Invoice.objects.filter(
            status__in=['sent', 'overdue']
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    
    # Facturas recientes
    recent_invoices = Invoice.objects.select_related('patient').order_by('-created_at')[:10]
    
    # Pagos recientes
    recent_payments = Payment.objects.select_related('invoice__patient').order_by('-payment_date')[:10]
    
    # Facturas vencidas
    overdue_invoices = Invoice.objects.filter(
        status='sent',
        due_date__lt=timezone.now().date()
    ).select_related('patient').order_by('due_date')[:5]
    
    context = {
        'title': 'Dashboard de Facturación',
        'stats': stats,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'overdue_invoices': overdue_invoices,
    }
    
    return render(request, 'billing/index.html', context)

@login_required
def invoices(request):
    """Lista de facturas con filtros"""
    form = InvoiceFilterForm(request.GET or None)
    invoices_list = Invoice.objects.select_related('patient').order_by('-created_at')
    
    # Aplicar filtros
    if form.is_valid():
        if form.cleaned_data.get('patient'):
            invoices_list = invoices_list.filter(patient=form.cleaned_data['patient'])
        if form.cleaned_data.get('status'):
            invoices_list = invoices_list.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            invoices_list = invoices_list.filter(issue_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            invoices_list = invoices_list.filter(issue_date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('overdue_only'):
            invoices_list = invoices_list.filter(
                status='sent',
                due_date__lt=timezone.now().date()
            )
    
    # Paginación
    paginator = Paginator(invoices_list, 20)
    page_number = request.GET.get('page')
    invoices = paginator.get_page(page_number)
    
    context = {
        'title': 'Facturas',
        'invoices': invoices,
        'form': form,
    }
    
    return render(request, 'billing/invoices.html', context)

@login_required
def invoice_detail(request, pk):
    """Detalle de una factura específica"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    context = {
        'title': f'Factura {invoice.invoice_number}',
        'invoice': invoice,
        'items': invoice.items.select_related('service').all(),
        'payments': invoice.payments.order_by('-payment_date'),
        'insurance_claims': invoice.insurance_claims.order_by('-created_at'),
    }
    
    return render(request, 'billing/invoice_detail.html', context)

@login_required
def create_invoice(request):
    """Crear nueva factura"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Factura {invoice.invoice_number} creada exitosamente.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(user=request.user)
    
    context = {
        'title': 'Crear Factura',
        'form': form,
    }
    
    return render(request, 'billing/create_invoice.html', context)

@login_required
def edit_invoice(request, pk):
    """Editar factura existente"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status not in ['draft']:
        messages.error(request, 'Solo se pueden editar facturas en borrador.')
        return redirect('billing:invoice_detail', pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        if form.is_valid():
            invoice = form.save()
            messages.success(request, f'Factura {invoice.invoice_number} actualizada exitosamente.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice, user=request.user)
    
    context = {
        'title': f'Editar Factura {invoice.invoice_number}',
        'form': form,
        'invoice': invoice,
    }
    
    return render(request, 'billing/edit_invoice.html', context)

@login_required
def add_invoice_item(request, invoice_pk):
    """Agregar elemento a factura"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if invoice.status not in ['draft']:
        messages.error(request, 'Solo se pueden agregar elementos a facturas en borrador.')
        return redirect('billing:invoice_detail', pk=invoice_pk)
    
    if request.method == 'POST':
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            
            # Recalcular totales de la factura
            invoice.calculate_totals()
            invoice.save()
            
            messages.success(request, 'Elemento agregado exitosamente.')
            return redirect('billing:invoice_detail', pk=invoice_pk)
    else:
        form = InvoiceItemForm()
    
    context = {
        'title': f'Agregar Elemento - Factura {invoice.invoice_number}',
        'form': form,
        'invoice': invoice,
    }
    
    return render(request, 'billing/add_invoice_item.html', context)

@login_required
def payments(request):
    """Lista de pagos con filtros"""
    form = PaymentFilterForm(request.GET or None)
    payments_list = Payment.objects.select_related('invoice__patient').order_by('-payment_date')
    
    # Aplicar filtros
    if form.is_valid():
        if form.cleaned_data.get('payment_method'):
            payments_list = payments_list.filter(payment_method=form.cleaned_data['payment_method'])
        if form.cleaned_data.get('status'):
            payments_list = payments_list.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('date_from'):
            payments_list = payments_list.filter(payment_date__date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            payments_list = payments_list.filter(payment_date__date__lte=form.cleaned_data['date_to'])
    
    # Paginación
    paginator = Paginator(payments_list, 20)
    page_number = request.GET.get('page')
    payments = paginator.get_page(page_number)
    
    context = {
        'title': 'Pagos',
        'payments': payments,
        'form': form,
    }
    
    return render(request, 'billing/payments.html', context)

@login_required
def create_payment(request, invoice_pk):
    """Crear pago para una factura"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if invoice.amount_pending <= 0:
        messages.error(request, 'Esta factura ya está completamente pagada.')
        return redirect('billing:invoice_detail', pk=invoice_pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice, user=request.user)
        if form.is_valid():
            payment = form.save()
            
            # Actualizar estado de la factura si está completamente pagada
            if invoice.amount_pending <= 0:
                invoice.status = 'paid'
                invoice.save()
            
            messages.success(request, f'Pago {payment.payment_number} registrado exitosamente.')
            return redirect('billing:invoice_detail', pk=invoice_pk)
    else:
        form = PaymentForm(invoice=invoice, user=request.user)
    
    context = {
        'title': f'Registrar Pago - Factura {invoice.invoice_number}',
        'form': form,
        'invoice': invoice,
    }
    
    return render(request, 'billing/create_payment.html', context)

@login_required
def services(request):
    """Lista de servicios"""
    services_list = Service.objects.order_by('category', 'name')
    
    # Búsqueda
    search_query = request.GET.get('search')
    if search_query:
        services_list = services_list.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filtro por categoría
    category_filter = request.GET.get('category')
    if category_filter:
        services_list = services_list.filter(category__icontains=category_filter)
    
    # Filtro por estado
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        services_list = services_list.filter(is_active=True)
    elif status_filter == 'inactive':
        services_list = services_list.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(services_list, 20)
    page_number = request.GET.get('page')
    services = paginator.get_page(page_number)
    
    context = {
        'title': 'Servicios',
        'services': services,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'billing/services.html', context)

@login_required
def create_service(request):
    """Crear nuevo servicio"""
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Servicio "{service.name}" creado exitosamente.')
            return redirect('billing:services')
    else:
        form = ServiceForm()
    
    context = {
        'title': 'Crear Servicio',
        'form': form,
    }
    
    return render(request, 'billing/create_service.html', context)

@login_required
def edit_service(request, pk):
    """Editar servicio existente"""
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Servicio "{service.name}" actualizado exitosamente.')
            return redirect('billing:services')
    else:
        form = ServiceForm(instance=service)
    
    context = {
        'title': f'Editar Servicio: {service.name}',
        'form': form,
        'service': service,
    }
    
    return render(request, 'billing/edit_service.html', context)

@login_required
def create_insurance_claim(request, invoice_pk):
    """Crear reclamo de seguro para una factura"""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = InsuranceClaimForm(request.POST, invoice=invoice, user=request.user)
        if form.is_valid():
            claim = form.save()
            messages.success(request, f'Reclamo {claim.claim_number} creado exitosamente.')
            return redirect('billing:invoice_detail', pk=invoice_pk)
    else:
        form = InsuranceClaimForm(invoice=invoice, user=request.user)
    
    context = {
        'title': f'Crear Reclamo de Seguro - Factura {invoice.invoice_number}',
        'form': form,
        'invoice': invoice,
    }
    
    return render(request, 'billing/create_insurance_claim.html', context)

@login_required
def bulk_invoice(request):
    """Crear facturas en lote"""
    if request.method == 'POST':
        form = BulkInvoiceForm(request.POST)
        if form.is_valid():
            created_count = 0
            service = form.cleaned_data['service']
            
            for patient in form.cleaned_data['patients']:
                # Crear factura
                invoice = Invoice.objects.create(
                    patient=patient,
                    issue_date=form.cleaned_data['issue_date'],
                    payment_terms=form.cleaned_data['payment_terms'],
                    notes=form.cleaned_data['notes'],
                    created_by=request.user
                )
                
                # Agregar elemento de servicio
                InvoiceItem.objects.create(
                    invoice=invoice,
                    service=service,
                    quantity=1,
                    unit_price=service.price,
                    tax_rate=service.tax_rate
                )
                
                # Calcular totales
                invoice.calculate_totals()
                invoice.save()
                
                created_count += 1
            
            messages.success(request, f'{created_count} facturas creadas exitosamente.')
            return redirect('billing:invoices')
    else:
        form = BulkInvoiceForm()
    
    context = {
        'title': 'Crear Facturas en Lote',
        'form': form,
    }
    
    return render(request, 'billing/bulk_invoice.html', context)

# API Views
@login_required
def api_service_price(request, pk):
    """API para obtener precio de un servicio"""
    try:
        service = Service.objects.get(pk=pk, is_active=True)
        return JsonResponse({
            'price': float(service.price),
            'tax_rate': float(service.tax_rate),
            'name': service.name
        })
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Servicio no encontrado'}, status=404)

@login_required
def api_invoice_totals(request, pk):
    """API para obtener totales de una factura"""
    try:
        invoice = Invoice.objects.get(pk=pk)
        totals = invoice.calculate_totals()
        return JsonResponse(totals)
    except Invoice.DoesNotExist:
        return JsonResponse({'error': 'Factura no encontrada'}, status=404)


@login_required
def export_payments(request):
    """Exportar pagos a CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pagos.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Número', 'Factura', 'Paciente', 'Fecha', 'Método', 'Monto', 'Estado'])
    
    payments = Payment.objects.select_related('invoice', 'invoice__patient').all()
    for payment in payments:
        writer.writerow([
            payment.payment_number,
            payment.invoice.invoice_number,
            payment.invoice.patient.get_full_name(),
            payment.payment_date.strftime('%d/%m/%Y %H:%M'),
            payment.get_payment_method_display(),
            f'{payment.amount:.2f}',
            payment.get_status_display()
        ])
    
    return response

