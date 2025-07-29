from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    MedicalRecord, Consultation, VitalSigns, LabResult, 
    Prescription, MedicalDocument, MedicalAlert
)
from patients.models import Patient
from accounts.models import User


class MedicalRecordForm(forms.ModelForm):
    """
    Form for creating and editing medical records
    """
    class Meta:
        model = MedicalRecord
        fields = [
            'blood_type', 'allergies', 'chronic_conditions', 'current_medications',
            'family_history', 'smoking_status', 'alcohol_consumption', 'exercise_frequency',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        
        widgets = {
            'blood_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: O+, A-, AB+, etc.'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Lista todas las alergias conocidas del paciente'
            }),
            'chronic_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Condiciones médicas crónicas diagnosticadas'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medicamentos actuales con dosis y frecuencia'
            }),
            'family_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Antecedentes médicos familiares relevantes'
            }),
            'smoking_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alcohol_consumption': forms.Select(attrs={
                'class': 'form-select'
            }),
            'exercise_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del contacto de emergencia'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 55 1234-5678'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relación con el paciente (ej: Esposa, Hijo, Madre)'
            })
        }


class ConsultationForm(forms.ModelForm):
    """
    Form for creating medical consultations
    """
    class Meta:
        model = Consultation
        fields = [
            'consultation_date', 'consultation_type', 'chief_complaint',
            'history_present_illness', 'vital_signs_notes', 'physical_examination',
            'assessment', 'diagnosis_primary', 'diagnosis_secondary',
            'treatment_plan', 'medications_prescribed', 'procedures_performed',
            'follow_up_instructions', 'follow_up_date', 'referral_to',
            'doctor_notes', 'patient_education'
        ]
        
        widgets = {
            'consultation_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'consultation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Motivo principal de la consulta'
            }),
            'history_present_illness': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Historia detallada de la enfermedad actual'
            }),
            'vital_signs_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre los signos vitales'
            }),
            'physical_examination': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Hallazgos de la exploración física'
            }),
            'assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Evaluación clínica del paciente'
            }),
            'diagnosis_primary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Diagnóstico principal'
            }),
            'diagnosis_secondary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Diagnósticos secundarios o diferenciales'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Plan de tratamiento detallado'
            }),
            'medications_prescribed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medicamentos prescritos con dosis y duración'
            }),
            'procedures_performed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Procedimientos realizados durante la consulta'
            }),
            'follow_up_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instrucciones para el seguimiento'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'referral_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialista o servicio de referencia'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas privadas del médico'
            }),
            'patient_education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Educación proporcionada al paciente'
            })
        }
    
    def clean_consultation_date(self):
        consultation_date = self.cleaned_data.get('consultation_date')
        if consultation_date and consultation_date > timezone.now():
            raise ValidationError("La fecha de consulta no puede ser futura.")
        return consultation_date


class VitalSignsForm(forms.ModelForm):
    """
    Form for recording vital signs
    """
    class Meta:
        model = VitalSigns
        fields = [
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height', 'glucose_level', 'pain_scale', 'notes'
        ]
        
        widgets = {
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '30.0',
                'max': '45.0',
                'placeholder': '36.5'
            }),
            'blood_pressure_systolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '50',
                'max': '300',
                'placeholder': '120'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '30',
                'max': '200',
                'placeholder': '80'
            }),
            'heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '30',
                'max': '250',
                'placeholder': '70'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '60',
                'placeholder': '16'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '70',
                'max': '100',
                'placeholder': '98'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '1',
                'placeholder': '70.5'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '50',
                'placeholder': '170.0'
            }),
            'glucose_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '20',
                'max': '800',
                'placeholder': '100'
            }),
            'pain_scale': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'placeholder': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas sobre los signos vitales'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        systolic = cleaned_data.get('blood_pressure_systolic')
        diastolic = cleaned_data.get('blood_pressure_diastolic')
        
        if systolic and diastolic and systolic <= diastolic:
            raise ValidationError("La presión sistólica debe ser mayor que la diastólica.")
        
        return cleaned_data


class LabResultForm(forms.ModelForm):
    """
    Form for recording laboratory results
    """
    class Meta:
        model = LabResult
        fields = [
            'test_name', 'test_code', 'test_category', 'result_value',
            'reference_range', 'units', 'status', 'ordered_date',
            'result_date', 'laboratory_name', 'technician_notes',
            'doctor_interpretation'
        ]
        
        widgets = {
            'test_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del examen de laboratorio'
            }),
            'test_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código del examen (opcional)'
            }),
            'test_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'result_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resultado del examen'
            }),
            'reference_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 70-100 mg/dL'
            }),
            'units': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: mg/dL, mmol/L, etc.'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordered_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'result_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'laboratory_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del laboratorio'
            }),
            'technician_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas del técnico de laboratorio'
            }),
            'doctor_interpretation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Interpretación médica del resultado'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        ordered_date = cleaned_data.get('ordered_date')
        result_date = cleaned_data.get('result_date')
        
        if ordered_date and result_date and result_date < ordered_date:
            raise ValidationError("La fecha del resultado no puede ser anterior a la fecha de orden.")
        
        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    """
    Form for creating prescriptions
    """
    class Meta:
        model = Prescription
        fields = [
            'medication_name', 'generic_name', 'dosage', 'frequency',
            'route', 'duration', 'quantity', 'refills', 'instructions',
            'special_instructions', 'start_date', 'end_date'
        ]
        
        widgets = {
            'medication_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial del medicamento'
            }),
            'generic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre genérico (opcional)'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 500mg, 10ml, 1 tableta'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cada 8 horas, 2 veces al día'
            }),
            'route': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 7 días, 2 semanas, 1 mes'
            }),
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cantidad total a dispensar'
            }),
            'refills': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '12'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Instrucciones de uso para el paciente'
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Instrucciones especiales (opcional)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        
        return cleaned_data


class MedicalDocumentForm(forms.ModelForm):
    """
    Form for uploading medical documents
    """
    class Meta:
        model = MedicalDocument
        fields = ['title', 'description', 'document_type', 'file', 'is_confidential']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo del documento'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del contenido del documento'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif'
            }),
            'is_confidential': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 25MB)
            if file.size > 25 * 1024 * 1024:
                raise ValidationError("El archivo no puede ser mayor a 25MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
            file_extension = '.' + file.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise ValidationError(f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}")
        
        return file


class MedicalAlertForm(forms.ModelForm):
    """
    Form for creating medical alerts
    """
    class Meta:
        model = MedicalAlert
        fields = ['alert_type', 'severity', 'title', 'description', 'expires_at']
        
        widgets = {
            'alert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título breve de la alerta'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada de la alerta médica'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        if expires_at and expires_at <= timezone.now():
            raise ValidationError("La fecha de expiración debe ser futura.")
        return expires_at


class MedicalRecordSearchForm(forms.Form):
    """
    Form for searching medical records
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre del paciente, diagnóstico, medicamento...'
        })
    )
    
    consultation_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los tipos')] + Consultation._meta.get_field('consultation_type').choices,
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
    
    doctor = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Todos los médicos",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        
        if organization:
            self.fields['doctor'].queryset = User.objects.filter(
                profile__organization=organization, role='doctor', is_active=True
            ).order_by('first_name', 'last_name')