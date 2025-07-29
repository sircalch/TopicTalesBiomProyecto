from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required  
def index(request):
    return render(request, 'reports/index.html', {'title': 'Reportes'})

@login_required
def patients_report(request):
    return render(request, 'reports/patients.html', {'title': 'Reporte de Pacientes'})

@login_required
def appointments_report(request):
    return render(request, 'reports/appointments.html', {'title': 'Reporte de Citas'})

@login_required
def financial_report(request):
    return render(request, 'reports/financial.html', {'title': 'Reporte Financiero'})

@login_required
def analytics_report(request):
    return render(request, 'reports/analytics.html', {'title': 'Análisis Avanzado'})

