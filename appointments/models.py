from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, Organization
from patients.models import Patient


class AppointmentType(models.Model):
    """
    Types of appointments available in the medical system
    """
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    duration_minutes = models.IntegerField(default=30, validators=[MinValueValidator(5), MaxValueValidator(480)], verbose_name="Duración (minutos)")
    color = models.CharField(max_length=7, default="#007bff", help_text="Color en formato hexadecimal", verbose_name="Color")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="Precio")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointment_types')
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"
    
    class Meta:
        verbose_name = "Tipo de Cita"
        verbose_name_plural = "Tipos de Cita"
        unique_together = ['name', 'organization']


class Appointment(models.Model):
    """
    Appointment scheduling system for medical consultations
    """
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('confirmed', 'Confirmada'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No se presentó'),
        ('rescheduled', 'Reprogramada'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Basic Information
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'role': 'doctor'})
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE, related_name='appointments')
    
    # Scheduling
    start_datetime = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    end_datetime = models.DateTimeField(verbose_name="Fecha y hora de fin")
    
    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Estado")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name="Prioridad")
    
    # Additional Information
    reason = models.TextField(verbose_name="Motivo de la consulta")
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    private_notes = models.TextField(blank=True, verbose_name="Notas privadas (solo personal médico)")
    
    # Contact and Reminders
    patient_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono del paciente")
    patient_email = models.EmailField(blank=True, verbose_name="Email del paciente")
    reminder_sent = models.BooleanField(default=False, verbose_name="Recordatorio enviado")
    reminder_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Recordatorio enviado el")
    
    # System Information
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointments')
    
    # Billing
    amount_charged = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Monto cobrado")
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('insurance', 'Seguro'),
        ('other', 'Otro'),
    ], blank=True, verbose_name="Método de pago")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_name()} ({self.start_datetime.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def duration(self):
        """Return duration in minutes"""
        if self.end_datetime and self.start_datetime:
            delta = self.end_datetime - self.start_datetime
            return int(delta.total_seconds() / 60)
        return self.appointment_type.duration_minutes
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        return self.start_datetime < timezone.now()
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        return self.start_datetime.date() == timezone.now().date()
    
    @property
    def can_be_cancelled(self):
        """Check if appointment can still be cancelled"""
        return self.status in ['scheduled', 'confirmed'] and not self.is_past
    
    def save(self, *args, **kwargs):
        # Auto-calculate end_datetime if not provided
        if not self.end_datetime and self.start_datetime:
            self.end_datetime = self.start_datetime + timezone.timedelta(minutes=self.appointment_type.duration_minutes)
        
        # Copy patient contact info if not provided
        if not self.patient_phone and self.patient.phone_number:
            self.patient_phone = self.patient.phone_number
        if not self.patient_email and self.patient.email:
            self.patient_email = self.patient.email
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['start_datetime']


class AppointmentTemplate(models.Model):
    """
    Template for recurring appointments
    """
    RECURRENCE_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('custom', 'Personalizado'),
    ]
    
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_templates')
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointment_templates')
    
    name = models.CharField(max_length=100, verbose_name="Nombre de la plantilla")
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, verbose_name="Tipo de recurrencia")
    recurrence_interval = models.IntegerField(default=1, verbose_name="Intervalo de recurrencia")
    
    # Time settings
    start_time = models.TimeField(verbose_name="Hora de inicio")
    duration_minutes = models.IntegerField(verbose_name="Duración (minutos)")
    
    # Days of week (for weekly recurrence)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    
    # Date range
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.doctor.get_full_name()}"
    
    @property
    def selected_weekdays(self):
        """Return list of selected weekdays"""
        days = []
        if self.monday: days.append(0)
        if self.tuesday: days.append(1)
        if self.wednesday: days.append(2)
        if self.thursday: days.append(3)
        if self.friday: days.append(4)
        if self.saturday: days.append(5)
        if self.sunday: days.append(6)
        return days
    
    class Meta:
        verbose_name = "Plantilla de Cita"
        verbose_name_plural = "Plantillas de Cita"


class AppointmentNote(models.Model):
    """
    Notes and observations during appointments
    """
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation_note')
    
    # Chief complaint and history
    chief_complaint = models.TextField(verbose_name="Motivo de consulta")
    present_illness_history = models.TextField(blank=True, verbose_name="Historia de enfermedad actual")
    
    # Physical examination
    physical_examination = models.TextField(blank=True, verbose_name="Exploración física")
    
    # Assessment and diagnosis
    assessment = models.TextField(blank=True, verbose_name="Evaluación")
    diagnosis = models.TextField(blank=True, verbose_name="Diagnóstico")
    differential_diagnosis = models.TextField(blank=True, verbose_name="Diagnóstico diferencial")
    
    # Treatment plan
    treatment_plan = models.TextField(blank=True, verbose_name="Plan de tratamiento")
    medications = models.TextField(blank=True, verbose_name="Medicamentos")
    recommendations = models.TextField(blank=True, verbose_name="Recomendaciones")
    
    # Follow-up
    follow_up_needed = models.BooleanField(default=False, verbose_name="Requiere seguimiento")
    follow_up_date = models.DateField(null=True, blank=True, verbose_name="Fecha de seguimiento")
    referral_needed = models.BooleanField(default=False, verbose_name="Requiere referencia")
    referral_to = models.CharField(max_length=200, blank=True, verbose_name="Referir a")
    
    # Additional notes
    additional_notes = models.TextField(blank=True, verbose_name="Notas adicionales")
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Nota de consulta - {self.appointment.patient.get_full_name()} ({self.appointment.start_datetime.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Nota de Consulta"
        verbose_name_plural = "Notas de Consulta"


class AppointmentReminder(models.Model):
    """
    Appointment reminders management
    """
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('call', 'Llamada telefónica'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregado'),
        ('failed', 'Falló'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, verbose_name="Tipo de recordatorio")
    
    # Timing
    send_datetime = models.DateTimeField(verbose_name="Fecha y hora de envío")
    hours_before = models.IntegerField(verbose_name="Horas antes de la cita")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado el")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de error")
    
    # Content
    message = models.TextField(verbose_name="Mensaje")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recordatorio {self.get_reminder_type_display()} - {self.appointment.patient.get_full_name()}"
    
    class Meta:
        verbose_name = "Recordatorio de Cita"
        verbose_name_plural = "Recordatorios de Cita"
        ordering = ['send_datetime']


class DoctorSchedule(models.Model):
    """
    Doctor's working schedule and availability
    """
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules', limit_choices_to={'role': 'doctor'})
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='doctor_schedules')
    
    # Day of the week (0=Monday, 6=Sunday)
    day_of_week = models.IntegerField(choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ], verbose_name="Día de la semana")
    
    start_time = models.TimeField(verbose_name="Hora de inicio")
    end_time = models.TimeField(verbose_name="Hora de fin")
    
    # Break time
    break_start = models.TimeField(null=True, blank=True, verbose_name="Inicio de descanso")
    break_end = models.TimeField(null=True, blank=True, verbose_name="Fin de descanso")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        return f"{self.doctor.get_full_name()} - {days[self.day_of_week]} ({self.start_time}-{self.end_time})"
    
    class Meta:
        verbose_name = "Horario del Médico"
        verbose_name_plural = "Horarios de los Médicos"
        unique_together = ['doctor', 'day_of_week', 'start_time']


class AppointmentBlock(models.Model):
    """
    Blocked time slots when doctors are not available
    """
    BLOCK_TYPES = [
        ('vacation', 'Vacaciones'),
        ('sick_leave', 'Incapacidad'),
        ('conference', 'Conferencia'),
        ('surgery', 'Cirugía'),
        ('emergency', 'Emergencia'),
        ('personal', 'Personal'),
        ('other', 'Otro'),
    ]
    
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_blocks')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='appointment_blocks')
    
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, verbose_name="Tipo de bloqueo")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    start_datetime = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    end_datetime = models.DateTimeField(verbose_name="Fecha y hora de fin")
    
    all_day = models.BooleanField(default=False, verbose_name="Todo el día")
    recurring = models.BooleanField(default=False, verbose_name="Recurrente")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_blocks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.doctor.get_full_name()} ({self.start_datetime.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Bloqueo de Citas"
        verbose_name_plural = "Bloqueos de Citas"
        ordering = ['start_datetime']
