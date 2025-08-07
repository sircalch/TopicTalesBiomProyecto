from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML
from crispy_forms.bootstrap import Field, PrependedText, AppendedText
from .models import (
    PsychologicalEvaluation, PsychologicalTest, TestResult, 
    TherapySession, TreatmentPlan, PsychologicalGoal
)
from patients.models import Patient

User = get_user_model()


class PsychologicalEvaluationForm(forms.ModelForm):
    """Formulario para evaluaciones psicológicas"""
    
    class Meta:
        model = PsychologicalEvaluation
        fields = [
            'patient', 'evaluation_type', 'evaluation_date', 'referral_source',
            'referral_reason', 'chief_complaint', 'symptoms_duration', 
            'previous_treatments', 'medications', 'family_mental_health',
            'family_relationships', 'educational_background', 'occupational_history',
            'social_relationships', 'substance_use', 'appearance', 'mood_affect',
            'thought_process', 'perception', 'cognition', 'insight_judgment',
            'provisional_diagnosis', 'differential_diagnosis', 'recommendations',
            'treatment_plan', 'scale_scores', 'is_completed', 'follow_up_date'
        ]
        widgets = {
            'evaluation_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'referral_reason': forms.Textarea(attrs={'rows': 3}),
            'chief_complaint': forms.Textarea(attrs={'rows': 4}),
            'previous_treatments': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'family_mental_health': forms.Textarea(attrs={'rows': 3}),
            'family_relationships': forms.Textarea(attrs={'rows': 3}),
            'educational_background': forms.Textarea(attrs={'rows': 3}),
            'occupational_history': forms.Textarea(attrs={'rows': 3}),
            'social_relationships': forms.Textarea(attrs={'rows': 3}),
            'substance_use': forms.Textarea(attrs={'rows': 3}),
            'appearance': forms.Textarea(attrs={'rows': 4}),
            'mood_affect': forms.Textarea(attrs={'rows': 4}),
            'thought_process': forms.Textarea(attrs={'rows': 4}),
            'perception': forms.Textarea(attrs={'rows': 3}),
            'cognition': forms.Textarea(attrs={'rows': 4}),
            'insight_judgment': forms.Textarea(attrs={'rows': 3}),
            'provisional_diagnosis': forms.Textarea(attrs={'rows': 4}),
            'differential_diagnosis': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 5}),
            'treatment_plan': forms.Textarea(attrs={'rows': 5}),
            'scale_scores': forms.Textarea(attrs={'placeholder': 'Formato JSON: {"escala": "puntuacion", ...}'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-user-check me-2"></i>Información de la Evaluación</h5></div>'),
            Row(
                Column('patient', css_class='form-group col-md-6 mb-3'),
                Column('evaluation_type', css_class='form-group col-md-3 mb-3'),
                Column('evaluation_date', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column('referral_source', css_class='form-group col-md-4 mb-3'),
                Column('referral_reason', css_class='form-group col-md-8 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-comments me-2"></i>Historia Clínica</h5></div>'),
            'chief_complaint',
            Row(
                Column('symptoms_duration', css_class='form-group col-md-4 mb-3'),
                Column('previous_treatments', css_class='form-group col-md-4 mb-3'),
                Column('medications', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-users me-2"></i>Historia Familiar y Personal</h5></div>'),
            Row(
                Column('family_mental_health', css_class='form-group col-md-6 mb-3'),
                Column('family_relationships', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('educational_background', css_class='form-group col-md-4 mb-3'),
                Column('occupational_history', css_class='form-group col-md-4 mb-3'),
                Column('social_relationships', css_class='form-group col-md-4 mb-3'),
            ),
            'substance_use',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-brain me-2"></i>Examen del Estado Mental</h5></div>'),
            Row(
                Column('appearance', css_class='form-group col-md-6 mb-3'),
                Column('mood_affect', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('thought_process', css_class='form-group col-md-4 mb-3'),
                Column('perception', css_class='form-group col-md-4 mb-3'),
                Column('cognition', css_class='form-group col-md-4 mb-3'),
            ),
            'insight_judgment',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-stethoscope me-2"></i>Diagnóstico y Plan</h5></div>'),
            Row(
                Column('provisional_diagnosis', css_class='form-group col-md-6 mb-3'),
                Column('differential_diagnosis', css_class='form-group col-md-6 mb-3'),
            ),
            'recommendations',
            'treatment_plan',
            'scale_scores',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-check-circle me-2"></i>Estado y Seguimiento</h5></div>'),
            Row(
                Column('is_completed', css_class='form-group col-md-6 mb-3'),
                Column('follow_up_date', css_class='form-group col-md-6 mb-3'),
            ),
            
            Div(
                Submit('submit', 'Guardar Evaluación', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class PsychologicalTestForm(forms.ModelForm):
    """Formulario para tests psicológicos"""
    
    class Meta:
        model = PsychologicalTest
        fields = [
            'name', 'abbreviation', 'category', 'description', 'age_range_min',
            'age_range_max', 'administration_time', 'scoring_method', 
            'interpretation_guide', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'scoring_method': forms.Textarea(attrs={'rows': 4}),
            'interpretation_guide': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-clipboard-list me-2"></i>Información del Test</h5></div>'),
            Row(
                Column('name', css_class='form-group col-md-8 mb-3'),
                Column('abbreviation', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('category', css_class='form-group col-md-6 mb-3'),
                Column('is_active', css_class='form-group col-md-6 mb-3'),
            ),
            'description',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-users me-2"></i>Parámetros de Aplicación</h5></div>'),
            Row(
                Column(AppendedText('age_range_min', 'años'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('age_range_max', 'años'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('administration_time', 'minutos'), css_class='form-group col-md-4 mb-3'),
            ),
            'scoring_method',
            'interpretation_guide',
            
            Div(
                Submit('submit', 'Guardar Test', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class TestResultForm(forms.ModelForm):
    """Formulario para resultados de tests"""
    
    class Meta:
        model = TestResult
        fields = [
            'evaluation', 'test', 'administration_date', 'raw_scores',
            'scaled_scores', 'percentiles', 'interpretation', 
            'clinical_significance', 'recommendations', 'validity_concerns',
            'test_behavior'
        ]
        widgets = {
            'administration_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'raw_scores': forms.Textarea(attrs={'placeholder': 'Formato JSON: {"subtest": "puntuacion", ...}'}),
            'scaled_scores': forms.Textarea(attrs={'placeholder': 'Formato JSON: {"subtest": "puntuacion_escalar", ...}'}),
            'percentiles': forms.Textarea(attrs={'placeholder': 'Formato JSON: {"subtest": "percentil", ...}'}),
            'interpretation': forms.Textarea(attrs={'rows': 5}),
            'clinical_significance': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
            'validity_concerns': forms.Textarea(attrs={'rows': 3}),
            'test_behavior': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-chart-bar me-2"></i>Información del Resultado</h5></div>'),
            Row(
                Column('evaluation', css_class='form-group col-md-6 mb-3'),
                Column('test', css_class='form-group col-md-6 mb-3'),
            ),
            'administration_date',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-calculator me-2"></i>Puntuaciones</h5></div>'),
            Row(
                Column('raw_scores', css_class='form-group col-md-4 mb-3'),
                Column('scaled_scores', css_class='form-group col-md-4 mb-3'),
                Column('percentiles', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-microscope me-2"></i>Interpretación y Validez</h5></div>'),
            'interpretation',
            Row(
                Column('clinical_significance', css_class='form-group col-md-6 mb-3'),
                Column('recommendations', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('validity_concerns', css_class='form-group col-md-6 mb-3'),
                Column('test_behavior', css_class='form-group col-md-6 mb-3'),
            ),
            
            Div(
                Submit('submit', 'Guardar Resultado', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class TherapySessionForm(forms.ModelForm):
    """Formulario para sesiones de terapia"""
    
    class Meta:
        model = TherapySession
        fields = [
            'patient', 'evaluation', 'session_number', 'session_date', 
            'session_type', 'duration_minutes', 'status', 'session_goals',
            'interventions_used', 'patient_mood', 'patient_participation',
            'progress_notes', 'homework_assigned', 'homework_review',
            'risk_assessment', 'crisis_intervention', 'safety_plan',
            'next_session_date', 'next_session_goals'
        ]
        widgets = {
            'session_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'next_session_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'session_goals': forms.Textarea(attrs={'rows': 3}),
            'interventions_used': forms.Textarea(attrs={'rows': 4}),
            'patient_participation': forms.Textarea(attrs={'rows': 3}),
            'progress_notes': forms.Textarea(attrs={'rows': 5}),
            'homework_assigned': forms.Textarea(attrs={'rows': 3}),
            'homework_review': forms.Textarea(attrs={'rows': 3}),
            'risk_assessment': forms.Textarea(attrs={'rows': 3}),
            'crisis_intervention': forms.Textarea(attrs={'rows': 4}),
            'safety_plan': forms.Textarea(attrs={'rows': 4}),
            'next_session_goals': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-calendar-check me-2"></i>Información de la Sesión</h5></div>'),
            Row(
                Column('patient', css_class='form-group col-md-6 mb-3'),
                Column('evaluation', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('session_number', css_class='form-group col-md-3 mb-3'),
                Column('session_date', css_class='form-group col-md-3 mb-3'),
                Column('session_type', css_class='form-group col-md-3 mb-3'),
                Column('status', css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column(AppendedText('duration_minutes', 'min'), css_class='form-group col-md-6 mb-3'),
                Column('patient_mood', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-tasks me-2"></i>Contenido de la Sesión</h5></div>'),
            'session_goals',
            'interventions_used',
            'patient_participation',
            'progress_notes',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-home me-2"></i>Tareas y Seguimiento</h5></div>'),
            Row(
                Column('homework_assigned', css_class='form-group col-md-6 mb-3'),
                Column('homework_review', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-exclamation-triangle me-2"></i>Evaluación de Riesgo</h5></div>'),
            'risk_assessment',
            Row(
                Column('crisis_intervention', css_class='form-group col-md-6 mb-3'),
                Column('safety_plan', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-forward me-2"></i>Próxima Sesión</h5></div>'),
            Row(
                Column('next_session_date', css_class='form-group col-md-6 mb-3'),
                Column('next_session_goals', css_class='form-group col-md-6 mb-3'),
            ),
            
            Div(
                Submit('submit', 'Guardar Sesión', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class TreatmentPlanForm(forms.ModelForm):
    """Formulario para planes de tratamiento"""
    
    class Meta:
        model = TreatmentPlan
        fields = [
            'evaluation', 'treatment_approach', 'estimated_sessions',
            'session_frequency', 'estimated_duration', 'primary_objectives',
            'secondary_objectives', 'measurable_goals', 'therapeutic_techniques',
            'homework_assignments', 'family_involvement', 'progress_indicators',
            'review_frequency', 'risk_factors', 'protective_factors',
            'barriers_to_treatment', 'referrals_needed', 'collaboration_notes',
            'is_active', 'start_date', 'review_date', 'completion_date'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'review_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'primary_objectives': forms.Textarea(attrs={'rows': 4}),
            'secondary_objectives': forms.Textarea(attrs={'rows': 3}),
            'measurable_goals': forms.Textarea(attrs={'rows': 4}),
            'therapeutic_techniques': forms.Textarea(attrs={'rows': 4}),
            'homework_assignments': forms.Textarea(attrs={'rows': 3}),
            'family_involvement': forms.Textarea(attrs={'rows': 3}),
            'progress_indicators': forms.Textarea(attrs={'rows': 3}),
            'risk_factors': forms.Textarea(attrs={'rows': 3}),
            'protective_factors': forms.Textarea(attrs={'rows': 3}),
            'barriers_to_treatment': forms.Textarea(attrs={'rows': 3}),
            'referrals_needed': forms.Textarea(attrs={'rows': 3}),
            'collaboration_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-map me-2"></i>Información del Plan</h5></div>'),
            Row(
                Column('evaluation', css_class='form-group col-md-6 mb-3'),
                Column('treatment_approach', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('estimated_sessions', css_class='form-group col-md-4 mb-3'),
                Column('session_frequency', css_class='form-group col-md-4 mb-3'),
                Column('estimated_duration', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-bullseye me-2"></i>Objetivos del Tratamiento</h5></div>'),
            'primary_objectives',
            Row(
                Column('secondary_objectives', css_class='form-group col-md-6 mb-3'),
                Column('measurable_goals', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-tools me-2"></i>Intervenciones Específicas</h5></div>'),
            'therapeutic_techniques',
            Row(
                Column('homework_assignments', css_class='form-group col-md-6 mb-3'),
                Column('family_involvement', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-chart-line me-2"></i>Evaluación del Progreso</h5></div>'),
            Row(
                Column('progress_indicators', css_class='form-group col-md-6 mb-3'),
                Column('review_frequency', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-shield-alt me-2"></i>Factores Especiales</h5></div>'),
            Row(
                Column('risk_factors', css_class='form-group col-md-4 mb-3'),
                Column('protective_factors', css_class='form-group col-md-4 mb-3'),
                Column('barriers_to_treatment', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-handshake me-2"></i>Coordinación de Cuidados</h5></div>'),
            Row(
                Column('referrals_needed', css_class='form-group col-md-6 mb-3'),
                Column('collaboration_notes', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-calendar-alt me-2"></i>Estado del Plan</h5></div>'),
            Row(
                Column('is_active', css_class='form-group col-md-3 mb-3'),
                Column('start_date', css_class='form-group col-md-3 mb-3'),
                Column('review_date', css_class='form-group col-md-3 mb-3'),
                Column('completion_date', css_class='form-group col-md-3 mb-3'),
            ),
            
            Div(
                Submit('submit', 'Guardar Plan de Tratamiento', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class PsychologicalGoalForm(forms.ModelForm):
    """Formulario para objetivos psicológicos"""
    
    class Meta:
        model = PsychologicalGoal
        fields = [
            'treatment_plan', 'goal_type', 'title', 'description',
            'success_criteria', 'measurement_method', 'target_value',
            'current_progress', 'start_date', 'target_date', 'achieved_date',
            'status', 'priority', 'difficulty_level', 'progress_notes',
            'obstacles', 'interventions'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'achieved_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'success_criteria': forms.Textarea(attrs={'rows': 3}),
            'measurement_method': forms.Textarea(attrs={'rows': 3}),
            'current_progress': forms.Textarea(attrs={'rows': 3}),
            'progress_notes': forms.Textarea(attrs={'rows': 4}),
            'obstacles': forms.Textarea(attrs={'rows': 3}),
            'interventions': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<div class="section-header"><h5><i class="fas fa-bullseye me-2"></i>Información del Objetivo</h5></div>'),
            Row(
                Column('treatment_plan', css_class='form-group col-md-6 mb-3'),
                Column('goal_type', css_class='form-group col-md-6 mb-3'),
            ),
            'title',
            'description',
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-check-circle me-2"></i>Criterios de Éxito</h5></div>'),
            Row(
                Column('success_criteria', css_class='form-group col-md-6 mb-3'),
                Column('measurement_method', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('target_value', css_class='form-group col-md-6 mb-3'),
                Column('current_progress', css_class='form-group col-md-6 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-calendar me-2"></i>Fechas y Estado</h5></div>'),
            Row(
                Column('start_date', css_class='form-group col-md-4 mb-3'),
                Column('target_date', css_class='form-group col-md-4 mb-3'),
                Column('achieved_date', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('status', css_class='form-group col-md-4 mb-3'),
                Column('priority', css_class='form-group col-md-4 mb-3'),
                Column('difficulty_level', css_class='form-group col-md-4 mb-3'),
            ),
            
            HTML('<div class="section-header mt-4"><h5><i class="fas fa-notes-medical me-2"></i>Seguimiento</h5></div>'),
            'progress_notes',
            Row(
                Column('obstacles', css_class='form-group col-md-6 mb-3'),
                Column('interventions', css_class='form-group col-md-6 mb-3'),
            ),
            
            Div(
                Submit('submit', 'Guardar Objetivo', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )