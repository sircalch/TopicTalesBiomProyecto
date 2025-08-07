from django import forms
from django.contrib.auth import get_user_model
from .models import Report, ReportTemplate, ReportShare
from datetime import date, timedelta

User = get_user_model()

class ReportFilterForm(forms.Form):
    """Formulario base para filtros de reportes"""
    date_from = forms.DateField(
        label="Fecha Desde",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False
    )
    
    date_to = forms.DateField(
        label="Fecha Hasta", 
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fechas por defecto (último mes)
        today = date.today()
        month_ago = today - timedelta(days=30)
        
        if not self.is_bound:
            self.fields['date_from'].initial = month_ago
            self.fields['date_to'].initial = today

class PatientsReportForm(ReportFilterForm):
    """Formulario para reporte de pacientes"""
    GENDER_CHOICES = [
        ('', 'Todos los géneros'),
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    AGE_RANGE_CHOICES = [
        ('', 'Todas las edades'),
        ('0-18', '0-18 años'),
        ('19-30', '19-30 años'),
        ('31-50', '31-50 años'),
        ('51-70', '51-70 años'),
        ('70+', 'Más de 70 años'),
    ]
    
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label="Género",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    age_range = forms.ChoiceField(
        choices=AGE_RANGE_CHOICES,
        label="Rango de Edad",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    city = forms.CharField(
        label="Ciudad",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filtrar por ciudad'
        })
    )
    
    has_appointments = forms.BooleanField(
        label="Solo pacientes con citas",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    active_only = forms.BooleanField(
        label="Solo pacientes activos",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class AppointmentsReportForm(ReportFilterForm):
    """Formulario para reporte de citas"""
    STATUS_CHOICES = [
        ('', 'Todos los estados'),
        ('scheduled', 'Programada'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No asistió'),
    ]
    
    SPECIALTY_CHOICES = [
        ('', 'Todas las especialidades'),
        ('psychology', 'Psicología'),
        ('nutrition', 'Nutrición'),
        ('general', 'Medicina General'),
        ('pediatrics', 'Pediatría'),
        ('ophthalmology', 'Oftalmología'),
        ('dentistry', 'Odontología'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label="Estado",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    specialty = forms.ChoiceField(
        choices=SPECIALTY_CHOICES,
        label="Especialidad",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        label="Doctor",
        required=False,
        empty_label="Todos los doctores",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    include_notes = forms.BooleanField(
        label="Incluir notas de las citas",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    group_by_day = forms.BooleanField(
        label="Agrupar por día",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class FinancialReportForm(ReportFilterForm):
    """Formulario para reporte financiero"""
    PAYMENT_STATUS_CHOICES = [
        ('', 'Todos los estados'),
        ('paid', 'Pagado'),
        ('pending', 'Pendiente'),
        ('overdue', 'Vencido'),
        ('partial', 'Pago Parcial'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('', 'Todos los métodos'),
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('insurance', 'Seguro'),
    ]
    
    payment_status = forms.ChoiceField(
        choices=PAYMENT_STATUS_CHOICES,
        label="Estado de Pago",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        label="Método de Pago",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_amount = forms.DecimalField(
        label="Monto Mínimo",
        required=False,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    max_amount = forms.DecimalField(
        label="Monto Máximo",
        required=False,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    include_taxes = forms.BooleanField(
        label="Incluir impuestos",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    group_by_month = forms.BooleanField(
        label="Agrupar por mes",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class AnalyticsReportForm(ReportFilterForm):
    """Formulario para reporte de análisis avanzado"""
    METRICS_CHOICES = [
        ('patient_growth', 'Crecimiento de Pacientes'),
        ('appointment_trends', 'Tendencias de Citas'),
        ('revenue_analysis', 'Análisis de Ingresos'),
        ('specialty_performance', 'Rendimiento por Especialidad'),
        ('patient_satisfaction', 'Satisfacción del Paciente'),
        ('doctor_productivity', 'Productividad de Doctores'),
    ]
    
    CHART_TYPES = [
        ('line', 'Gráfico de Líneas'),
        ('bar', 'Gráfico de Barras'),
        ('pie', 'Gráfico Circular'),
        ('area', 'Gráfico de Área'),
    ]
    
    metrics = forms.MultipleChoiceField(
        choices=METRICS_CHOICES,
        label="Métricas a Incluir",
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    chart_type = forms.ChoiceField(
        choices=CHART_TYPES,
        label="Tipo de Gráfico",
        initial='line',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    include_predictions = forms.BooleanField(
        label="Incluir predicciones",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    compare_previous_period = forms.BooleanField(
        label="Comparar con período anterior",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class ReportForm(forms.ModelForm):
    """Formulario para crear/editar reportes"""
    class Meta:
        model = Report
        fields = [
            'title', 'description', 'report_type', 'date_from', 'date_to',
            'file_format', 'is_scheduled', 'schedule_frequency'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del reporte'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional del reporte'
            }),
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'date_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'file_format': forms.Select(
                choices=[
                    ('pdf', 'PDF'),
                    ('excel', 'Excel'),
                    ('csv', 'CSV'),
                    ('json', 'JSON')
                ],
                attrs={'class': 'form-select'}
            ),
            'is_scheduled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'schedule_frequency': forms.Select(
                choices=[
                    ('', 'No programado'),
                    ('daily', 'Diario'),
                    ('weekly', 'Semanal'),
                    ('monthly', 'Mensual'),
                    ('quarterly', 'Trimestral'),
                ],
                attrs={'class': 'form-select'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Establecer fechas por defecto si no se proporcionan
        if not self.instance.pk:
            today = date.today()
            month_ago = today - timedelta(days=30)
            self.fields['date_from'].initial = month_ago
            self.fields['date_to'].initial = today
    
    def save(self, commit=True):
        report = super().save(commit=False)
        if self.user:
            report.created_by = self.user
        
        if commit:
            report.save()
        return report

class ReportTemplateForm(forms.ModelForm):
    """Formulario para crear/editar plantillas de reportes"""
    class Meta:
        model = ReportTemplate
        fields = ['name', 'description', 'report_type', 'is_active', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la plantilla'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la plantilla'
            }),
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        template = super().save(commit=False)
        if self.user:
            template.created_by = self.user
        
        if commit:
            template.save()
        return template

class ReportShareForm(forms.ModelForm):
    """Formulario para compartir reportes"""
    class Meta:
        model = ReportShare
        fields = ['shared_with', 'can_edit', 'can_download', 'expires_at']
        widgets = {
            'shared_with': forms.Select(attrs={'class': 'form-select'}),
            'can_edit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_download': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expires_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.report = kwargs.pop('report', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios para no incluir el creador del reporte
        if self.report:
            self.fields['shared_with'].queryset = User.objects.exclude(
                pk=self.report.created_by.pk
            )
    
    def save(self, commit=True):
        share = super().save(commit=False)
        if self.user:
            share.shared_by = self.user
        if self.report:
            share.report = self.report
        
        if commit:
            share.save()
        return share

class CustomReportForm(forms.Form):
    """Formulario para reportes personalizados"""
    title = forms.CharField(
        label="Título del Reporte",
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el título del reporte'
        })
    )
    
    description = forms.CharField(
        label="Descripción",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descripción opcional'
        })
    )
    
    # Fuentes de datos
    DATA_SOURCES = [
        ('patients', 'Pacientes'),
        ('appointments', 'Citas'),
        ('medical_records', 'Expedientes Médicos'),
        ('psychology_sessions', 'Sesiones de Psicología'),
        ('nutrition_assessments', 'Evaluaciones Nutricionales'),
        ('billing', 'Facturación'),
    ]
    
    data_sources = forms.MultipleChoiceField(
        choices=DATA_SOURCES,
        label="Fuentes de Datos",
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    # Campos a incluir
    include_personal_data = forms.BooleanField(
        label="Incluir datos personales",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_medical_data = forms.BooleanField(
        label="Incluir datos médicos",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_financial_data = forms.BooleanField(
        label="Incluir datos financieros",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Formato y configuración
    file_format = forms.ChoiceField(
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV'),
        ],
        label="Formato de Archivo",
        initial='pdf',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    include_charts = forms.BooleanField(
        label="Incluir gráficos",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_summary = forms.BooleanField(
        label="Incluir resumen ejecutivo",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )