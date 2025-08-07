from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from patients.models import Patient
from appointments.models import Appointment

User = get_user_model()

class Service(models.Model):
    """Servicios que se pueden facturar"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Tasa de Impuesto (%)")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    category = models.CharField(max_length=100, blank=True, verbose_name="Categoría")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def price_with_tax(self):
        """Precio incluyendo impuestos"""
        tax_amount = self.price * (self.tax_rate / 100)
        return self.price + tax_amount

class Invoice(models.Model):
    """Facturas emitidas"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ]
    
    PAYMENT_TERMS_CHOICES = [
        ('immediate', 'Inmediato'),
        ('15_days', '15 días'),
        ('30_days', '30 días'),
        ('60_days', '60 días'),
        ('90_days', '90 días'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Factura")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cita")
    
    issue_date = models.DateField(default=timezone.now, verbose_name="Fecha de Emisión")
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='30_days', verbose_name="Términos de Pago")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    
    # Subtotales y totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Impuestos")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Descuento")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total")
    
    # Información adicional
    notes = models.TextField(blank=True, verbose_name="Notas")
    terms_conditions = models.TextField(blank=True, verbose_name="Términos y Condiciones")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Factura {self.invoice_number} - {self.patient.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calcular fecha de vencimiento según términos de pago
        if not self.due_date:
            self.due_date = self.calculate_due_date()
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Genera número de factura automático"""
        year = timezone.now().year
        count = Invoice.objects.filter(created_at__year=year).count() + 1
        return f"INV-{year}-{count:05d}"
    
    def calculate_due_date(self):
        """Calcula fecha de vencimiento según términos de pago"""
        from datetime import timedelta
        
        days_map = {
            'immediate': 0,
            '15_days': 15,
            '30_days': 30,
            '60_days': 60,
            '90_days': 90,
        }
        
        days = days_map.get(self.payment_terms, 30)
        return self.issue_date + timedelta(days=days)
    
    def calculate_totals(self):
        """Calcula los totales de la factura"""
        items = self.items.all()
        subtotal = sum(item.total for item in items)
        tax_amount = sum(item.tax_amount for item in items)
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total_amount = subtotal + tax_amount - self.discount_amount
        
        return {
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount
        }
    
    @property
    def is_overdue(self):
        """Verifica si la factura está vencida"""
        return self.status in ['sent'] and timezone.now().date() > self.due_date
    
    @property
    def days_overdue(self):
        """Días de retraso"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def amount_paid(self):
        """Total pagado"""
        return sum(payment.amount for payment in self.payments.filter(status='completed'))
    
    @property
    def amount_pending(self):
        """Monto pendiente de pago"""
        return self.total_amount - self.amount_paid

class InvoiceItem(models.Model):
    """Elementos/líneas de una factura"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name="Factura")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1.00, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Tasa de Impuesto (%)")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Descuento (%)")
    
    class Meta:
        verbose_name = "Elemento de Factura"
        verbose_name_plural = "Elementos de Factura"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.service.name} - {self.invoice.invoice_number}"
    
    @property
    def subtotal(self):
        """Subtotal antes de impuestos y descuentos"""
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self):
        """Monto del descuento"""
        return self.subtotal * (self.discount_rate / 100)
    
    @property
    def taxable_amount(self):
        """Monto sobre el que se calculan impuestos"""
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self):
        """Monto de impuestos"""
        return self.taxable_amount * (self.tax_rate / 100)
    
    @property
    def total(self):
        """Total del elemento"""
        return self.taxable_amount + self.tax_amount

class Payment(models.Model):
    """Pagos recibidos"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta de Crédito/Débito'),
        ('transfer', 'Transferencia Bancaria'),
        ('check', 'Cheque'),
        ('insurance', 'Seguro Médico'),
        ('other', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', verbose_name="Factura")
    payment_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Pago")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Pago")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Método de Pago")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Información adicional según método de pago
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Número de Referencia")
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Banco")
    check_number = models.CharField(max_length=50, blank=True, verbose_name="Número de Cheque")
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Procesado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Pago {self.payment_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            self.payment_number = self.generate_payment_number()
        super().save(*args, **kwargs)
    
    def generate_payment_number(self):
        """Genera número de pago automático"""
        year = timezone.now().year
        count = Payment.objects.filter(created_at__year=year).count() + 1
        return f"PAY-{year}-{count:05d}"

class InsuranceClaim(models.Model):
    """Reclamos a seguros médicos"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviado'),
        ('under_review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('paid', 'Pagado'),
    ]
    
    claim_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Reclamo")
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='insurance_claims', verbose_name="Factura")
    insurance_company = models.CharField(max_length=200, verbose_name="Compañía de Seguros")
    policy_number = models.CharField(max_length=100, verbose_name="Número de Póliza")
    
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto del Reclamo")
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Aprobado")
    
    submission_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Envío")
    response_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Respuesta")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Notas")
    rejection_reason = models.TextField(blank=True, verbose_name="Razón de Rechazo")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Reclamo de Seguro"
        verbose_name_plural = "Reclamos de Seguros"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reclamo {self.claim_number} - {self.insurance_company}"
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            self.claim_number = self.generate_claim_number()
        super().save(*args, **kwargs)
    
    def generate_claim_number(self):
        """Genera número de reclamo automático"""
        year = timezone.now().year
        count = InsuranceClaim.objects.filter(created_at__year=year).count() + 1
        return f"CLM-{year}-{count:05d}"
