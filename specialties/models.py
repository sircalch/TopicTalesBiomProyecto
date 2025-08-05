from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from patients.models import Patient

User = get_user_model()

class Specialty(models.Model):
    """Especialidades médicas disponibles"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    
    # Configuración
    requires_referral = models.BooleanField(default=False, verbose_name="Requiere Referencia")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # Precios por defecto
    consultation_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio de Consulta")
    follow_up_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio de Seguimiento")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    """Doctores y sus especialidades"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    specialties = models.ManyToManyField(Specialty, verbose_name="Especialidades")
    
    # Información profesional
    license_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Licencia")
    education = models.TextField(blank=True, verbose_name="Educación")
    certifications = models.TextField(blank=True, verbose_name="Certificaciones")
    years_experience = models.PositiveIntegerField(default=0, verbose_name="Años de Experiencia")
    
    # Disponibilidad
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    accepts_new_patients = models.BooleanField(default=True, verbose_name="Acepta Nuevos Pacientes")
    
    # Información adicional
    bio = models.TextField(blank=True, verbose_name="Biografía")
    photo = models.ImageField(upload_to='doctors/', blank=True, verbose_name="Foto")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctores"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"

class SpecialtyProcedure(models.Model):
    """Procedimientos específicos por especialidad"""
    name = models.CharField(max_length=200, verbose_name="Nombre del Procedimiento")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='procedures', verbose_name="Especialidad")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Información del procedimiento
    duration_minutes = models.PositiveIntegerField(verbose_name="Duración (minutos)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    preparation_instructions = models.TextField(blank=True, verbose_name="Instrucciones de Preparación")
    
    # Configuración
    requires_anesthesia = models.BooleanField(default=False, verbose_name="Requiere Anestesia")
    requires_fasting = models.BooleanField(default=False, verbose_name="Requiere Ayuno")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Procedimiento de Especialidad"
        verbose_name_plural = "Procedimientos de Especialidades"
        ordering = ['specialty', 'name']
    
    def __str__(self):
        return f"{self.specialty.name} - {self.name}"

class SpecialtyConsultation(models.Model):
    """Consultas específicas por especialidad"""
    TYPE_CHOICES = [
        ('initial', 'Consulta Inicial'),
        ('follow_up', 'Seguimiento'),
        ('emergency', 'Emergencia'),
        ('routine', 'Control de Rutina'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Doctor")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name="Especialidad")
    
    consultation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo de Consulta")
    date = models.DateTimeField(verbose_name="Fecha y Hora")
    
    # Motivo y síntomas
    chief_complaint = models.TextField(verbose_name="Motivo Principal de Consulta")
    symptoms = models.TextField(blank=True, verbose_name="Síntomas")
    
    # Examen físico
    physical_examination = models.TextField(blank=True, verbose_name="Examen Físico")
    vital_signs = models.JSONField(default=dict, blank=True, verbose_name="Signos Vitales")
    
    # Diagnóstico y tratamiento
    diagnosis = models.TextField(blank=True, verbose_name="Diagnóstico")
    treatment_plan = models.TextField(blank=True, verbose_name="Plan de Tratamiento")
    medications = models.TextField(blank=True, verbose_name="Medicamentos")
    
    # Seguimiento
    follow_up_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Seguimiento")
    follow_up_instructions = models.TextField(blank=True, verbose_name="Instrucciones de Seguimiento")
    
    # Referrals
    referral_needed = models.BooleanField(default=False, verbose_name="Necesita Referencia")
    referral_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, null=True, blank=True, 
                                         related_name='referrals', verbose_name="Especialidad de Referencia")
    referral_reason = models.TextField(blank=True, verbose_name="Razón de Referencia")
    
    # Estado
    is_completed = models.BooleanField(default=False, verbose_name="Completada")
    notes = models.TextField(blank=True, verbose_name="Notas Adicionales")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Consulta de Especialidad"
        verbose_name_plural = "Consultas de Especialidades"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.specialty.name} - {self.patient.get_full_name()} ({self.date.strftime('%d/%m/%Y')})"

class SpecialtyTreatment(models.Model):
    """Tratamientos específicos por especialidad"""
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('suspended', 'Suspendido'),
        ('cancelled', 'Cancelado'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Doctor")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, verbose_name="Especialidad")
    consultation = models.ForeignKey(SpecialtyConsultation, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Consulta Origen")
    
    # Información del tratamiento
    name = models.CharField(max_length=200, verbose_name="Nombre del Tratamiento")
    description = models.TextField(verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Estado")
    
    # Fechas
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    expected_end_date = models.DateField(null=True, blank=True, verbose_name="Fecha Esperada de Finalización")
    actual_end_date = models.DateField(null=True, blank=True, verbose_name="Fecha Real de Finalización")
    
    # Objetivos y seguimiento
    objectives = models.TextField(verbose_name="Objetivos del Tratamiento")
    progress_notes = models.TextField(blank=True, verbose_name="Notas de Progreso")
    
    # Medicamentos y procedimientos
    medications = models.TextField(blank=True, verbose_name="Medicamentos")
    procedures = models.ManyToManyField(SpecialtyProcedure, blank=True, verbose_name="Procedimientos")
    
    # Resultados
    outcomes = models.TextField(blank=True, verbose_name="Resultados")
    complications = models.TextField(blank=True, verbose_name="Complicaciones")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Tratamiento de Especialidad"
        verbose_name_plural = "Tratamientos de Especialidades"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.patient.get_full_name()}"

class SpecialtyReferral(models.Model):
    """Referencias entre especialidades"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('rejected', 'Rechazada'),
    ]
    
    URGENCY_CHOICES = [
        ('routine', 'Rutina'),
        ('urgent', 'Urgente'),
        ('emergency', 'Emergencia'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Paciente")
    referring_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='referrals_made', verbose_name="Doctor Referente")
    from_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='referrals_from', verbose_name="Especialidad Origen")
    to_specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='referrals_to', verbose_name="Especialidad Destino")
    receiving_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name='referrals_received', verbose_name="Doctor Receptor")
    
    # Información de la referencia
    reason = models.TextField(verbose_name="Razón de la Referencia")
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='routine', verbose_name="Urgencia")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Información clínica
    relevant_history = models.TextField(blank=True, verbose_name="Historia Relevante")
    current_medications = models.TextField(blank=True, verbose_name="Medicamentos Actuales")
    test_results = models.TextField(blank=True, verbose_name="Resultados de Pruebas")
    
    # Fechas
    referral_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Referencia")
    appointment_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cita")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Completado")
    
    # Respuesta
    response = models.TextField(blank=True, verbose_name="Respuesta del Especialista")
    recommendations = models.TextField(blank=True, verbose_name="Recomendaciones")
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Referencia de Especialidad"
        verbose_name_plural = "Referencias de Especialidades"
        ordering = ['-referral_date']
    
    def __str__(self):
        return f"{self.from_specialty.name} → {self.to_specialty.name} - {self.patient.get_full_name()}"
