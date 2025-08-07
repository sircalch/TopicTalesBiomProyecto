from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML, Div, Field
from crispy_forms.bootstrap import TabHolder, Tab

from .models import (
    Specialty, Doctor, SpecialtyProcedure, SpecialtyConsultation,
    SpecialtyTreatment, SpecialtyReferral
)
from patients.models import Patient

User = get_user_model()

class SpecialtyForm(forms.ModelForm):
    """Formulario para crear/editar especialidades"""
    
    class Meta:
        model = Specialty
        fields = [
            'name', 'description', 'code', 'requires_referral',
            'consultation_price', 'follow_up_price', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'consultation_price': forms.NumberInput(attrs={'step': '0.01'}),
            'follow_up_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6'),
                Column('code', css_class='form-group col-md-6'),
            ),
            'description',
            Row(
                Column('consultation_price', css_class='form-group col-md-6'),
                Column('follow_up_price', css_class='form-group col-md-6'),
            ),
            Row(
                Column('requires_referral', css_class='form-group col-md-6'),
                Column('is_active', css_class='form-group col-md-6'),
            ),
            Submit('submit', 'Guardar Especialidad', css_class='btn btn-primary')
        )

class DoctorForm(forms.ModelForm):
    """Formulario para crear/editar doctores"""
    
    class Meta:
        model = Doctor
        fields = [
            'user', 'specialties', 'license_number', 'education',
            'certifications', 'years_experience', 'bio', 'photo',
            'is_active', 'accepts_new_patients'
        ]
        widgets = {
            'specialties': forms.CheckboxSelectMultiple(),
            'education': forms.Textarea(attrs={'rows': 3}),
            'certifications': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios que sean médicos o no tengan perfil de doctor
        self.fields['user'].queryset = User.objects.filter(
            role__in=['doctor', 'admin']
        ).exclude(
            doctor__isnull=False
        ) if not self.instance.pk else User.objects.filter(
            role__in=['doctor', 'admin']
        )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Información Básica',
                    Row(
                        Column('user', css_class='form-group col-md-6'),
                        Column('license_number', css_class='form-group col-md-6'),
                    ),
                    'specialties',
                    Row(
                        Column('years_experience', css_class='form-group col-md-6'),
                        Column('photo', css_class='form-group col-md-6'),
                    ),
                ),
                Tab('Información Profesional',
                    'education',
                    'certifications',
                    'bio',
                ),
                Tab('Configuración',
                    Row(
                        Column('is_active', css_class='form-group col-md-6'),
                        Column('accepts_new_patients', css_class='form-group col-md-6'),
                    ),
                )
            ),
            Submit('submit', 'Guardar Doctor', css_class='btn btn-primary')
        )

class SpecialtyProcedureForm(forms.ModelForm):
    """Formulario para crear/editar procedimientos de especialidad"""
    
    class Meta:
        model = SpecialtyProcedure
        fields = [
            'name', 'specialty', 'description', 'duration_minutes', 'price',
            'preparation_instructions', 'requires_anesthesia', 'requires_fasting',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'preparation_instructions': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-8'),
                Column('specialty', css_class='form-group col-md-4'),
            ),
            'description',
            Row(
                Column('duration_minutes', css_class='form-group col-md-4'),
                Column('price', css_class='form-group col-md-4'),
                Column('is_active', css_class='form-group col-md-4'),
            ),
            'preparation_instructions',
            Row(
                Column('requires_anesthesia', css_class='form-group col-md-6'),
                Column('requires_fasting', css_class='form-group col-md-6'),
            ),
            Submit('submit', 'Guardar Procedimiento', css_class='btn btn-primary')
        )

class SpecialtyConsultationForm(forms.ModelForm):
    """Formulario para crear/editar consultas de especialidad"""
    
    class Meta:
        model = SpecialtyConsultation
        fields = [
            'patient', 'doctor', 'specialty', 'consultation_type', 'date',
            'chief_complaint', 'symptoms', 'physical_examination',
            'diagnosis', 'treatment_plan', 'medications',
            'follow_up_date', 'follow_up_instructions',
            'referral_needed', 'referral_specialty', 'referral_reason',
            'notes', 'is_completed'
        ]
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'chief_complaint': forms.Textarea(attrs={'rows': 2}),
            'symptoms': forms.Textarea(attrs={'rows': 3}),
            'physical_examination': forms.Textarea(attrs={'rows': 4}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'rows': 4}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'follow_up_instructions': forms.Textarea(attrs={'rows': 3}),
            'referral_reason': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar doctores activos
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Filtrar especialidades activas
        self.fields['specialty'].queryset = Specialty.objects.filter(is_active=True)
        self.fields['referral_specialty'].queryset = Specialty.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab('Información de la Consulta',
                    Row(
                        Column('patient', css_class='form-group col-md-4'),
                        Column('doctor', css_class='form-group col-md-4'),
                        Column('specialty', css_class='form-group col-md-4'),
                    ),
                    Row(
                        Column('consultation_type', css_class='form-group col-md-6'),
                        Column('date', css_class='form-group col-md-6'),
                    ),
                    'chief_complaint',
                    'symptoms',
                ),
                Tab('Examen y Diagnóstico',
                    'physical_examination',
                    'diagnosis',
                    'treatment_plan',
                    'medications',
                ),
                Tab('Seguimiento y Referencias',
                    Row(
                        Column('follow_up_date', css_class='form-group col-md-6'),
                        Column('referral_needed', css_class='form-group col-md-6'),
                    ),
                    'follow_up_instructions',
                    'referral_specialty',
                    'referral_reason',
                ),
                Tab('Notas y Estado',
                    'notes',
                    'is_completed',
                )
            ),
            Submit('submit', 'Guardar Consulta', css_class='btn btn-primary')
        )

class SpecialtyTreatmentForm(forms.ModelForm):
    """Formulario para crear/editar tratamientos de especialidad"""
    
    class Meta:
        model = SpecialtyTreatment
        fields = [
            'patient', 'doctor', 'specialty', 'consultation', 'name',
            'description', 'status', 'start_date', 'expected_end_date',
            'objectives', 'medications', 'procedures'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'procedures': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar opciones
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)
        self.fields['specialty'].queryset = Specialty.objects.filter(is_active=True)
        
        if self.instance.pk and self.instance.specialty:
            self.fields['procedures'].queryset = SpecialtyProcedure.objects.filter(
                specialty=self.instance.specialty, is_active=True
            )
        else:
            self.fields['procedures'].queryset = SpecialtyProcedure.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('patient', css_class='form-group col-md-4'),
                Column('doctor', css_class='form-group col-md-4'),
                Column('specialty', css_class='form-group col-md-4'),
            ),
            'consultation',
            Row(
                Column('name', css_class='form-group col-md-8'),
                Column('status', css_class='form-group col-md-4'),
            ),
            'description',
            Row(
                Column('start_date', css_class='form-group col-md-6'),
                Column('expected_end_date', css_class='form-group col-md-6'),
            ),
            'objectives',
            'medications',
            'procedures',
            Submit('submit', 'Guardar Tratamiento', css_class='btn btn-primary')
        )

class SpecialtyReferralForm(forms.ModelForm):
    """Formulario para crear/editar referencias de especialidad"""
    
    class Meta:
        model = SpecialtyReferral
        fields = [
            'patient', 'referring_doctor', 'from_specialty', 'to_specialty',
            'receiving_doctor', 'reason', 'urgency', 'relevant_history',
            'current_medications', 'test_results'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'relevant_history': forms.Textarea(attrs={'rows': 4}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
            'test_results': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar doctores activos
        self.fields['referring_doctor'].queryset = Doctor.objects.filter(is_active=True)
        self.fields['receiving_doctor'].queryset = Doctor.objects.filter(is_active=True)
        
        # Filtrar especialidades activas
        self.fields['from_specialty'].queryset = Specialty.objects.filter(is_active=True)
        self.fields['to_specialty'].queryset = Specialty.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('patient', css_class='form-group col-md-6'),
                Column('urgency', css_class='form-group col-md-6'),
            ),
            Row(
                Column('referring_doctor', css_class='form-group col-md-6'),
                Column('receiving_doctor', css_class='form-group col-md-6'),
            ),
            Row(
                Column('from_specialty', css_class='form-group col-md-6'),
                Column('to_specialty', css_class='form-group col-md-6'),
            ),
            'reason',
            'relevant_history',
            'current_medications',
            'test_results',
            Submit('submit', 'Crear Referencia', css_class='btn btn-primary')
        )

class SpecialtyFilterForm(forms.Form):
    """Formulario para filtrar consultas de especialidades"""
    
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las especialidades"
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True),
        required=False,
        empty_label="Todos los doctores"
    )
    consultation_type = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + SpecialtyConsultation.TYPE_CHOICES,
        required=False
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    completed_only = forms.BooleanField(
        required=False,
        label="Solo consultas completadas"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('specialty', css_class='form-group col-md-3'),
                Column('doctor', css_class='form-group col-md-3'),
                Column('consultation_type', css_class='form-group col-md-3'),
                Column('completed_only', css_class='form-group col-md-3'),
            ),
            Row(
                Column('date_from', css_class='form-group col-md-6'),
                Column('date_to', css_class='form-group col-md-6'),
            ),
            Submit('submit', 'Filtrar', css_class='btn btn-primary'),
            HTML('<a href="{% url "specialties:consultation_list" %}" class="btn btn-secondary ml-2">Limpiar</a>')
        )

class DoctorAvailabilityForm(forms.Form):
    """Formulario para configurar disponibilidad de doctores"""
    
    DAYS_OF_WEEK = [
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miércoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sábado'),
        ('sunday', 'Domingo'),
    ]
    
    days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Días disponibles"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de inicio"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label="Hora de fin"
    )
    consultation_duration = forms.IntegerField(
        min_value=15,
        max_value=180,
        initial=30,
        label="Duración de consulta (minutos)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'days',
            Row(
                Column('start_time', css_class='form-group col-md-4'),
                Column('end_time', css_class='form-group col-md-4'),
                Column('consultation_duration', css_class='form-group col-md-4'),
            ),
            Submit('submit', 'Guardar Disponibilidad', css_class='btn btn-primary')
        )

class SpecialtySearchForm(forms.Form):
    """Formulario de búsqueda para especialidades"""
    
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar especialidades, doctores, procedimientos...',
            'class': 'form-control'
        })
    )
    specialty_filter = forms.ModelChoiceField(
        queryset=Specialty.objects.filter(is_active=True),
        required=False,
        empty_label="Todas las especialidades"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-8'),
                Column('specialty_filter', css_class='form-group col-md-4'),
            ),
            Submit('submit', 'Buscar', css_class='btn btn-primary')
        )