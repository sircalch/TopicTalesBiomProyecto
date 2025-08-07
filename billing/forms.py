from django import forms
from django.contrib.auth import get_user_model
from .models import Service, Invoice, InvoiceItem, Payment, InsuranceClaim
from patients.models import Patient
from appointments.models import Appointment
from datetime import date, timedelta

User = get_user_model()

class ServiceForm(forms.ModelForm):
    """Formulario para crear/editar servicios"""
    class Meta:
        model = Service
        fields = ['name', 'description', 'code', 'price', 'tax_rate', 'category', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del servicio'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del servicio'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único del servicio'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Categoría del servicio'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            if Service.objects.filter(code=code).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("Ya existe un servicio con este código.")
        return code

class InvoiceForm(forms.ModelForm):
    """Formulario para crear/editar facturas"""
    class Meta:
        model = Invoice
        fields = [
            'patient', 'appointment', 'issue_date', 'payment_terms', 
            'discount_amount', 'notes', 'terms_conditions'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'payment_terms': forms.Select(attrs={'class': 'form-select'}),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
            'terms_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Términos y condiciones'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar pacientes activos
        self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
        
        # Filtrar citas programadas y confirmadas
        self.fields['appointment'].queryset = Appointment.objects.filter(
            status__in=['scheduled', 'confirmed']
        ).select_related('patient', 'doctor')
        
        # Hacer appointment opcional
        self.fields['appointment'].required = False
        self.fields['appointment'].empty_label = "Sin cita asociada"
        
        # Establecer fecha por defecto
        if not self.instance.pk:
            self.fields['issue_date'].initial = date.today()
    
    def save(self, commit=True):
        invoice = super().save(commit=False)
        if self.user:
            invoice.created_by = self.user
        
        if commit:
            invoice.save()
        return invoice

class InvoiceItemForm(forms.ModelForm):
    """Formulario para elementos de factura"""
    class Meta:
        model = InvoiceItem
        fields = ['service', 'description', 'quantity', 'unit_price', 'tax_rate', 'discount_rate']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción adicional (opcional)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'discount_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar servicios activos
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        
        # Si se selecciona un servicio, pre-llenar precio y tasa de impuesto
        if self.instance and self.instance.service:
            self.fields['unit_price'].initial = self.instance.service.price
            self.fields['tax_rate'].initial = self.instance.service.tax_rate

class PaymentForm(forms.ModelForm):
    """Formulario para registrar pagos"""
    class Meta:
        model = Payment
        fields = [
            'amount', 'payment_date', 'payment_method', 'reference_number',
            'bank_name', 'check_number', 'notes'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de referencia'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del banco'
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cheque'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer monto máximo como el pendiente de la factura
        if self.invoice:
            max_amount = self.invoice.amount_pending
            self.fields['amount'].widget.attrs['max'] = str(max_amount)
            self.fields['amount'].initial = max_amount
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.invoice and amount:
            if amount > self.invoice.amount_pending:
                raise forms.ValidationError(
                    f"El monto no puede ser mayor al pendiente: ${self.invoice.amount_pending}"
                )
        return amount
    
    def save(self, commit=True):
        payment = super().save(commit=False)
        if self.invoice:
            payment.invoice = self.invoice
        if self.user:
            payment.processed_by = self.user
        
        if commit:
            payment.save()
        return payment

class InsuranceClaimForm(forms.ModelForm):
    """Formulario para reclamos de seguros"""
    class Meta:
        model = InsuranceClaim
        fields = [
            'insurance_company', 'policy_number', 'claim_amount',
            'submission_date', 'notes'
        ]
        widgets = {
            'insurance_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la compañía de seguros'
            }),
            'policy_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de póliza'
            }),
            'claim_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'submission_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas sobre el reclamo'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer monto máximo como el total de la factura
        if self.invoice:
            max_amount = self.invoice.total_amount
            self.fields['claim_amount'].widget.attrs['max'] = str(max_amount)
            self.fields['claim_amount'].initial = max_amount
    
    def clean_claim_amount(self):
        amount = self.cleaned_data.get('claim_amount')
        if self.invoice and amount:
            if amount > self.invoice.total_amount:
                raise forms.ValidationError(
                    f"El monto del reclamo no puede ser mayor al total de la factura: ${self.invoice.total_amount}"
                )
        return amount
    
    def save(self, commit=True):
        claim = super().save(commit=False)
        if self.invoice:
            claim.invoice = self.invoice
        if self.user:
            claim.created_by = self.user
        
        if commit:
            claim.save()
        return claim

class InvoiceFilterForm(forms.Form):
    """Formulario para filtrar facturas"""
    STATUS_CHOICES = [('', 'Todos los estados')] + Invoice.STATUS_CHOICES
    
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(is_active=True),
        required=False,
        empty_label="Todos los pacientes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        label="Fecha Desde",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        label="Fecha Hasta",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    overdue_only = forms.BooleanField(
        label="Solo facturas vencidas",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class PaymentFilterForm(forms.Form):
    """Formulario para filtrar pagos"""
    METHOD_CHOICES = [('', 'Todos los métodos')] + Payment.PAYMENT_METHOD_CHOICES
    STATUS_CHOICES = [('', 'Todos los estados')] + Payment.STATUS_CHOICES
    
    payment_method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        label="Fecha Desde",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    date_to = forms.DateField(
        label="Fecha Hasta",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

class BulkInvoiceForm(forms.Form):
    """Formulario para crear facturas en lote"""
    patients = forms.ModelMultipleChoiceField(
        queryset=Patient.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Seleccionar Pacientes"
    )
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Servicio"
    )
    
    issue_date = forms.DateField(
        label="Fecha de Emisión",
        initial=date.today,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    payment_terms = forms.ChoiceField(
        choices=Invoice.PAYMENT_TERMS_CHOICES,
        initial='30_days',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Términos de Pago"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notas para todas las facturas'
        }),
        label="Notas"
    )