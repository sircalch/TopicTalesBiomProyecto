from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Appointment, AppointmentType, AppointmentTemplate, 
    AppointmentNote, DoctorSchedule, AppointmentBlock
)
from accounts.models import User
from patients.models import Patient


class AppointmentForm(forms.ModelForm):
    """
    Form for creating and editing appointments
    """
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_type', 'start_datetime',
            'reason', 'priority', 'notes', 'patient_phone', 'patient_email'
        ]
        
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'appointment_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo de la consulta médica',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas adicionales (opcional)'
            }),
            'patient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 55 1234-5678'
            }),
            'patient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            })
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            # Filter patients by organization
            self.fields['patient'].queryset = Patient.objects.filter(
                organization=organization, is_active=True
            ).order_by('first_name', 'last_name')
            
            # Filter doctors by organization and role
            self.fields['doctor'].queryset = User.objects.filter(
                profile__organization=organization, role='doctor', is_active=True
            ).order_by('first_name', 'last_name')
            
            # Filter appointment types by organization
            self.fields['appointment_type'].queryset = AppointmentType.objects.filter(
                organization=organization, is_active=True
            ).order_by('name')
    
    def clean_start_datetime(self):
        start_datetime = self.cleaned_data.get('start_datetime')
        if start_datetime:
            # Check if appointment is in the past
            if start_datetime < timezone.now():
                raise ValidationError("La fecha y hora no puede ser en el pasado.")
            
            # Check if appointment is too far in the future (1 year)
            if start_datetime > timezone.now() + timedelta(days=365):
                raise ValidationError("La fecha no puede ser más de un año en el futuro.")
                
        return start_datetime
    
    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        doctor = cleaned_data.get('doctor')
        start_datetime = cleaned_data.get('start_datetime')
        appointment_type = cleaned_data.get('appointment_type')
        
        if all([patient, doctor, start_datetime, appointment_type]):
            # Calculate end datetime
            end_datetime = start_datetime + timedelta(minutes=appointment_type.duration_minutes)
            
            # Check for doctor conflicts
            doctor_conflicts = Appointment.objects.filter(
                doctor=doctor,
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime,
                status__in=['scheduled', 'confirmed', 'in_progress']
            )
            
            # Exclude current appointment for updates
            if self.instance.pk:
                doctor_conflicts = doctor_conflicts.exclude(pk=self.instance.pk)
            
            if doctor_conflicts.exists():
                raise ValidationError("El médico ya tiene una cita programada en este horario.")
            
            # Check for patient conflicts
            patient_conflicts = Appointment.objects.filter(
                patient=patient,
                start_datetime__lt=end_datetime,
                end_datetime__gt=start_datetime,
                status__in=['scheduled', 'confirmed', 'in_progress']
            )
            
            # Exclude current appointment for updates
            if self.instance.pk:
                patient_conflicts = patient_conflicts.exclude(pk=self.instance.pk)
            
            if patient_conflicts.exists():
                raise ValidationError("El paciente ya tiene una cita programada en este horario.")
        
        return cleaned_data


class AppointmentTypeForm(forms.ModelForm):
    """
    Form for managing appointment types
    """
    class Meta:
        model = AppointmentType
        fields = ['name', 'description', 'duration_minutes', 'color', 'price']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de cita'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del tipo de cita'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '480',
                'placeholder': 'Duración en minutos'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#007bff'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            })
        }


class AppointmentNoteForm(forms.ModelForm):
    """
    Form for consultation notes during appointments
    """
    class Meta:
        model = AppointmentNote
        fields = [
            'chief_complaint', 'present_illness_history', 'physical_examination',
            'assessment', 'diagnosis', 'differential_diagnosis', 'treatment_plan',
            'medications', 'recommendations', 'follow_up_needed', 'follow_up_date',
            'referral_needed', 'referral_to', 'additional_notes'
        ]
        
        widgets = {
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo principal de la consulta'
            }),
            'present_illness_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Historia de la enfermedad actual'
            }),
            'physical_examination': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Hallazgos de la exploración física'
            }),
            'assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Evaluación clínica'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnóstico principal'
            }),
            'differential_diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnósticos diferenciales'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Plan de tratamiento'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medicamentos prescritos con dosis y frecuencia'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Recomendaciones generales'
            }),
            'follow_up_needed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'referral_needed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'referral_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialista o servicio de referencia'
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            })
        }


class DoctorScheduleForm(forms.ModelForm):
    """
    Form for managing doctor's work schedule
    """
    class Meta:
        model = DoctorSchedule
        fields = [
            'doctor', 'day_of_week', 'start_time', 'end_time',
            'break_start', 'break_end'
        ]
        
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'break_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'break_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            })
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['doctor'].queryset = User.objects.filter(
                profile__organization=organization, role='doctor', is_active=True
            ).order_by('first_name', 'last_name')
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        break_start = cleaned_data.get('break_start')
        break_end = cleaned_data.get('break_end')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
        
        if break_start and break_end:
            if break_start >= break_end:
                raise ValidationError("La hora de inicio del descanso debe ser anterior a la hora de fin.")
            
            if start_time and end_time:
                if break_start < start_time or break_end > end_time:
                    raise ValidationError("El horario de descanso debe estar dentro del horario de trabajo.")
        
        return cleaned_data


class AppointmentBlockForm(forms.ModelForm):
    """
    Form for blocking doctor availability
    """
    class Meta:
        model = AppointmentBlock
        fields = [
            'doctor', 'block_type', 'title', 'description',
            'start_datetime', 'end_datetime', 'all_day'
        ]
        
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'block_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del bloqueo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del bloqueo'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'all_day': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['doctor'].queryset = User.objects.filter(
                profile__organization=organization, role='doctor', is_active=True
            ).order_by('first_name', 'last_name')
    
    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        
        if start_datetime and end_datetime and start_datetime >= end_datetime:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        return cleaned_data


class AppointmentFilterForm(forms.Form):
    """
    Form for filtering appointments in calendar and list views
    """
    doctor = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Todos los médicos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    appointment_type = forms.ModelChoiceField(
        queryset=AppointmentType.objects.none(),
        required=False,
        empty_label="Todos los tipos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Appointment.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + Appointment.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por paciente, motivo...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['doctor'].queryset = User.objects.filter(
                profile__organization=organization, role='doctor', is_active=True
            ).order_by('first_name', 'last_name')
            
            self.fields['appointment_type'].queryset = AppointmentType.objects.filter(
                organization=organization, is_active=True
            ).order_by('name')


class QuickAppointmentForm(forms.Form):
    """
    Quick appointment form for calendar drag and drop
    """
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    appointment_type = forms.ModelChoiceField(
        queryset=AppointmentType.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reason = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Motivo de la consulta'
        })
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['patient'].queryset = Patient.objects.filter(
                organization=organization, is_active=True
            ).order_by('first_name', 'last_name')
            
            self.fields['appointment_type'].queryset = AppointmentType.objects.filter(
                organization=organization, is_active=True
            ).order_by('name')