from django.contrib import admin
from .models import (
    NutritionalAssessment, 
    DietPlan, 
    MealPlan, 
    FoodItem, 
    NutritionConsultation, 
    NutritionGoal
)


class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 3
    fields = ['name', 'quantity', 'unit', 'calories_per_serving', 'protein_per_serving', 'carbs_per_serving', 'fat_per_serving']


class MealPlanInline(admin.TabularInline):
    model = MealPlan
    extra = 0
    fields = ['meal_type', 'day_number', 'name', 'calories', 'protein', 'carbs', 'fat']
    readonly_fields = ['calories', 'protein', 'carbs', 'fat']


@admin.register(NutritionalAssessment)
class NutritionalAssessmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'nutritionist', 'weight', 'height', 'bmi', 'get_bmi_category', 'activity_level', 'objective', 'created_at']
    list_filter = ['activity_level', 'objective', 'created_at', 'nutritionist']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__identification_number']
    readonly_fields = ['bmi', 'bmr', 'daily_calories', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Paciente', {
            'fields': ('patient', 'nutritionist')
        }),
        ('Medidas Antropométricas', {
            'fields': ('weight', 'height', 'waist_circumference', 'hip_circumference', 'body_fat_percentage', 'muscle_mass')
        }),
        ('Cálculos Automáticos', {
            'fields': ('bmi', 'bmr', 'daily_calories'),
            'classes': ('collapse',)
        }),
        ('Información del Paciente', {
            'fields': ('activity_level', 'objective')
        }),
        ('Antecedentes Médicos', {
            'fields': ('allergies', 'food_intolerances', 'chronic_diseases', 'medications'),
            'classes': ('collapse',)
        }),
        ('Hábitos Alimentarios', {
            'fields': ('meals_per_day', 'water_intake', 'alcohol_consumption', 'supplements'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('notes', 'recommendations')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_bmi_category(self, obj):
        return obj.get_bmi_category()
    get_bmi_category.short_description = 'Categoría IMC'


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_patient_name', 'plan_type', 'target_calories', 'is_active', 'start_date', 'created_at']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'assessment__patient__first_name', 'assessment__patient__last_name']
    inlines = [MealPlanInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('assessment', 'name', 'plan_type')
        }),
        ('Objetivos Nutricionales', {
            'fields': ('target_calories', 'protein_grams', 'carbs_grams', 'fat_grams', 'fiber_grams')
        }),
        ('Distribución de Calorías', {
            'fields': ('breakfast_calories', 'morning_snack_calories', 'lunch_calories', 'afternoon_snack_calories', 'dinner_calories'),
            'classes': ('collapse',)
        }),
        ('Instrucciones', {
            'fields': ('instructions', 'foods_to_avoid', 'recommended_foods')
        }),
        ('Fechas y Estado', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.assessment.patient.get_full_name()
    get_patient_name.short_description = 'Paciente'


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'get_diet_plan_name', 'day_number', 'meal_type', 'name', 'calories', 'preparation_time']
    list_filter = ['meal_type', 'day_number', 'diet_plan__plan_type']
    search_fields = ['name', 'diet_plan__name', 'diet_plan__assessment__patient__first_name', 'diet_plan__assessment__patient__last_name']
    inlines = [FoodItemInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('diet_plan', 'meal_type', 'day_number', 'name')
        }),
        ('Descripción', {
            'fields': ('description', 'preparation_instructions', 'preparation_time')
        }),
        ('Información Nutricional', {
            'fields': ('calories', 'protein', 'carbs', 'fat', 'fiber')
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.diet_plan.assessment.patient.get_full_name()
    get_patient_name.short_description = 'Paciente'
    
    def get_diet_plan_name(self, obj):
        return obj.diet_plan.name
    get_diet_plan_name.short_description = 'Plan Dietético'


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'get_meal_info', 'calories_per_serving']
    list_filter = ['meal_plan__meal_type', 'unit']
    search_fields = ['name', 'meal_plan__name']
    
    def get_meal_info(self, obj):
        return f"{obj.meal_plan.get_meal_type_display()} - Día {obj.meal_plan.day_number}"
    get_meal_info.short_description = 'Comida'


@admin.register(NutritionConsultation)
class NutritionConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'nutritionist', 'consultation_date', 'consultation_type', 'current_weight', 'weight_change', 'diet_adherence']
    list_filter = ['consultation_type', 'consultation_date', 'nutritionist', 'patient_satisfaction']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__identification_number']
    readonly_fields = ['weight_change', 'created_at', 'updated_at']
    date_hierarchy = 'consultation_date'
    
    fieldsets = (
        ('Información de la Consulta', {
            'fields': ('patient', 'nutritionist', 'assessment', 'consultation_date', 'consultation_type')
        }),
        ('Progreso del Paciente', {
            'fields': ('current_weight', 'weight_change', 'diet_adherence', 'exercise_adherence')
        }),
        ('Evaluación Subjetiva', {
            'fields': ('patient_satisfaction', 'energy_level'),
            'classes': ('collapse',)
        }),
        ('Observaciones', {
            'fields': ('patient_concerns', 'progress_notes', 'next_goals')
        }),
        ('Seguimiento', {
            'fields': ('next_appointment',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NutritionGoal)
class NutritionGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'nutritionist', 'goal_type', 'target_value', 'current_value', 'status', 'priority', 'target_date']
    list_filter = ['goal_type', 'status', 'priority', 'target_date', 'nutritionist']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información General', {
            'fields': ('patient', 'nutritionist', 'goal_type', 'title', 'description')
        }),
        ('Objetivos', {
            'fields': ('target_value', 'current_value', 'unit')
        }),
        ('Fechas y Estado', {
            'fields': ('start_date', 'target_date', 'achieved_date', 'status', 'priority')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Fechas de Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
