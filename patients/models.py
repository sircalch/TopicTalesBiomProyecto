from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from accounts.models import User, Organization


class Patient(models.Model):
    """
    Patient model for medical management system
    """
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('U', 'Desconocido'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Soltero/a'),
        ('married', 'Casado/a'),
        ('divorced', 'Divorciado/a'),
        ('widowed', 'Viudo/a'),
        ('separated', 'Separado/a'),
        ('other', 'Otro'),
    ]
    
    # Basic Information
    patient_id = models.CharField(max_length=20, unique=True, verbose_name="ID Paciente")
    first_name = models.CharField(max_length=50, verbose_name="Nombre(s)")
    last_name = models.CharField(max_length=50, verbose_name="Apellido paterno")
    mother_last_name = models.CharField(max_length=50, blank=True, verbose_name="Apellido materno")
    birth_date = models.DateField(verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Género")
    
    # Contact Information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato: '+999999999'. Hasta 15 dígitos.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Estado")
    postal_code = models.CharField(max_length=10, verbose_name="Código postal")
    
    # Medical Information
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, default='U', verbose_name="Tipo de sangre")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Altura (cm)")
    
    # Personal Information
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, verbose_name="Estado civil")
    occupation = models.CharField(max_length=100, blank=True, verbose_name="Ocupación")
    education_level = models.CharField(max_length=100, blank=True, verbose_name="Nivel educativo")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, verbose_name="Contacto de emergencia")
    emergency_contact_relationship = models.CharField(max_length=50, verbose_name="Parentesco")
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, verbose_name="Teléfono de emergencia")
    
    # Insurance Information
    insurance_company = models.CharField(max_length=100, blank=True, verbose_name="Aseguradora")
    insurance_policy = models.CharField(max_length=50, blank=True, verbose_name="Póliza")
    insurance_group = models.CharField(max_length=50, blank=True, verbose_name="Grupo")
    
    # System Information
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='patients')
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    last_visit = models.DateTimeField(null=True, blank=True, verbose_name="Última visita")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    
    # Additional fields
    profile_picture = models.ImageField(upload_to='patients/photos/', blank=True, null=True, verbose_name="Foto")
    notes = models.TextField(blank=True, verbose_name="Notas generales")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        if self.mother_last_name:
            return f"{self.first_name} {self.last_name} {self.mother_last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100  # Convert cm to meters
            return round(float(self.weight) / (height_m ** 2), 2)
        return None
    
    @property
    def bmi_category(self):
        bmi = self.bmi
        if not bmi:
            return "N/A"
        if bmi < 18.5:
            return "Bajo peso"
        elif bmi < 25:
            return "Peso normal"
        elif bmi < 30:
            return "Sobrepeso"
        else:
            return "Obesidad"
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-registration_date']


class MedicalHistory(models.Model):
    """
    Medical history for patients
    """
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='medical_history')
    
    # Personal Medical History
    allergies = models.TextField(blank=True, verbose_name="Alergias")
    chronic_diseases = models.TextField(blank=True, verbose_name="Enfermedades crónicas")
    previous_surgeries = models.TextField(blank=True, verbose_name="Cirugías previas")
    current_medications = models.TextField(blank=True, verbose_name="Medicamentos actuales")
    
    # Family Medical History
    family_diseases = models.TextField(blank=True, verbose_name="Enfermedades familiares")
    
    # Lifestyle
    smoking_status = models.CharField(max_length=20, choices=[
        ('never', 'Nunca ha fumado'),
        ('former', 'Ex fumador'),
        ('current', 'Fumador actual'),
    ], default='never', verbose_name="Estado de fumador")
    
    alcohol_consumption = models.CharField(max_length=20, choices=[
        ('none', 'No consume'),
        ('occasional', 'Ocasional'),
        ('moderate', 'Moderado'),
        ('heavy', 'Excesivo'),
    ], default='none', verbose_name="Consumo de alcohol")
    
    exercise_frequency = models.CharField(max_length=20, choices=[
        ('none', 'Sedentario'),
        ('low', 'Poco ejercicio'),
        ('moderate', 'Ejercicio moderado'),
        ('high', 'Ejercicio intenso'),
    ], default='none', verbose_name="Frecuencia de ejercicio")
    
    # Reproductive Health (for women)
    menstrual_cycle_regular = models.BooleanField(null=True, blank=True, verbose_name="Ciclo menstrual regular")
    pregnancies = models.IntegerField(null=True, blank=True, verbose_name="Embarazos")
    births = models.IntegerField(null=True, blank=True, verbose_name="Partos")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Historia médica de {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Historia Médica"
        verbose_name_plural = "Historias Médicas"


class VitalSigns(models.Model):
    """
    Vital signs records for patients
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Vital Signs
    systolic_pressure = models.IntegerField(null=True, blank=True, verbose_name="Presión sistólica")
    diastolic_pressure = models.IntegerField(null=True, blank=True, verbose_name="Presión diastólica")
    heart_rate = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia cardíaca")
    respiratory_rate = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia respiratoria")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°C)")
    oxygen_saturation = models.IntegerField(null=True, blank=True, verbose_name="Saturación de oxígeno (%)")
    
    # Physical measurements
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Altura (cm)")
    
    # Additional measurements
    glucose_level = models.IntegerField(null=True, blank=True, verbose_name="Glucosa (mg/dL)")
    
    notes = models.TextField(blank=True, verbose_name="Observaciones")
    
    def __str__(self):
        return f"Signos vitales - {self.patient.get_full_name()} ({self.recorded_at.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def blood_pressure(self):
        if self.systolic_pressure and self.diastolic_pressure:
            return f"{self.systolic_pressure}/{self.diastolic_pressure}"
        return "N/A"
    
    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None
    
    class Meta:
        verbose_name = "Signos Vitales"
        verbose_name_plural = "Signos Vitales"
        ordering = ['-recorded_at']


class PatientDocument(models.Model):
    """
    Documents associated with patients
    """
    DOCUMENT_TYPES = [
        ('id', 'Identificación'),
        ('insurance', 'Seguro médico'),
        ('lab_result', 'Resultado de laboratorio'),
        ('imaging', 'Estudios de imagen'),
        ('prescription', 'Receta médica'),
        ('consent', 'Consentimiento informado'),
        ('other', 'Otros'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name="Tipo de documento")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    file = models.FileField(upload_to='patients/documents/', verbose_name="Archivo")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Documento del Paciente"
        verbose_name_plural = "Documentos del Paciente"
        ordering = ['-uploaded_at']
