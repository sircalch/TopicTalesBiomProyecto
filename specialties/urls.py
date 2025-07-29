from django.urls import path
from . import views

app_name = 'specialties'

urlpatterns = [
    path('', views.index, name='index'),
    path('nutrition/', views.nutrition, name='nutrition'),
    path('psychology/', views.psychology, name='psychology'),
    path('pediatrics/', views.pediatrics, name='pediatrics'),
    path('ophthalmology/', views.ophthalmology, name='ophthalmology'),
    path('dentistry/', views.dentistry, name='dentistry'),
]