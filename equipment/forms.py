from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Equipment, EquipmentCategory, Location, Supplier, 
    MaintenanceRecord, EquipmentUsageLog, CalibrationRecord, EquipmentAlert
)
from datetime import date, timedelta

User = get_user_model()

class EquipmentCategoryForm(forms.ModelForm):
    """Formulario para categorías de equipos"""
    class Meta:
        model = EquipmentCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class LocationForm(forms.ModelForm):
    """Formulario para ubicaciones"""
    class Meta:
        model = Location
        fields = ['name', 'description', 'floor', 'room_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la ubicación'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción'
            }),
            'floor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Piso'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de habitación'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class SupplierForm(forms.ModelForm):
    """Formulario para proveedores"""
    class Meta:
        model = Supplier
        fields = [
            'name', 'contact_person', 'phone', 'email', 
            'address', 'website', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proveedor'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Persona de contacto'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sitio web'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class EquipmentForm(forms.ModelForm):
    """Formulario para equipos"""
    class Meta:
        model = Equipment
        fields = [
            'name', 'model', 'brand', 'serial_number', 'asset_tag',
            'category', 'supplier', 'location', 'status', 'condition',
            'purchase_price', 'purchase_date', 'warranty_expiry',
            'specifications', 'manual_url', 'description', 'notes',
            'maintenance_frequency_days'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca'
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie'
            }),
            'asset_tag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etiqueta de activo (opcional)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'warranty_expiry': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'manual_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL del manual'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del equipo'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
            'maintenance_frequency_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar opciones activas
        self.fields['category'].queryset = EquipmentCategory.objects.filter(is_active=True)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['location'].queryset = Location.objects.filter(is_active=True)
    
    def save(self, commit=True):
        equipment = super().save(commit=False)
        if self.user:
            equipment.created_by = self.user
        
        if commit:
            equipment.save()
        return equipment

class MaintenanceRecordForm(forms.ModelForm):
    """Formulario para registros de mantenimiento"""
    class Meta:
        model = MaintenanceRecord
        fields = [
            'maintenance_type', 'scheduled_date', 'description',
            'technician', 'supervisor', 'status'
        ]
        widgets = {
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción del trabajo a realizar'
            }),
            'technician': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios staff para técnicos y supervisores
        staff_users = User.objects.filter(is_staff=True)
        self.fields['technician'].queryset = staff_users
        self.fields['supervisor'].queryset = staff_users
        self.fields['supervisor'].required = False
    
    def save(self, commit=True):
        maintenance = super().save(commit=False)
        if self.equipment:
            maintenance.equipment = self.equipment
        
        if commit:
            maintenance.save()
        return maintenance

class EquipmentUsageLogForm(forms.ModelForm):
    """Formulario para registro de uso de equipos"""
    class Meta:
        model = EquipmentUsageLog
        fields = [
            'start_time', 'end_time', 'purpose', 
            'patient_name', 'notes'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Propósito del uso'
            }),
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del paciente (si aplica)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.equipment = kwargs.pop('equipment', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['end_time'].required = False
    
    def save(self, commit=True):
        usage_log = super().save(commit=False)
        if self.equipment:
            usage_log.equipment = self.equipment
        if self.user:
            usage_log.user = self.user
        
        if commit:
            usage_log.save()
        return usage_log

class EquipmentFilterForm(forms.Form):
    """Formulario para filtrar equipos"""
    STATUS_CHOICES = [('', 'Todos los estados')] + Equipment.STATUS_CHOICES
    CONDITION_CHOICES = [('', 'Todas las condiciones')] + Equipment.CONDITION_CHOICES
    
    category = forms.ModelChoiceField(
        queryset=EquipmentCategory.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las ubicaciones",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    maintenance_due = forms.BooleanField(
        label="Solo equipos con mantenimiento vencido",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    warranty_expiring = forms.BooleanField(
        label="Solo equipos con garantía por vencer (30 días)",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class EquipmentAlertForm(forms.ModelForm):
    """Formulario para crear alertas de equipos"""
    class Meta:
        model = EquipmentAlert
        fields = ['alert_type', 'priority', 'title', 'message']
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la alerta'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mensaje de la alerta'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        alert = super().save(commit=False)
        if self.equipment:
            alert.equipment = self.equipment
        
        if commit:
            alert.save()
        return alert