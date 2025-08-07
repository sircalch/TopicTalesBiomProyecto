from django.db import models
from django.contrib.auth import get_user_model
from patients.models import Patient
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class NutritionalAssessment(models.Model):
    """Evaluación nutricional completa del paciente"""
    
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentario'),
        ('light', 'Actividad Ligera'),
        ('moderate', 'Actividad Moderada'),
        ('active', 'Actividad Intensa'),
        ('very_active', 'Muy Activo'),
    ]
    
    OBJECTIVE_CHOICES = [
        ('maintain', 'Mantener Peso'),
        ('lose', 'Perder Peso'),
        ('gain', 'Ganar Peso'),
        ('muscle', 'Ganar Músculo'),
        ('health', 'Mejorar Salud'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nutritional_assessments')
    nutritionist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_assessments')
    
    # Medidas antropométricas
    weight = models.DecimalField('Peso (kg)', max_digits=5, decimal_places=2)
    height = models.DecimalField('Altura (cm)', max_digits=5, decimal_places=2)
    waist_circumference = models.DecimalField('Circunferencia de Cintura (cm)', max_digits=5, decimal_places=2, null=True, blank=True)
    hip_circumference = models.DecimalField('Circunferencia de Cadera (cm)', max_digits=5, decimal_places=2, null=True, blank=True)
    body_fat_percentage = models.DecimalField('Porcentaje de Grasa Corporal', max_digits=5, decimal_places=2, null=True, blank=True)
    muscle_mass = models.DecimalField('Masa Muscular (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Cálculos automáticos
    bmi = models.DecimalField('IMC', max_digits=5, decimal_places=2, editable=False)
    bmr = models.DecimalField('Metabolismo Basal (kcal)', max_digits=6, decimal_places=2, editable=False)
    daily_calories = models.DecimalField('Calorías Diarias Recomendadas', max_digits=6, decimal_places=2, editable=False)
    
    # Información del paciente
    activity_level = models.CharField('Nivel de Actividad', max_length=20, choices=ACTIVITY_CHOICES)
    objective = models.CharField('Objetivo Nutricional', max_length=20, choices=OBJECTIVE_CHOICES)
    
    # Antecedentes médicos nutricionales
    allergies = models.TextField('Alergias Alimentarias', blank=True)
    food_intolerances = models.TextField('Intolerancias Alimentarias', blank=True)
    chronic_diseases = models.TextField('Enfermedades Crónicas', blank=True)
    medications = models.TextField('Medicamentos Actuales', blank=True)
    
    # Hábitos alimentarios
    meals_per_day = models.IntegerField('Comidas por Día', default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    water_intake = models.DecimalField('Consumo de Agua (litros/día)', max_digits=3, decimal_places=1, default=2.0)
    alcohol_consumption = models.CharField('Consumo de Alcohol', max_length=100, blank=True)
    supplements = models.TextField('Suplementos', blank=True)
    
    # Observaciones
    notes = models.TextField('Observaciones', blank=True)
    recommendations = models.TextField('Recomendaciones', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Evaluación Nutricional'
        verbose_name_plural = 'Evaluaciones Nutricionales'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evaluación de {self.patient.get_full_name()} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Calcular IMC
        height_m = float(self.height) / 100
        self.bmi = round(float(self.weight) / (height_m ** 2), 2)
        
        # Calcular Metabolismo Basal (Fórmula de Harris-Benedict)
        age = self.patient.get_age()
        weight_kg = float(self.weight)
        height_cm = float(self.height)
        
        if self.patient.gender == 'M':
            self.bmr = round(88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age), 2)
        else:
            self.bmr = round(447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age), 2)
        
        # Calcular calorías diarias según actividad
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        self.daily_calories = round(float(self.bmr) * multiplier, 2)
        
        super().save(*args, **kwargs)
    
    def get_bmi_category(self):
        """Retorna la categoría del IMC según OMS"""
        bmi = float(self.bmi)
        if bmi < 18.5:
            return 'Bajo peso'
        elif 18.5 <= bmi < 25:
            return 'Peso normal'
        elif 25 <= bmi < 30:
            return 'Sobrepeso'
        elif 30 <= bmi < 35:
            return 'Obesidad grado I'
        elif 35 <= bmi < 40:
            return 'Obesidad grado II'
        else:
            return 'Obesidad grado III'
    
    def get_waist_hip_ratio(self):
        """Calcula la relación cintura-cadera"""
        if self.waist_circumference and self.hip_circumference:
            return round(float(self.waist_circumference) / float(self.hip_circumference), 2)
        return None


class DietPlan(models.Model):
    """Plan dietético personalizado"""
    
    PLAN_TYPE_CHOICES = [
        ('weight_loss', 'Pérdida de Peso'),
        ('weight_gain', 'Ganancia de Peso'),
        ('maintenance', 'Mantenimiento'),
        ('muscle_gain', 'Ganancia Muscular'),
        ('diabetic', 'Diabético'),
        ('hypertensive', 'Hipertensivo'),
        ('low_sodium', 'Bajo en Sodio'),
        ('vegetarian', 'Vegetariano'),
        ('vegan', 'Vegano'),
        ('mediterranean', 'Mediterránea'),
        ('keto', 'Cetogénica'),
    ]
    
    assessment = models.ForeignKey(NutritionalAssessment, on_delete=models.CASCADE, related_name='diet_plans')
    name = models.CharField('Nombre del Plan', max_length=200)
    plan_type = models.CharField('Tipo de Plan', max_length=20, choices=PLAN_TYPE_CHOICES)
    
    # Objetivos calóricos y macronutrientes
    target_calories = models.DecimalField('Calorías Objetivo', max_digits=6, decimal_places=2)
    protein_grams = models.DecimalField('Proteínas (g)', max_digits=6, decimal_places=2)
    carbs_grams = models.DecimalField('Carbohidratos (g)', max_digits=6, decimal_places=2)
    fat_grams = models.DecimalField('Grasas (g)', max_digits=6, decimal_places=2)
    fiber_grams = models.DecimalField('Fibra (g)', max_digits=5, decimal_places=2, default=25)
    
    # Distribución por comida
    breakfast_calories = models.DecimalField('Desayuno (kcal)', max_digits=5, decimal_places=2)
    morning_snack_calories = models.DecimalField('Colación Matutina (kcal)', max_digits=5, decimal_places=2, default=0)
    lunch_calories = models.DecimalField('Comida (kcal)', max_digits=5, decimal_places=2)
    afternoon_snack_calories = models.DecimalField('Colación Vespertina (kcal)', max_digits=5, decimal_places=2, default=0)
    dinner_calories = models.DecimalField('Cena (kcal)', max_digits=5, decimal_places=2)
    
    # Instrucciones
    instructions = models.TextField('Instrucciones Generales')
    foods_to_avoid = models.TextField('Alimentos a Evitar', blank=True)
    recommended_foods = models.TextField('Alimentos Recomendados', blank=True)
    
    # Fechas
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin', null=True, blank=True)
    
    is_active = models.BooleanField('Plan Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan Dietético'
        verbose_name_plural = 'Planes Dietéticos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.assessment.patient.get_full_name()}"
    
    def get_protein_percentage(self):
        return round((float(self.protein_grams) * 4) / float(self.target_calories) * 100, 1)
    
    def get_carbs_percentage(self):
        return round((float(self.carbs_grams) * 4) / float(self.target_calories) * 100, 1)
    
    def get_fat_percentage(self):
        return round((float(self.fat_grams) * 9) / float(self.target_calories) * 100, 1)


class MealPlan(models.Model):
    """Menú específico para un día"""
    
    MEAL_CHOICES = [
        ('breakfast', 'Desayuno'),
        ('morning_snack', 'Colación Matutina'),
        ('lunch', 'Comida'),
        ('afternoon_snack', 'Colación Vespertina'),
        ('dinner', 'Cena'),
    ]
    
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meal_plans')
    meal_type = models.CharField('Tipo de Comida', max_length=20, choices=MEAL_CHOICES)
    day_number = models.IntegerField('Día del Plan', validators=[MinValueValidator(1), MaxValueValidator(7)])
    
    name = models.CharField('Nombre del Menú', max_length=200)
    description = models.TextField('Descripción')
    preparation_instructions = models.TextField('Instrucciones de Preparación', blank=True)
    
    # Información nutricional
    calories = models.DecimalField('Calorías', max_digits=6, decimal_places=2)
    protein = models.DecimalField('Proteínas (g)', max_digits=5, decimal_places=2)
    carbs = models.DecimalField('Carbohidratos (g)', max_digits=5, decimal_places=2)
    fat = models.DecimalField('Grasas (g)', max_digits=5, decimal_places=2)
    fiber = models.DecimalField('Fibra (g)', max_digits=5, decimal_places=2, default=0)
    
    preparation_time = models.IntegerField('Tiempo de Preparación (minutos)', default=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Menú de Comida'
        verbose_name_plural = 'Menús de Comidas'
        ordering = ['day_number', 'meal_type']
        unique_together = ['diet_plan', 'meal_type', 'day_number']
    
    def __str__(self):
        return f"Día {self.day_number} - {self.get_meal_type_display()}: {self.name}"


class FoodItem(models.Model):
    """Ingredientes individuales de los menús"""
    
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField('Alimento', max_length=200)
    quantity = models.DecimalField('Cantidad', max_digits=6, decimal_places=2)
    unit = models.CharField('Unidad', max_length=50)  # gramos, piezas, tazas, etc.
    
    # Valores nutricionales por porción
    calories_per_serving = models.DecimalField('Calorías por Porción', max_digits=6, decimal_places=2)
    protein_per_serving = models.DecimalField('Proteínas por Porción (g)', max_digits=5, decimal_places=2, default=0)
    carbs_per_serving = models.DecimalField('Carbohidratos por Porción (g)', max_digits=5, decimal_places=2, default=0)
    fat_per_serving = models.DecimalField('Grasas por Porción (g)', max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'
    
    def __str__(self):
        return f"{self.quantity} {self.unit} de {self.name}"


class NutritionConsultation(models.Model):
    """Consulta nutricional - seguimiento del paciente"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nutrition_consultations')
    nutritionist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_consultations')
    assessment = models.ForeignKey(NutritionalAssessment, on_delete=models.CASCADE, related_name='consultations', null=True, blank=True)
    
    # Información de la consulta
    consultation_date = models.DateTimeField('Fecha de Consulta')
    consultation_type = models.CharField('Tipo de Consulta', max_length=50, choices=[
        ('initial', 'Consulta Inicial'),
        ('followup', 'Seguimiento'),
        ('adjustment', 'Ajuste de Plan'),
        ('emergency', 'Consulta de Emergencia'),
    ], default='followup')
    
    # Progreso del paciente
    current_weight = models.DecimalField('Peso Actual (kg)', max_digits=5, decimal_places=2)
    weight_change = models.DecimalField('Cambio de Peso (kg)', max_digits=5, decimal_places=2, editable=False)
    
    # Adherencia al plan
    diet_adherence = models.IntegerField('Adherencia a la Dieta (%)', validators=[MinValueValidator(0), MaxValueValidator(100)])
    exercise_adherence = models.IntegerField('Adherencia al Ejercicio (%)', validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Evaluación subjetiva
    patient_satisfaction = models.IntegerField('Satisfacción del Paciente', choices=[
        (1, 'Muy Insatisfecho'),
        (2, 'Insatisfecho'),
        (3, 'Neutral'),
        (4, 'Satisfecho'),
        (5, 'Muy Satisfecho'),
    ], default=3)
    
    energy_level = models.IntegerField('Nivel de Energía', choices=[
        (1, 'Muy Bajo'),
        (2, 'Bajo'),
        (3, 'Normal'),
        (4, 'Alto'),
        (5, 'Muy Alto'),
    ], default=3)
    
    # Observaciones
    patient_concerns = models.TextField('Preocupaciones del Paciente', blank=True)
    progress_notes = models.TextField('Notas de Progreso')
    next_goals = models.TextField('Objetivos para Próxima Consulta', blank=True)
    
    # Próxima cita
    next_appointment = models.DateTimeField('Próxima Cita', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Consulta Nutricional'
        verbose_name_plural = 'Consultas Nutricionales'
        ordering = ['-consultation_date']
    
    def __str__(self):
        return f"Consulta {self.patient.get_full_name()} - {self.consultation_date.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Calcular cambio de peso si hay evaluación previa
        if self.assessment:
            previous_weight = float(self.assessment.weight)
            current_weight = float(self.current_weight)
            self.weight_change = current_weight - previous_weight
        
        super().save(*args, **kwargs)


class NutritionGoal(models.Model):
    """Objetivos nutricionales específicos del paciente"""
    
    GOAL_TYPE_CHOICES = [
        ('weight', 'Meta de Peso'),
        ('bmi', 'Meta de IMC'),
        ('body_fat', 'Meta de Grasa Corporal'),
        ('muscle_mass', 'Meta de Masa Muscular'),
        ('waist', 'Meta de Circunferencia de Cintura'),
        ('habit', 'Cambio de Hábito'),
        ('nutrition', 'Meta Nutricional'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('achieved', 'Lograda'),
        ('paused', 'Pausada'),
        ('cancelled', 'Cancelada'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nutrition_goals')
    nutritionist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_nutrition_goals')
    
    goal_type = models.CharField('Tipo de Meta', max_length=20, choices=GOAL_TYPE_CHOICES)
    title = models.CharField('Título de la Meta', max_length=200)
    description = models.TextField('Descripción')
    
    # Valores objetivo
    target_value = models.DecimalField('Valor Objetivo', max_digits=8, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField('Valor Actual', max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField('Unidad', max_length=50, blank=True)
    
    # Fechas
    start_date = models.DateField('Fecha de Inicio')
    target_date = models.DateField('Fecha Objetivo')
    achieved_date = models.DateField('Fecha de Logro', null=True, blank=True)
    
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.IntegerField('Prioridad', choices=[
        (1, 'Baja'),
        (2, 'Media'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ], default=2)
    
    notes = models.TextField('Notas', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Meta Nutricional'
        verbose_name_plural = 'Metas Nutricionales'
        ordering = ['-priority', 'target_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name()}"
    
    def get_progress_percentage(self):
        """Calcula el porcentaje de progreso hacia la meta"""
        if not self.target_value or not self.current_value:
            return 0
        
        if self.goal_type in ['weight', 'bmi', 'body_fat', 'waist']:
            # Para metas de reducción
            initial_assessment = self.patient.nutritional_assessments.first()
            if not initial_assessment:
                return 0
            
            if self.goal_type == 'weight':
                initial_value = float(initial_assessment.weight)
            elif self.goal_type == 'bmi':
                initial_value = float(initial_assessment.bmi)
            elif self.goal_type == 'body_fat':
                initial_value = float(initial_assessment.body_fat_percentage or 0)
            elif self.goal_type == 'waist':
                initial_value = float(initial_assessment.waist_circumference or 0)
            
            target = float(self.target_value)
            current = float(self.current_value)
            
            if initial_value == target:
                return 100
            
            progress = abs(initial_value - current) / abs(initial_value - target) * 100
            return min(100, max(0, progress))
        
        return 0
