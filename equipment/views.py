from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required  
def equipment_list(request):
    return render(request, 'equipment/list.html', {'title': 'Equipos Médicos'})

@login_required
def equipment_create(request):
    return render(request, 'equipment/create.html', {'title': 'Crear Equipo'})

@login_required
def equipment_detail(request, equipment_id):
    return render(request, 'equipment/detail.html', {'title': 'Detalle del Equipo'})

@login_required
def maintenance_schedule(request, equipment_id):
    return render(request, 'equipment/maintenance.html', {'title': 'Mantenimiento'})

