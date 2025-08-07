from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json

User = get_user_model()


class PsychologicalEvaluation(models.Model):
    """Evaluación psicológica completa del paciente"""
    
    EVALUATION_TYPE_CHOICES = [
        ('initial', 'Evaluación Inicial'),
        ('cognitive', 'Evaluación Cognitiva'),
        ('personality', 'Evaluación de Personalidad'),
        ('neuropsychological', 'Evaluación Neuropsicológica'),
        ('clinical', 'Evaluación Clínica'),
        ('educational', 'Evaluación Educativa'),
        ('occupational', 'Evaluación Ocupacional'),
    ]
    
    REFERRAL_SOURCE_CHOICES = [
        ('self', 'Autoref erencia'),
        ('family', 'Familia'),
        ('medical_doctor', 'Médico'),
        ('school', 'Escuela'),
        ('court', 'Legal/Judicial'),
        ('insurance', 'Aseguradora'),
        ('other', 'Otro'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='psychological_evaluations')
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='psychology_evaluations')
    
    # Información de la evaluación
    evaluation_type = models.CharField('Tipo de Evaluación', max_length=20, choices=EVALUATION_TYPE_CHOICES)
    evaluation_date = models.DateTimeField('Fecha de Evaluación')
    referral_source = models.CharField('Fuente de Referencia', max_length=20, choices=REFERRAL_SOURCE_CHOICES)
    referral_reason = models.TextField('Motivo de Referencia')
    
    # Historia clínica psicológica
    chief_complaint = models.TextField('Motivo de Consulta Principal')
    symptoms_duration = models.CharField('Duración de Síntomas', max_length=100, blank=True)
    previous_treatments = models.TextField('Tratamientos Previos', blank=True)
    medications = models.TextField('Medicamentos Actuales', blank=True)
    
    # Historia familiar
    family_mental_health = models.TextField('Antecedentes Familiares de Salud Mental', blank=True)
    family_relationships = models.TextField('Relaciones Familiares', blank=True)
    
    # Historia personal
    educational_background = models.TextField('Antecedentes Educativos', blank=True)
    occupational_history = models.TextField('Historia Laboral', blank=True)
    social_relationships = models.TextField('Relaciones Sociales', blank=True)
    substance_use = models.TextField('Uso de Sustancias', blank=True)
    
    # Observaciones del examen mental
    appearance = models.TextField('Apariencia y Comportamiento', blank=True)
    mood_affect = models.TextField('Estado de Ánimo y Afecto', blank=True)
    thought_process = models.TextField('Proceso de Pensamiento', blank=True)
    perception = models.TextField('Percepción', blank=True)
    cognition = models.TextField('Función Cognitiva', blank=True)
    insight_judgment = models.TextField('Insight y Juicio', blank=True)
    
    # Diagnóstico y recomendaciones
    provisional_diagnosis = models.TextField('Diagnóstico Provisional', blank=True)
    differential_diagnosis = models.TextField('Diagnóstico Diferencial', blank=True)
    recommendations = models.TextField('Recomendaciones')
    treatment_plan = models.TextField('Plan de Tratamiento', blank=True)
    
    # Puntuaciones de escalas (JSON para flexibilidad)
    scale_scores = models.JSONField('Puntuaciones de Escalas', default=dict, blank=True)
    
    # Estado y seguimiento
    is_completed = models.BooleanField('Evaluación Completada', default=False)
    follow_up_date = models.DateField('Fecha de Seguimiento', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Evaluación Psicológica'
        verbose_name_plural = 'Evaluaciones Psicológicas'
        ordering = ['-evaluation_date']
    
    def __str__(self):
        return f"Evaluación de {self.patient.get_full_name()} - {self.evaluation_date.strftime('%d/%m/%Y')}"


class PsychologicalTest(models.Model):
    """Tests psicológicos y escalas de evaluación"""
    
    TEST_CATEGORY_CHOICES = [
        ('intelligence', 'Inteligencia'),
        ('personality', 'Personalidad'),
        ('anxiety', 'Ansiedad'),
        ('depression', 'Depresión'),
        ('attention', 'Atención/TDAH'),
        ('memory', 'Memoria'),
        ('neuropsychological', 'Neuropsicológico'),
        ('projective', 'Proyectivo'),
        ('behavioral', 'Conductual'),
        ('social', 'Habilidades Sociales'),
    ]
    
    name = models.CharField('Nombre del Test', max_length=200)
    abbreviation = models.CharField('Abreviación', max_length=20, blank=True)
    category = models.CharField('Categoría', max_length=20, choices=TEST_CATEGORY_CHOICES)
    description = models.TextField('Descripción')
    age_range_min = models.IntegerField('Edad Mínima', validators=[MinValueValidator(0)])
    age_range_max = models.IntegerField('Edad Máxima', validators=[MaxValueValidator(120)])
    administration_time = models.IntegerField('Tiempo de Administración (minutos)')
    scoring_method = models.TextField('Método de Puntuación')
    interpretation_guide = models.TextField('Guía de Interpretación')
    is_active = models.BooleanField('Activo', default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Test Psicológico'
        verbose_name_plural = 'Tests Psicológicos'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})" if self.abbreviation else self.name


class TestResult(models.Model):
    """Resultados de tests psicológicos aplicados"""
    
    evaluation = models.ForeignKey(PsychologicalEvaluation, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE)
    administered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    administration_date = models.DateTimeField('Fecha de Aplicación')
    raw_scores = models.JSONField('Puntuaciones Brutas', default=dict)
    scaled_scores = models.JSONField('Puntuaciones Escalares', default=dict)
    percentiles = models.JSONField('Percentiles', default=dict)
    
    # Interpretación
    interpretation = models.TextField('Interpretación de Resultados')
    clinical_significance = models.TextField('Significancia Clínica', blank=True)
    recommendations = models.TextField('Recomendaciones Específicas', blank=True)
    
    # Validez del test
    validity_concerns = models.TextField('Preocupaciones de Validez', blank=True)
    test_behavior = models.TextField('Comportamiento Durante el Test', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Resultado de Test'
        verbose_name_plural = 'Resultados de Tests'
        ordering = ['-administration_date']
    
    def __str__(self):
        return f"{self.test.name} - {self.evaluation.patient.get_full_name()}"


class TherapySession(models.Model):
    """Sesiones de terapia psicológica"""
    
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Grupal'),
        ('family', 'Familiar'),
        ('couple', 'Pareja'),
        ('play', 'Terapia de Juego'),
        ('behavioral', 'Conductual'),
        ('cognitive', 'Cognitiva'),
        ('psychodynamic', 'Psicodinámica'),
        ('humanistic', 'Humanística'),
    ]
    
    SESSION_STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No Asistió'),
        ('rescheduled', 'Reprogramada'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='therapy_sessions')
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapy_sessions')
    evaluation = models.ForeignKey(PsychologicalEvaluation, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información de la sesión
    session_number = models.IntegerField('Número de Sesión')
    session_date = models.DateTimeField('Fecha y Hora')
    session_type = models.CharField('Tipo de Sesión', max_length=20, choices=SESSION_TYPE_CHOICES)
    duration_minutes = models.IntegerField('Duración (minutos)', default=50)
    status = models.CharField('Estado', max_length=20, choices=SESSION_STATUS_CHOICES, default='scheduled')
    
    # Contenido de la sesión
    session_goals = models.TextField('Objetivos de la Sesión', blank=True)
    interventions_used = models.TextField('Intervenciones Utilizadas', blank=True)
    patient_mood = models.CharField('Estado de Ánimo del Paciente', max_length=100, blank=True)
    patient_participation = models.TextField('Participación del Paciente', blank=True)
    
    # Progreso y observaciones
    progress_notes = models.TextField('Notas de Progreso')
    homework_assigned = models.TextField('Tareas Asignadas', blank=True)
    homework_review = models.TextField('Revisión de Tareas Previas', blank=True)
    
    # Crisis y factores de riesgo
    risk_assessment = models.TextField('Evaluación de Riesgo', blank=True)
    crisis_intervention = models.TextField('Intervención en Crisis', blank=True)
    safety_plan = models.TextField('Plan de Seguridad', blank=True)
    
    # Próxima sesión
    next_session_date = models.DateTimeField('Próxima Sesión', null=True, blank=True)
    next_session_goals = models.TextField('Objetivos Próxima Sesión', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sesión de Terapia'
        verbose_name_plural = 'Sesiones de Terapia'
        ordering = ['-session_date']
        unique_together = ['patient', 'session_number']
    
    def __str__(self):
        return f"Sesión {self.session_number} - {self.patient.get_full_name()}"


class TreatmentPlan(models.Model):
    """Plan de tratamiento psicológico"""
    
    TREATMENT_APPROACH_CHOICES = [
        ('cbt', 'Terapia Cognitivo-Conductual'),
        ('psychodynamic', 'Psicoterapia Psicodinámica'),
        ('humanistic', 'Terapia Humanística'),
        ('behavioral', 'Terapia Conductual'),
        ('family_systems', 'Terapia Familiar Sistémica'),
        ('gestalt', 'Terapia Gestalt'),
        ('solution_focused', 'Terapia Centrada en Soluciones'),
        ('dbt', 'Terapia Dialéctica Conductual'),
        ('emdr', 'EMDR'),
        ('integrative', 'Enfoque Integrativo'),
    ]
    
    PRIORITY_LEVEL_CHOICES = [
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    evaluation = models.OneToOneField(PsychologicalEvaluation, on_delete=models.CASCADE, related_name='psychological_treatment_plan')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Información del plan
    treatment_approach = models.CharField('Enfoque Terapéutico', max_length=20, choices=TREATMENT_APPROACH_CHOICES)
    estimated_sessions = models.IntegerField('Sesiones Estimadas', validators=[MinValueValidator(1)])
    session_frequency = models.CharField('Frecuencia de Sesiones', max_length=100)
    estimated_duration = models.CharField('Duración Estimada', max_length=100)
    
    # Objetivos del tratamiento
    primary_objectives = models.TextField('Objetivos Primarios')
    secondary_objectives = models.TextField('Objetivos Secundarios', blank=True)
    measurable_goals = models.TextField('Metas Medibles')
    
    # Intervenciones específicas
    therapeutic_techniques = models.TextField('Técnicas Terapéuticas')
    homework_assignments = models.TextField('Tareas Terapéuticas', blank=True)
    family_involvement = models.TextField('Participación Familiar', blank=True)
    
    # Evaluación del progreso
    progress_indicators = models.TextField('Indicadores de Progreso')
    review_frequency = models.CharField('Frecuencia de Revisión', max_length=100)
    
    # Factores especiales
    risk_factors = models.TextField('Factores de Riesgo', blank=True)
    protective_factors = models.TextField('Factores Protectores', blank=True)
    barriers_to_treatment = models.TextField('Barreras al Tratamiento', blank=True)
    
    # Coordinación de cuidados
    referrals_needed = models.TextField('Referencias Necesarias', blank=True)
    collaboration_notes = models.TextField('Coordinación con Otros Profesionales', blank=True)
    
    # Estado del plan
    is_active = models.BooleanField('Plan Activo', default=True)
    start_date = models.DateField('Fecha de Inicio')
    review_date = models.DateField('Fecha de Revisión', null=True, blank=True)
    completion_date = models.DateField('Fecha de Finalización', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan de Tratamiento'
        verbose_name_plural = 'Planes de Tratamiento'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Plan de Tratamiento - {self.evaluation.patient.get_full_name()}"
    
    def get_progress_percentage(self):
        """Calcula el porcentaje de progreso basado en sesiones completadas"""
        completed_sessions = self.evaluation.patient.therapy_sessions.filter(status='completed').count()
        if self.estimated_sessions > 0:
            return min(100, (completed_sessions / self.estimated_sessions) * 100)
        return 0


class PsychologicalGoal(models.Model):
    """Objetivos específicos del tratamiento psicológico"""
    
    GOAL_TYPE_CHOICES = [
        ('symptom_reduction', 'Reducción de Síntomas'),
        ('skill_building', 'Desarrollo de Habilidades'),
        ('behavioral_change', 'Cambio Conductual'),
        ('emotional_regulation', 'Regulación Emocional'),
        ('relationship_improvement', 'Mejora de Relaciones'),
        ('academic_performance', 'Rendimiento Académico'),
        ('occupational_functioning', 'Funcionamiento Laboral'),
        ('self_esteem', 'Autoestima'),
        ('coping_skills', 'Habilidades de Afrontamiento'),
        ('social_skills', 'Habilidades Sociales'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('achieved', 'Logrado'),
        ('modified', 'Modificado'),
        ('discontinued', 'Descontinuado'),
    ]
    
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name='goals')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    goal_type = models.CharField('Tipo de Objetivo', max_length=30, choices=GOAL_TYPE_CHOICES)
    title = models.CharField('Título del Objetivo', max_length=200)
    description = models.TextField('Descripción Detallada')
    
    # Criterios de éxito
    success_criteria = models.TextField('Criterios de Éxito')
    measurement_method = models.TextField('Método de Medición')
    target_value = models.CharField('Valor Objetivo', max_length=100, blank=True)
    current_progress = models.TextField('Progreso Actual', blank=True)
    
    # Fechas y estado
    start_date = models.DateField('Fecha de Inicio')
    target_date = models.DateField('Fecha Objetivo')
    achieved_date = models.DateField('Fecha de Logro', null=True, blank=True)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Prioridad y dificultad
    priority = models.IntegerField('Prioridad', choices=[(1, 'Baja'), (2, 'Media'), (3, 'Alta'), (4, 'Crítica')], default=2)
    difficulty_level = models.IntegerField('Nivel de Dificultad', choices=[(1, 'Fácil'), (2, 'Moderado'), (3, 'Difícil'), (4, 'Muy Difícil')], default=2)
    
    # Seguimiento
    progress_notes = models.TextField('Notas de Progreso', blank=True)
    obstacles = models.TextField('Obstáculos Encontrados', blank=True)
    interventions = models.TextField('Intervenciones Específicas', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Objetivo Psicológico'
        verbose_name_plural = 'Objetivos Psicológicos'
        ordering = ['-priority', 'target_date']
    
    def __str__(self):
        return f"{self.title} - {self.treatment_plan.evaluation.patient.get_full_name()}"
    
    def get_days_remaining(self):
        """Calcula los días restantes para el objetivo"""
        from datetime import date
        if self.target_date:
            delta = self.target_date - date.today()
            return delta.days
        return 0
