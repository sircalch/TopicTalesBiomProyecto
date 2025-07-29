from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Patient, MedicalHistory, VitalSigns, PatientDocument


class PatientForm(forms.ModelForm):
    """
    Form for creating and editing patients
    """
    class Meta:
        model = Patient
        fields = [
            'patient_id', 'first_name', 'last_name', 'mother_last_name',
            'birth_date', 'gender', 'phone_number', 'email', 'address',
            'city', 'state', 'postal_code', 'blood_type', 'weight', 'height',
            'marital_status', 'occupation', 'education_level',
            'emergency_contact_name', 'emergency_contact_relationship', 
            'emergency_contact_phone', 'insurance_company', 'insurance_policy',
            'insurance_group', 'profile_picture', 'notes'
        ]
        
        widgets = {
            'patient_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID único del paciente (ej: PAC001)'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre(s) del paciente'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido paterno'
            }),
            'mother_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido materno'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 55 1234-5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa del paciente'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg',
                'step': '0.1',
                'min': '0'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Altura en cm',
                'step': '0.1',
                'min': '50'
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ocupación del paciente'
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nivel educativo'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del contacto'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relación (ej: Esposa, Hijo, Madre)'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+52 55 1234-5678'
            }),
            'insurance_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la aseguradora'
            }),
            'insurance_policy': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de póliza'
            }),
            'insurance_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Grupo de seguro'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas generales sobre el paciente'
            })
        }
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            if birth_date > today:
                raise ValidationError("La fecha de nacimiento no puede ser futura.")
            
            # Check if age is reasonable (not more than 150 years)
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age > 150:
                raise ValidationError("La edad no puede ser mayor a 150 años.")
                
        return birth_date
    
    def clean_patient_id(self):
        patient_id = self.cleaned_data.get('patient_id')
        if patient_id:
            # Check if patient_id already exists (excluding current instance for updates)
            qs = Patient.objects.filter(patient_id=patient_id)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Ya existe un paciente con este ID.")
        return patient_id
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and (weight <= 0 or weight > 1000):
            raise ValidationError("El peso debe estar entre 0.1 y 1000 kg.")
        return weight
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is not None and (height < 30 or height > 300):
            raise ValidationError("La altura debe estar entre 30 y 300 cm.")
        return height


class MedicalHistoryForm(forms.ModelForm):
    """
    Form for managing patient medical history
    """
    class Meta:
        model = MedicalHistory
        fields = [
            'allergies', 'chronic_diseases', 'previous_surgeries', 
            'current_medications', 'family_diseases', 'smoking_status',
            'alcohol_consumption', 'exercise_frequency', 'menstrual_cycle_regular',
            'pregnancies', 'births'
        ]
        
        widgets = {
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alergias conocidas del paciente'
            }),
            'chronic_diseases': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enfermedades crónicas diagnosticadas'
            }),
            'previous_surgeries': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Cirugías previas con fechas aproximadas'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medicamentos actuales con dosis'
            }),
            'family_diseases': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enfermedades familiares relevantes'
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
            'menstrual_cycle_regular': forms.Select(choices=[
                ('', 'No aplica'),
                (True, 'Regular'),
                (False, 'Irregular')
            ], attrs={
                'class': 'form-select'
            }),
            'pregnancies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Número total de embarazos'
            }),
            'births': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Número total de partos'
            })
        }


class VitalSignsForm(forms.ModelForm):
    """
    Form for recording patient vital signs
    """
    class Meta:
        model = VitalSigns
        fields = [
            'systolic_pressure', 'diastolic_pressure', 'heart_rate',
            'respiratory_rate', 'temperature', 'oxygen_saturation',
            'weight', 'height', 'glucose_level', 'notes'
        ]
        
        widgets = {
            'systolic_pressure': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'mmHg',
                'min': '50',
                'max': '300'
            }),
            'diastolic_pressure': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'mmHg',
                'min': '30',
                'max': '200'
            }),
            'heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'latidos/min',
                'min': '30',
                'max': '250'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'respiraciones/min',
                'min': '5',
                'max': '60'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '°C',
                'step': '0.1',
                'min': '30.0',
                'max': '45.0'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '%',
                'min': '70',
                'max': '100'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'kg',
                'step': '0.1',
                'min': '0.1'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'cm',
                'step': '0.1',
                'min': '30'
            }),
            'glucose_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'mg/dL',
                'min': '20',
                'max': '800'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre los signos vitales'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        systolic = cleaned_data.get('systolic_pressure')
        diastolic = cleaned_data.get('diastolic_pressure')
        
        if systolic and diastolic and systolic <= diastolic:
            raise ValidationError("La presión sistólica debe ser mayor que la diastólica.")
        
        return cleaned_data


class PatientDocumentForm(forms.ModelForm):
    """
    Form for uploading patient documents
    """
    class Meta:
        model = PatientDocument
        fields = ['document_type', 'title', 'description', 'file']
        
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título descriptivo del documento'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional del documento'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("El archivo no puede ser mayor a 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError(f"Tipo de archivo no permitido. Permitidos: {', '.join(allowed_extensions)}")
        
        return file


class PatientSearchForm(forms.Form):
    """
    Form for advanced patient search
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, ID, email o teléfono...'
        })
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Patient.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    age_range = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas las edades'),
            ('0-17', '0-17 años'),
            ('18-35', '18-35 años'),
            ('36-60', '36-60 años'),
            ('60+', '60+ años')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    blood_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Patient.BLOOD_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos'),
            ('true', 'Activos'),
            ('false', 'Inactivos')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )