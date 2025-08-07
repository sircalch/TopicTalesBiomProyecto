from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from crispy_forms.bootstrap import PrependedText, AppendedText
from .models import (
    NutritionalAssessment, 
    DietPlan, 
    MealPlan, 
    FoodItem, 
    NutritionConsultation, 
    NutritionGoal
)
from patients.models import Patient

User = get_user_model()


class NutritionalAssessmentForm(forms.ModelForm):
    class Meta:
        model = NutritionalAssessment
        fields = [
            'patient', 'weight', 'height', 'waist_circumference', 'hip_circumference',
            'body_fat_percentage', 'muscle_mass', 'activity_level', 'objective',
            'allergies', 'food_intolerances', 'chronic_diseases', 'medications',
            'meals_per_day', 'water_intake', 'alcohol_consumption', 'supplements',
            'notes', 'recommendations'
        ]
        widgets = {
            'weight': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'waist_circumference': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'hip_circumference': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'body_fat_percentage': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '100'}),
            'muscle_mass': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'water_intake': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'meals_per_day': forms.NumberInput(attrs={'min': '1', 'max': '10'}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'food_intolerances': forms.Textarea(attrs={'rows': 3}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'supplements': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar pacientes por organización del usuario
            self.fields['patient'].queryset = Patient.objects.filter(
                organization=user.profile.organization
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('patient', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-weight me-2"></i>Medidas Antropométricas</h5>'),
            Row(
                Column(AppendedText('weight', 'kg'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('height', 'cm'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('waist_circumference', 'cm'), css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column(AppendedText('hip_circumference', 'cm'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('body_fat_percentage', '%'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('muscle_mass', 'kg'), css_class='form-group col-md-4 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-running me-2"></i>Información del Estilo de Vida</h5>'),
            Row(
                Column('activity_level', css_class='form-group col-md-6 mb-3'),
                Column('objective', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('meals_per_day', css_class='form-group col-md-6 mb-3'),
                Column(AppendedText('water_intake', 'L/día'), css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('alcohol_consumption', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-notes-medical me-2"></i>Antecedentes Médicos</h5>'),
            Row(
                Column('allergies', css_class='form-group col-md-6 mb-3'),
                Column('food_intolerances', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('chronic_diseases', css_class='form-group col-md-6 mb-3'),
                Column('medications', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('supplements', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-clipboard-list me-2"></i>Observaciones</h5>'),
            Row(
                Column('notes', css_class='form-group col-md-6 mb-3'),
                Column('recommendations', css_class='form-group col-md-6 mb-3'),
            ),
            Div(
                Submit('submit', 'Guardar Evaluación Nutricional', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class DietPlanForm(forms.ModelForm):
    class Meta:
        model = DietPlan
        fields = [
            'assessment', 'name', 'plan_type', 'target_calories', 'protein_grams',
            'carbs_grams', 'fat_grams', 'fiber_grams', 'breakfast_calories',
            'morning_snack_calories', 'lunch_calories', 'afternoon_snack_calories',
            'dinner_calories', 'instructions', 'foods_to_avoid', 'recommended_foods',
            'start_date', 'end_date'
        ]
        widgets = {
            'target_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'protein_grams': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'carbs_grams': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'fat_grams': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'fiber_grams': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'breakfast_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'morning_snack_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'lunch_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'afternoon_snack_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'dinner_calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'instructions': forms.Textarea(attrs={'rows': 4}),
            'foods_to_avoid': forms.Textarea(attrs={'rows': 3}),
            'recommended_foods': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar evaluaciones por organización del usuario
            self.fields['assessment'].queryset = NutritionalAssessment.objects.filter(
                patient__organization=user.profile.organization
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('assessment', css_class='form-group col-md-6 mb-3'),
                Column('name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('plan_type', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-calculator me-2"></i>Objetivos Nutricionales</h5>'),
            Row(
                Column(AppendedText('target_calories', 'kcal'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('protein_grams', 'g'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('carbs_grams', 'g'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('fat_grams', 'g'), css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column(AppendedText('fiber_grams', 'g'), css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-utensils me-2"></i>Distribución de Calorías por Comida</h5>'),
            Row(
                Column(AppendedText('breakfast_calories', 'kcal'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('morning_snack_calories', 'kcal'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('lunch_calories', 'kcal'), css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column(AppendedText('afternoon_snack_calories', 'kcal'), css_class='form-group col-md-6 mb-3'),
                Column(AppendedText('dinner_calories', 'kcal'), css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-clipboard-list me-2"></i>Instrucciones y Recomendaciones</h5>'),
            Row(
                Column('instructions', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('foods_to_avoid', css_class='form-group col-md-6 mb-3'),
                Column('recommended_foods', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-calendar me-2"></i>Duración del Plan</h5>'),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-3'),
                Column('end_date', css_class='form-group col-md-6 mb-3'),
            ),
            Div(
                Submit('submit', 'Guardar Plan Dietético', css_class='btn btn-success btn-lg'),
                css_class='text-center mt-4'
            )
        )


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = [
            'diet_plan', 'meal_type', 'day_number', 'name', 'description',
            'preparation_instructions', 'calories', 'protein', 'carbs', 'fat',
            'fiber', 'preparation_time'
        ]
        widgets = {
            'day_number': forms.NumberInput(attrs={'min': '1', 'max': '7'}),
            'calories': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
            'protein': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'carbs': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'fat': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'fiber': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'preparation_time': forms.NumberInput(attrs={'min': '1'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'preparation_instructions': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar planes dietéticos por organización del usuario
            self.fields['diet_plan'].queryset = DietPlan.objects.filter(
                assessment__patient__organization=user.profile.organization
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('diet_plan', css_class='form-group col-md-6 mb-3'),
                Column('name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('meal_type', css_class='form-group col-md-6 mb-3'),
                Column('day_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-chart-pie me-2"></i>Información Nutricional</h5>'),
            Row(
                Column(AppendedText('calories', 'kcal'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('protein', 'g'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('carbs', 'g'), css_class='form-group col-md-3 mb-3'),
                Column(AppendedText('fat', 'g'), css_class='form-group col-md-3 mb-3'),
            ),
            Row(
                Column(AppendedText('fiber', 'g'), css_class='form-group col-md-6 mb-3'),
                Column(AppendedText('preparation_time', 'min'), css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('preparation_instructions', css_class='form-group col-md-12 mb-3'),
            ),
            Div(
                Submit('submit', 'Guardar Menú', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


class NutritionConsultationForm(forms.ModelForm):
    class Meta:
        model = NutritionConsultation
        fields = [
            'patient', 'assessment', 'consultation_date', 'consultation_type',
            'current_weight', 'diet_adherence', 'exercise_adherence',
            'patient_satisfaction', 'energy_level', 'patient_concerns',
            'progress_notes', 'next_goals', 'next_appointment'
        ]
        widgets = {
            'consultation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'current_weight': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'diet_adherence': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'exercise_adherence': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'next_appointment': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'patient_concerns': forms.Textarea(attrs={'rows': 3}),
            'progress_notes': forms.Textarea(attrs={'rows': 4}),
            'next_goals': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar pacientes por organización del usuario
            self.fields['patient'].queryset = Patient.objects.filter(
                organization=user.profile.organization
            )
            # Filtrar evaluaciones por organización del usuario
            self.fields['assessment'].queryset = NutritionalAssessment.objects.filter(
                patient__organization=user.profile.organization
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('patient', css_class='form-group col-md-6 mb-3'),
                Column('assessment', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('consultation_date', css_class='form-group col-md-6 mb-3'),
                Column('consultation_type', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-chart-line me-2"></i>Progreso del Paciente</h5>'),
            Row(
                Column(AppendedText('current_weight', 'kg'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('diet_adherence', '%'), css_class='form-group col-md-4 mb-3'),
                Column(AppendedText('exercise_adherence', '%'), css_class='form-group col-md-4 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-smile me-2"></i>Evaluación Subjetiva</h5>'),
            Row(
                Column('patient_satisfaction', css_class='form-group col-md-6 mb-3'),
                Column('energy_level', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-notes-medical me-2"></i>Observaciones</h5>'),
            Row(
                Column('patient_concerns', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('progress_notes', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('next_goals', css_class='form-group col-md-6 mb-3'),
                Column('next_appointment', css_class='form-group col-md-6 mb-3'),
            ),
            Div(
                Submit('submit', 'Guardar Consulta', css_class='btn btn-success btn-lg'),
                css_class='text-center mt-4'
            )
        )


class NutritionGoalForm(forms.ModelForm):
    class Meta:
        model = NutritionGoal
        fields = [
            'patient', 'goal_type', 'title', 'description', 'target_value',
            'current_value', 'unit', 'start_date', 'target_date', 'status',
            'priority', 'notes'
        ]
        widgets = {
            'target_value': forms.NumberInput(attrs={'step': '0.1'}),
            'current_value': forms.NumberInput(attrs={'step': '0.1'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar pacientes por organización del usuario
            self.fields['patient'].queryset = Patient.objects.filter(
                organization=user.profile.organization
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('patient', css_class='form-group col-md-6 mb-3'),
                Column('goal_type', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('title', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-bullseye me-2"></i>Objetivos</h5>'),
            Row(
                Column('target_value', css_class='form-group col-md-4 mb-3'),
                Column('current_value', css_class='form-group col-md-4 mb-3'),
                Column('unit', css_class='form-group col-md-4 mb-3'),
            ),
            HTML('<h5 class="text-primary mb-3"><i class="fas fa-calendar me-2"></i>Fechas y Estado</h5>'),
            Row(
                Column('start_date', css_class='form-group col-md-4 mb-3'),
                Column('target_date', css_class='form-group col-md-4 mb-3'),
                Column('priority', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('status', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3'),
            ),
            Div(
                Submit('submit', 'Guardar Meta Nutricional', css_class='btn btn-primary btn-lg'),
                css_class='text-center mt-4'
            )
        )


# Formulario simplificado para búsqueda rápida de pacientes
class PatientSearchForm(forms.Form):
    patient_search = forms.CharField(
        label='Buscar Paciente',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre, apellido o número de identificación...',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('patient_search', css_class='form-group col-md-10'),
                Column(
                    Submit('search', 'Buscar', css_class='btn btn-primary'),
                    css_class='form-group col-md-2 d-flex align-items-end'
                ),
            )
        )