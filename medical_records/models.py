from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, Organization
from patients.models import Patient
from appointments.models import Appointment


class MedicalRecord(models.Model):
    """
    Main medical record for a patient
    """
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='medical_record')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='medical_records')
    
    # Basic Medical Information
    blood_type = models.CharField(max_length=10, blank=True, verbose_name="Tipo de Sangre")
    allergies = models.TextField(blank=True, verbose_name="Alergias")
    chronic_conditions = models.TextField(blank=True, verbose_name="Condiciones Crónicas")
    current_medications = models.TextField(blank=True, verbose_name="Medicamentos Actuales")
    
    # Family History
    family_history = models.TextField(blank=True, verbose_name="Antecedentes Familiares")
    
    # Social History
    smoking_status = models.CharField(max_length=20, choices=[
        ('never', 'Nunca ha fumado'),
        ('former', 'Ex fumador'),
        ('current', 'Fumador actual'),
        ('occasional', 'Fumador ocasional')
    ], default='never', verbose_name="Estado de Fumador")
    
    alcohol_consumption = models.CharField(max_length=20, choices=[
        ('none', 'No consume'),
        ('occasional', 'Ocasional'),
        ('moderate', 'Moderado'),
        ('heavy', 'Excesivo')
    ], default='none', verbose_name="Consumo de Alcohol")
    
    exercise_frequency = models.CharField(max_length=20, choices=[
        ('none', 'Sedentario'),
        ('light', 'Ejercicio ligero'),
        ('moderate', 'Ejercicio moderado'),
        ('intense', 'Ejercicio intenso')
    ], default='none', verbose_name="Frecuencia de Ejercicio")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name="Contacto de Emergencia")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de Emergencia")
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, verbose_name="Relación")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_medical_records')
    
    def __str__(self):
        return f"Expediente Médico - {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Expediente Médico"
        verbose_name_plural = "Expedientes Médicos"


class Consultation(models.Model):
    """
    Individual medical consultations/visits
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='consultation')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='consultations')
    
    # Basic Information
    consultation_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Consulta")
    consultation_type = models.CharField(max_length=50, choices=[
        ('routine', 'Consulta de Rutina'),
        ('follow_up', 'Seguimiento'),
        ('emergency', 'Emergencia'),
        ('specialist', 'Especialista'),
        ('second_opinion', 'Segunda Opinión')
    ], default='routine', verbose_name="Tipo de Consulta")
    
    # Chief Complaint and History
    chief_complaint = models.TextField(verbose_name="Motivo de Consulta")
    history_present_illness = models.TextField(blank=True, verbose_name="Historia de Enfermedad Actual")
    
    # Physical Examination
    vital_signs_notes = models.TextField(blank=True, verbose_name="Signos Vitales")
    physical_examination = models.TextField(blank=True, verbose_name="Exploración Física")
    
    # Assessment and Plan
    assessment = models.TextField(blank=True, verbose_name="Evaluación")
    diagnosis_primary = models.TextField(blank=True, verbose_name="Diagnóstico Principal")
    diagnosis_secondary = models.TextField(blank=True, verbose_name="Diagnósticos Secundarios")
    
    # Treatment
    treatment_plan = models.TextField(blank=True, verbose_name="Plan de Tratamiento")
    medications_prescribed = models.TextField(blank=True, verbose_name="Medicamentos Prescritos")
    procedures_performed = models.TextField(blank=True, verbose_name="Procedimientos Realizados")
    
    # Follow-up
    follow_up_instructions = models.TextField(blank=True, verbose_name="Instrucciones de Seguimiento")
    follow_up_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Seguimiento")
    referral_to = models.CharField(max_length=200, blank=True, verbose_name="Referido a")
    
    # Additional Notes
    doctor_notes = models.TextField(blank=True, verbose_name="Notas del Médico")
    patient_education = models.TextField(blank=True, verbose_name="Educación del Paciente")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Consulta - {self.patient.get_full_name()} ({self.consultation_date.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"
        ordering = ['-consultation_date']


class VitalSigns(models.Model):
    """
    Vital signs recorded during consultations
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='vital_signs')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_vital_signs')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='medical_vital_signs_recorded')
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°C)")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, verbose_name="Presión Sistólica")
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, verbose_name="Presión Diastólica")
    heart_rate = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia Cardíaca")
    respiratory_rate = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia Respiratoria")
    oxygen_saturation = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(70), MaxValueValidator(100)], verbose_name="Saturación de Oxígeno (%)")
    
    # Physical Measurements
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Altura (cm)")
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="IMC")
    
    # Additional Measurements
    glucose_level = models.IntegerField(null=True, blank=True, verbose_name="Nivel de Glucosa (mg/dL)")
    pain_scale = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)], verbose_name="Escala de Dolor (0-10)")
    
    recorded_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Registro")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    def save(self, *args, **kwargs):
        # Calculate BMI if weight and height are provided
        if self.weight and self.height:
            height_m = float(self.height) / 100  # Convert cm to m
            self.bmi = float(self.weight) / (height_m * height_m)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Signos Vitales - {self.patient.get_full_name()} ({self.recorded_at.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Signos Vitales"
        verbose_name_plural = "Signos Vitales"
        ordering = ['-recorded_at']


class LabResult(models.Model):
    """
    Laboratory test results
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='lab_results')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Test Information
    test_name = models.CharField(max_length=200, verbose_name="Nombre del Examen")
    test_code = models.CharField(max_length=50, blank=True, verbose_name="Código del Examen")
    test_category = models.CharField(max_length=100, choices=[
        ('hematology', 'Hematología'),
        ('chemistry', 'Química Sanguínea'),
        ('immunology', 'Inmunología'),
        ('microbiology', 'Microbiología'),
        ('pathology', 'Patología'),
        ('radiology', 'Radiología'),
        ('cardiology', 'Cardiología'),
        ('other', 'Otro')
    ], default='chemistry', verbose_name="Categoría")
    
    # Results
    result_value = models.CharField(max_length=500, verbose_name="Resultado")
    reference_range = models.CharField(max_length=200, blank=True, verbose_name="Rango de Referencia")
    units = models.CharField(max_length=50, blank=True, verbose_name="Unidades")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('normal', 'Normal'),
        ('abnormal', 'Anormal'),
        ('critical', 'Crítico'),
        ('pending', 'Pendiente')
    ], default='pending', verbose_name="Estado")
    
    # Dates
    ordered_date = models.DateField(verbose_name="Fecha de Orden")
    result_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Resultado")
    
    # Laboratory Info
    laboratory_name = models.CharField(max_length=200, blank=True, verbose_name="Laboratorio")
    technician_notes = models.TextField(blank=True, verbose_name="Notas del Técnico")
    doctor_interpretation = models.TextField(blank=True, verbose_name="Interpretación Médica")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.get_full_name()} ({self.ordered_date})"
    
    class Meta:
        verbose_name = "Resultado de Laboratorio"
        verbose_name_plural = "Resultados de Laboratorio"
        ordering = ['-ordered_date']


class Prescription(models.Model):
    """
    Medical prescriptions
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    prescribed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    
    # Medication Information
    medication_name = models.CharField(max_length=200, verbose_name="Nombre del Medicamento")
    generic_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre Genérico")
    dosage = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    route = models.CharField(max_length=50, choices=[
        ('oral', 'Oral'),
        ('topical', 'Tópico'),
        ('injection', 'Inyección'),
        ('inhalation', 'Inhalación'),
        ('other', 'Otro')
    ], default='oral', verbose_name="Vía de Administración")
    
    # Duration and Quantity
    duration = models.CharField(max_length=100, verbose_name="Duración del Tratamiento")
    quantity = models.CharField(max_length=100, blank=True, verbose_name="Cantidad")
    refills = models.IntegerField(default=0, verbose_name="Reposiciones")
    
    # Instructions
    instructions = models.TextField(verbose_name="Instrucciones")
    special_instructions = models.TextField(blank=True, verbose_name="Instrucciones Especiales")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('discontinued', 'Discontinuado'),
        ('on_hold', 'En Espera')
    ], default='active', verbose_name="Estado")
    
    prescribed_date = models.DateField(default=timezone.now, verbose_name="Fecha de Prescripción")
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Fin")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medication_name} - {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Prescripción"
        verbose_name_plural = "Prescripciones"
        ordering = ['-prescribed_date']


class MedicalDocument(models.Model):
    """
    Medical documents and attachments
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_documents')
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Document Information
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    document_type = models.CharField(max_length=50, choices=[
        ('lab_result', 'Resultado de Laboratorio'),
        ('imaging', 'Estudio de Imagen'),
        ('prescription', 'Receta'),
        ('report', 'Reporte Médico'),
        ('referral', 'Referencia'),
        ('consent', 'Consentimiento'),
        ('insurance', 'Seguro'),
        ('other', 'Otro')
    ], default='other', verbose_name="Tipo de Documento")
    
    # File
    file = models.FileField(upload_to='medical_documents/%Y/%m/', verbose_name="Archivo")
    file_size = models.IntegerField(null=True, blank=True)
    
    # Metadata
    is_confidential = models.BooleanField(default=True, verbose_name="Confidencial")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Documento Médico"
        verbose_name_plural = "Documentos Médicos"
        ordering = ['-uploaded_at']


class MedicalAlert(models.Model):
    """
    Medical alerts and warnings for patients
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_alerts')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Alert Information
    alert_type = models.CharField(max_length=50, choices=[
        ('allergy', 'Alergia'),
        ('drug_interaction', 'Interacción de Medicamentos'),
        ('medical_condition', 'Condición Médica'),
        ('behavioral', 'Conductual'),
        ('administrative', 'Administrativa'),
        ('other', 'Otra')
    ], verbose_name="Tipo de Alerta")
    
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica')
    ], default='medium', verbose_name="Severidad")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira el")
    
    def __str__(self):
        return f"Alerta: {self.title} - {self.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Alerta Médica"
        verbose_name_plural = "Alertas Médicas"
        ordering = ['-created_at']


class MedicalRecordTemplate(models.Model):
    """
    Templates for medical records to standardize data collection
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='medical_templates')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    
    # Template Information
    name = models.CharField(max_length=200, verbose_name="Nombre de la Plantilla")
    description = models.TextField(blank=True, verbose_name="Descripción")
    category = models.CharField(max_length=100, choices=[
        ('general', 'General'),
        ('pediatria', 'Pediatría'),
        ('ginecologia', 'Ginecología'),
        ('cardiologia', 'Cardiología'),
        ('neurologia', 'Neurología'),
        ('dermatologia', 'Dermatología'),
        ('traumatologia', 'Traumatología'),
        ('psiquiatria', 'Psiquiatría'),
        ('oftalmologia', 'Oftalmología'),
        ('otorrinolaringologia', 'Otorrinolaringología'),
        ('otra', 'Otra')
    ], default='general', verbose_name="Categoría")
    
    # Template Configuration - JSON field to store field configurations
    fields_config = models.JSONField(default=dict, verbose_name="Configuración de Campos", help_text="JSON con la configuración de campos incluidos")
    
    # Template Sections
    include_basic_info = models.BooleanField(default=True, verbose_name="Incluir Información Básica")
    include_vital_signs = models.BooleanField(default=True, verbose_name="Incluir Signos Vitales")
    include_allergies = models.BooleanField(default=True, verbose_name="Incluir Alergias")
    include_medications = models.BooleanField(default=True, verbose_name="Incluir Medicamentos")
    include_family_history = models.BooleanField(default=True, verbose_name="Incluir Historial Familiar")
    include_social_history = models.BooleanField(default=True, verbose_name="Incluir Historial Social")
    include_emergency_contact = models.BooleanField(default=True, verbose_name="Incluir Contacto de Emergencia")
    
    # Custom Fields (JSON format)
    custom_fields = models.JSONField(default=list, verbose_name="Campos Personalizados", help_text="Lista de campos personalizados adicionales")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    is_public = models.BooleanField(default=False, verbose_name="Pública", help_text="Disponible para todas las organizaciones")
    
    # Usage Statistics
    usage_count = models.IntegerField(default=0, verbose_name="Veces Utilizada")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_field_list(self):
        """Return a list of included fields"""
        fields = []
        if self.include_basic_info:
            fields.extend(['Tipo de Sangre', 'Información Básica'])
        if self.include_vital_signs:
            fields.append('Signos Vitales')
        if self.include_allergies:
            fields.append('Alergias')
        if self.include_medications:
            fields.append('Medicamentos Actuales')
        if self.include_family_history:
            fields.append('Historial Familiar')
        if self.include_social_history:
            fields.append('Historial Social')
        if self.include_emergency_contact:
            fields.append('Contacto de Emergencia')
        
        # Add custom fields
        for field in self.custom_fields:
            fields.append(field.get('name', 'Campo Personalizado'))
            
        return fields
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    class Meta:
        verbose_name = "Plantilla de Expediente"
        verbose_name_plural = "Plantillas de Expedientes"
        ordering = ['-created_at']
        unique_together = ['organization', 'name']
