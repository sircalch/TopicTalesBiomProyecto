from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Service, Invoice, InvoiceItem, Payment, InsuranceClaim

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'price', 'tax_rate', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'code', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'code', 'category')
        }),
        ('Precios', {
            'fields': ('price', 'tax_rate')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['subtotal_display', 'tax_amount_display', 'total_display']
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal:.2f}" if obj.subtotal else "$0.00"
    subtotal_display.short_description = "Subtotal"
    
    def tax_amount_display(self, obj):
        return f"${obj.tax_amount:.2f}" if obj.tax_amount else "$0.00"
    tax_amount_display.short_description = "Impuestos"
    
    def total_display(self, obj):
        return f"${obj.total:.2f}" if obj.total else "$0.00"
    total_display.short_description = "Total"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'patient', 'status', 'total_amount', 
        'issue_date', 'due_date', 'is_overdue_display', 'created_by'
    ]
    list_filter = ['status', 'payment_terms', 'issue_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name', 'notes']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at', 'amount_paid_display', 'amount_pending_display']
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('invoice_number', 'patient', 'appointment', 'status')
        }),
        ('Fechas', {
            'fields': ('issue_date', 'due_date', 'payment_terms')
        }),
        ('Totales', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount', 
                      'amount_paid_display', 'amount_pending_display')
        }),
        ('Información Adicional', {
            'fields': ('notes', 'terms_conditions'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            days = obj.days_overdue
            return format_html(
                '<span style="color: red; font-weight: bold;">Vencida ({} días)</span>',
                days
            )
        elif obj.status == 'paid':
            return format_html('<span style="color: green;">Pagada</span>')
        else:
            return format_html('<span style="color: orange;">Al día</span>')
    
    is_overdue_display.short_description = "Estado de Vencimiento"
    is_overdue_display.admin_order_field = 'due_date'
    
    def amount_paid_display(self, obj):
        return f"${obj.amount_paid:.2f}"
    amount_paid_display.short_description = "Monto Pagado"
    
    def amount_pending_display(self, obj):
        return f"${obj.amount_pending:.2f}"
    amount_pending_display.short_description = "Monto Pendiente"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'created_by', 'appointment')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_number', 'invoice_link', 'amount', 'payment_method',
        'status', 'payment_date', 'processed_by'
    ]
    list_filter = ['payment_method', 'status', 'payment_date', 'created_at']
    search_fields = [
        'payment_number', 'invoice__invoice_number', 'invoice__patient__first_name',
        'invoice__patient__last_name', 'reference_number'
    ]
    readonly_fields = ['payment_number', 'created_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('payment_number', 'invoice', 'amount', 'payment_date')
        }),
        ('Método de Pago', {
            'fields': ('payment_method', 'status', 'reference_number', 'bank_name', 'check_number')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('processed_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_link(self, obj):
        url = reverse('admin:billing_invoice_change', args=[obj.invoice.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.invoice.invoice_number
        )
    invoice_link.short_description = "Factura"
    invoice_link.admin_order_field = 'invoice__invoice_number'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'invoice__patient', 'processed_by'
        )

@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = [
        'claim_number', 'invoice_link', 'insurance_company', 'claim_amount',
        'approved_amount', 'status', 'submission_date', 'created_by'
    ]
    list_filter = ['status', 'submission_date', 'response_date', 'created_at']
    search_fields = [
        'claim_number', 'insurance_company', 'policy_number',
        'invoice__invoice_number', 'invoice__patient__first_name',
        'invoice__patient__last_name'
    ]
    readonly_fields = ['claim_number', 'created_at', 'updated_at']
    date_hierarchy = 'submission_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('claim_number', 'invoice', 'insurance_company', 'policy_number')
        }),
        ('Montos', {
            'fields': ('claim_amount', 'approved_amount')
        }),
        ('Estado y Fechas', {
            'fields': ('status', 'submission_date', 'response_date', 'payment_date')
        }),
        ('Notas', {
            'fields': ('notes', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_link(self, obj):
        url = reverse('admin:billing_invoice_change', args=[obj.invoice.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.invoice.invoice_number
        )
    invoice_link.short_description = "Factura"
    invoice_link.admin_order_field = 'invoice__invoice_number'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'invoice__patient', 'created_by'
        )
