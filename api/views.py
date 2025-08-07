from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    PatientSerializer, AppointmentSerializer, MedicalRecordSerializer,
    SpecialtySerializer, DoctorSerializer, SpecialtyConsultationSerializer,
    ReportSerializer, InvoiceSerializer, PaymentSerializer, UserSerializer
)

from patients.models import Patient
from appointments.models import Appointment
from medical_records.models import MedicalRecord
from specialties.models import Specialty, Doctor, SpecialtyConsultation, SpecialtyProcedure
from reports.models import Report
from billing.models import Invoice, Payment
from accounts.models import User, SystemModule

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# ViewSets principales
class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pacientes"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Patient.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Obtener citas de un paciente"""
        patient = self.get_object()
        appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def medical_records(self, request, pk=None):
        """Obtener expedientes médicos de un paciente"""
        patient = self.get_object()
        records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)

class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de citas"""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        # Filtros
        status_filter = self.request.query_params.get('status', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        doctor_id = self.request.query_params.get('doctor', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_from:
            queryset = queryset.filter(appointment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__date__lte=date_to)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        return queryset.order_by('-appointment_date')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar cita como completada"""
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.save()
        return Response({'status': 'appointment completed'})

class MedicalRecordViewSet(viewsets.ModelViewSet):
    """ViewSet para expedientes médicos"""
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = MedicalRecord.objects.select_related('patient', 'doctor')
        patient_id = self.request.query_params.get('patient', None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.order_by('-created_at')

class SpecialtyViewSet(viewsets.ModelViewSet):
    """ViewSet para especialidades médicas"""
    queryset = Specialty.objects.filter(is_active=True)
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def doctors(self, request, pk=None):
        """Obtener doctores de una especialidad"""
        specialty = self.get_object()
        doctors = Doctor.objects.filter(specialties=specialty, is_active=True)
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def procedures(self, request, pk=None):
        """Obtener procedimientos de una especialidad"""
        specialty = self.get_object()
        procedures = SpecialtyProcedure.objects.filter(specialty=specialty, is_active=True)
        procedures_data = [
            {
                'id': proc.id,
                'name': proc.name,
                'duration_minutes': proc.duration_minutes,
                'price': float(proc.price),
                'requires_anesthesia': proc.requires_anesthesia,
                'requires_fasting': proc.requires_fasting
            }
            for proc in procedures
        ]
        return Response(procedures_data)

class DoctorViewSet(viewsets.ModelViewSet):
    """ViewSet para doctores"""
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

class SpecialtyConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet para consultas de especialidad"""
    queryset = SpecialtyConsultation.objects.all()
    serializer_class = SpecialtyConsultationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = SpecialtyConsultation.objects.select_related('patient', 'doctor', 'specialty')
        specialty_id = self.request.query_params.get('specialty', None)
        patient_id = self.request.query_params.get('patient', None)
        
        if specialty_id:
            queryset = queryset.filter(specialty_id=specialty_id)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
            
        return queryset.order_by('-date')

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet para reportes"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generar un reporte"""
        report = self.get_object()
        # Aquí iría la lógica de generación del reporte
        report.status = 'processing'
        report.save()
        return Response({'status': 'report generation started'})

class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet para facturas"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Invoice.objects.select_related('patient')
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Enviar factura por email"""
        invoice = self.get_object()
        # Aquí iría la lógica de envío de email
        invoice.status = 'sent'
        invoice.save()
        return Response({'status': 'invoice sent'})
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marcar factura como pagada"""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.save()
        return Response({'status': 'invoice marked as paid'})

class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagos"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Payment.objects.select_related('invoice', 'invoice__patient').order_by('-payment_date')

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para usuarios"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.all().order_by('-date_joined')
        else:
            return User.objects.filter(id=self.request.user.id)

# Vistas de función
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Obtener información del usuario actual"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Estadísticas para el dashboard"""
    stats = {
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'appointments_today': Appointment.objects.filter(
            appointment_date__date=timezone.now().date()
        ).count(),
        'pending_appointments': Appointment.objects.filter(
            status='scheduled'
        ).count(),
        'total_consultations': SpecialtyConsultation.objects.count(),
        'pending_invoices': Invoice.objects.filter(status='sent').count(),
        'total_revenue': Invoice.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """Actividad reciente del sistema"""
    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor'
    ).order_by('-created_at')[:5]
    
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    
    activity_data = {
        'recent_appointments': AppointmentSerializer(recent_appointments, many=True).data,
        'recent_patients': PatientSerializer(recent_patients, many=True).data,
    }
    return Response(activity_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """Búsqueda global en el sistema"""
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    # Buscar en pacientes
    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    )[:5]
    
    # Buscar en citas
    appointments = Appointment.objects.select_related('patient').filter(
        Q(patient__first_name__icontains=query) |
        Q(patient__last_name__icontains=query) |
        Q(notes__icontains=query)
    )[:5]
    
    # Buscar en especialidades
    specialties = Specialty.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:5]
    
    results = {
        'patients': PatientSerializer(patients, many=True).data,
        'appointments': AppointmentSerializer(appointments, many=True).data,
        'specialties': SpecialtySerializer(specialties, many=True).data,
    }
    
    return Response(results)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_appointments(request, patient_id):
    """Obtener citas de un paciente específico"""
    patient = get_object_or_404(Patient, pk=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_medical_records(request, patient_id):
    """Obtener expedientes médicos de un paciente"""
    patient = get_object_or_404(Patient, pk=patient_id)
    records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
    serializer = MedicalRecordSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_appointment(request, appointment_id):
    """Completar una cita"""
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.status = 'completed'
    appointment.save()
    return Response({'status': 'appointment completed'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointments_calendar(request):
    """Obtener citas para el calendario"""
    date_from = request.GET.get('start')
    date_to = request.GET.get('end')
    
    appointments = Appointment.objects.select_related('patient', 'doctor')
    
    if date_from:
        appointments = appointments.filter(appointment_date__date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__date__lte=date_to)
    
    calendar_events = []
    for apt in appointments:
        calendar_events.append({
            'id': apt.id,
            'title': f'{apt.patient.get_full_name()} - {apt.appointment_type}',
            'start': apt.appointment_date.isoformat(),
            'end': (apt.appointment_date + timezone.timedelta(minutes=apt.duration)).isoformat(),
            'backgroundColor': '#007bff' if apt.status == 'scheduled' else '#28a745',
            'borderColor': '#007bff' if apt.status == 'scheduled' else '#28a745',
            'textColor': '#fff'
        })
    
    return Response(calendar_events)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specialty_doctors(request, specialty_id):
    """Obtener doctores de una especialidad"""
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    doctors = Doctor.objects.filter(specialties=specialty, is_active=True)
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def specialty_procedures(request, specialty_id):
    """Obtener procedimientos de una especialidad"""
    specialty = get_object_or_404(Specialty, pk=specialty_id)
    procedures = SpecialtyProcedure.objects.filter(specialty=specialty, is_active=True)
    
    procedures_data = [
        {
            'id': proc.id,
            'name': proc.name,
            'duration_minutes': proc.duration_minutes,
            'price': float(proc.price),
            'requires_anesthesia': proc.requires_anesthesia,
            'requires_fasting': proc.requires_fasting
        }
        for proc in procedures
    ]
    
    return Response(procedures_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request, report_id):
    """Generar un reporte"""
    report = get_object_or_404(Report, pk=report_id, created_by=request.user)
    # Aquí iría la lógica de generación del reporte
    report.status = 'processing'
    report.save()
    return Response({'status': 'report generation started'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report_api(request, report_id):
    """Descargar un reporte via API"""
    report = get_object_or_404(Report, pk=report_id, created_by=request.user)
    if not report.is_ready:
        return Response({'error': 'Report not ready'}, status=400)
    
    # Aquí iría la lógica de descarga
    return Response({'download_url': f'/api/reports/{report_id}/file/'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invoice(request, invoice_id):
    """Enviar factura por email"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    # Aquí iría la lógica de envío de email
    invoice.status = 'sent'
    invoice.save()
    return Response({'status': 'invoice sent'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_invoice_paid(request, invoice_id):
    """Marcar factura como pagada"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    invoice.status = 'paid'
    invoice.save()
    return Response({'status': 'invoice marked as paid'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """Subir documento"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    # Aquí iría la lógica de subida de archivo
    
    return Response({
        'filename': file.name,
        'size': file.size,
        'url': f'/media/documents/{file.name}'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    """Subir imagen de perfil"""
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=400)
    
    image = request.FILES['image']
    # Aquí iría la lógica de subida de imagen
    
    return Response({
        'filename': image.name,
        'url': f'/media/profiles/{image.name}'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_modules(request):
    """Obtener módulos del sistema"""
    modules = SystemModule.objects.filter(is_active=True).order_by('name')
    modules_data = [
        {
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'is_active': module.is_active,
            'required_plan': module.required_plan
        }
        for module in modules
    ]
    return Response(modules_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_settings(request):
    """Obtener configuraciones del sistema"""
    # Esta sería la configuración básica del sistema
    settings_data = {
        'app_name': 'TopicTales Biomédica',
        'version': '1.0.0',
        'timezone': str(settings.TIME_ZONE),
        'language': settings.LANGUAGE_CODE,
        'max_file_size': getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 2621440),
        'allowed_file_types': ['.pdf', '.doc', '.docx', '.jpg', '.png'],
    }
    return Response(settings_data)