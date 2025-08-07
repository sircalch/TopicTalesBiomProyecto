from rest_framework import serializers
from django.contrib.auth import get_user_model

from patients.models import Patient
from appointments.models import Appointment
from medical_records.models import MedicalRecord
from specialties.models import Specialty, Doctor, SpecialtyConsultation
from reports.models import Report
from billing.models import Invoice, Payment
from accounts.models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

class PatientSerializer(serializers.ModelSerializer):
    """Serializer para pacientes"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'birth_date', 'age', 'gender', 'address', 'city', 'state',
            'emergency_contact', 'emergency_phone', 'insurance_info',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class DoctorSerializer(serializers.ModelSerializer):
    """Serializer para doctores"""
    user = UserSerializer(read_only=True)
    specialties = serializers.StringRelatedField(many=True, read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'full_name', 'specialties', 'license_number',
            'education', 'certifications', 'years_experience', 'bio',
            'is_active', 'accepts_new_patients', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SpecialtySerializer(serializers.ModelSerializer):
    """Serializer para especialidades"""
    doctors_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Specialty
        fields = [
            'id', 'name', 'description', 'code', 'requires_referral',
            'consultation_price', 'follow_up_price', 'is_active',
            'doctors_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer para citas"""
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor = UserSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_id', 'patient_name', 'doctor', 'doctor_id', 'doctor_name',
            'appointment_date', 'appointment_type', 'status', 'duration', 'notes',
            'is_urgent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer para expedientes médicos"""
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor = UserSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_id', 'patient_name', 'doctor', 'doctor_id', 'doctor_name',
            'consultation_date', 'chief_complaint', 'symptoms', 'physical_examination',
            'diagnosis', 'treatment_plan', 'medications', 'follow_up_date',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SpecialtyConsultationSerializer(serializers.ModelSerializer):
    """Serializer para consultas de especialidad"""
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    specialty = SpecialtySerializer(read_only=True)
    specialty_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SpecialtyConsultation
        fields = [
            'id', 'patient', 'patient_id', 'doctor', 'doctor_id', 'specialty', 'specialty_id',
            'consultation_type', 'date', 'chief_complaint', 'symptoms', 'physical_examination',
            'diagnosis', 'treatment_plan', 'medications', 'follow_up_date',
            'follow_up_instructions', 'referral_needed', 'referral_specialty',
            'referral_reason', 'is_completed', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    """Serializer para reportes"""
    created_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'description', 'report_type', 'type_display', 'status',
            'status_display', 'date_from', 'date_to', 'created_by', 'created_at',
            'updated_at', 'file_format', 'file_size_mb', 'is_ready', 'is_scheduled'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_file_size_mb(self, obj):
        """Convertir tamaño de archivo a MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0

class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer para facturas"""
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'patient', 'patient_id', 'patient_name',
            'issue_date', 'due_date', 'subtotal', 'tax_amount', 'total_amount',
            'status', 'status_display', 'payment_terms', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    invoice = InvoiceSerializer(read_only=True)
    invoice_id = serializers.IntegerField(write_only=True)
    patient_name = serializers.CharField(source='invoice.patient.get_full_name()', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'invoice', 'invoice_id', 'patient_name',
            'amount', 'payment_date', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'transaction_id', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_number', 'created_at', 'updated_at']

# Serializers adicionales para casos específicos
class PatientSummarySerializer(serializers.ModelSerializer):
    """Serializer resumido para pacientes"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'email', 'phone', 'is_active']

class AppointmentCalendarSerializer(serializers.ModelSerializer):
    """Serializer para eventos del calendario"""
    title = serializers.SerializerMethodField()
    start = serializers.DateTimeField(source='appointment_date')
    end = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'title', 'start', 'end', 'status']
    
    def get_title(self, obj):
        return f"{obj.patient.get_full_name()} - {obj.appointment_type}"
    
    def get_end(self, obj):
        from django.utils import timezone
        return obj.appointment_date + timezone.timedelta(minutes=obj.duration)

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_patients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    appointments_today = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    total_consultations = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class SearchResultSerializer(serializers.Serializer):
    """Serializer para resultados de búsqueda"""
    patients = PatientSummarySerializer(many=True)
    appointments = AppointmentSerializer(many=True)
    specialties = SpecialtySerializer(many=True)

class ErrorSerializer(serializers.Serializer):
    """Serializer para errores de la API"""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.CharField(required=False)

class SuccessSerializer(serializers.Serializer):
    """Serializer para respuestas exitosas"""
    status = serializers.CharField()
    message = serializers.CharField(required=False)
    data = serializers.DictField(required=False)