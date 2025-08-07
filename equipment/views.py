from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Equipment, EquipmentCategory, Location, Supplier,
    MaintenanceRecord, EquipmentUsageLog, CalibrationRecord, EquipmentAlert
)
from .forms import (
    EquipmentForm, EquipmentCategoryForm, LocationForm, SupplierForm,
    MaintenanceRecordForm, EquipmentUsageLogForm, EquipmentFilterForm, EquipmentAlertForm
)

@login_required  
def equipment_list(request):
    """Lista de equipos con filtros"""
    form = EquipmentFilterForm(request.GET or None)
    equipment_list = Equipment.objects.select_related('category', 'location', 'supplier').order_by('name')
    
    # Aplicar filtros
    if form.is_valid():
        if form.cleaned_data.get('category'):
            equipment_list = equipment_list.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('location'):
            equipment_list = equipment_list.filter(location=form.cleaned_data['location'])
        if form.cleaned_data.get('status'):
            equipment_list = equipment_list.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('condition'):
            equipment_list = equipment_list.filter(condition=form.cleaned_data['condition'])
        if form.cleaned_data.get('maintenance_due'):
            equipment_list = equipment_list.filter(next_maintenance__lte=date.today())
        if form.cleaned_data.get('warranty_expiring'):
            thirty_days = date.today() + timedelta(days=30)
            equipment_list = equipment_list.filter(
                warranty_expiry__lte=thirty_days,
                warranty_expiry__gte=date.today()
            )
    
    # Búsqueda por texto
    search = request.GET.get('search')
    if search:
        equipment_list = equipment_list.filter(
            Q(name__icontains=search) |
            Q(model__icontains=search) |
            Q(brand__icontains=search) |
            Q(serial_number__icontains=search) |
            Q(asset_tag__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(equipment_list, 20)
    page_number = request.GET.get('page')
    equipment = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': Equipment.objects.count(),
        'operational': Equipment.objects.filter(status='operational').count(),
        'maintenance_due': Equipment.objects.filter(next_maintenance__lte=date.today()).count(),
        'warranty_expiring': Equipment.objects.filter(
            warranty_expiry__lte=date.today() + timedelta(days=30),
            warranty_expiry__gte=date.today()
        ).count(),
    }
    
    context = {
        'title': 'Equipos Médicos',
        'equipment': equipment,
        'form': form,
        'search': search,
        'stats': stats,
    }
    
    return render(request, 'equipment/list.html', context)

@login_required
def equipment_create(request):
    """Crear nuevo equipo"""
    if request.method == 'POST':
        form = EquipmentForm(request.POST, user=request.user)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, f'Equipo "{equipment.name}" creado exitosamente.')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = EquipmentForm(user=request.user)
    
    context = {
        'title': 'Crear Equipo',
        'form': form,
    }
    
    return render(request, 'equipment/create.html', context)

@login_required
def equipment_detail(request, pk):
    """Detalle de un equipo específico"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    # Registros de mantenimiento recientes
    maintenance_records = equipment.maintenance_records.order_by('-scheduled_date')[:10]
    
    # Registros de uso recientes
    usage_logs = equipment.usage_logs.select_related('user').order_by('-start_time')[:10]
    
    # Alertas activas
    active_alerts = equipment.alerts.filter(is_active=True, is_resolved=False).order_by('-created_at')
    
    # Registros de calibración
    calibration_records = equipment.calibration_records.order_by('-scheduled_date')[:5]
    
    context = {
        'title': f'Equipo: {equipment.name}',
        'equipment': equipment,
        'maintenance_records': maintenance_records,
        'usage_logs': usage_logs,
        'active_alerts': active_alerts,
        'calibration_records': calibration_records,
    }
    
    return render(request, 'equipment/detail.html', context)

@login_required
def equipment_edit(request, pk):
    """Editar equipo existente"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment, user=request.user)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, f'Equipo "{equipment.name}" actualizado exitosamente.')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = EquipmentForm(instance=equipment, user=request.user)
    
    context = {
        'title': f'Editar: {equipment.name}',
        'form': form,
        'equipment': equipment,
    }
    
    return render(request, 'equipment/edit.html', context)

@login_required
def maintenance_schedule(request, pk):
    """Programar mantenimiento para un equipo"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, equipment=equipment)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, f'Mantenimiento programado para {equipment.name}.')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = MaintenanceRecordForm(equipment=equipment)
    
    context = {
        'title': f'Programar Mantenimiento - {equipment.name}',
        'form': form,
        'equipment': equipment,
    }
    
    return render(request, 'equipment/maintenance_schedule.html', context)

@login_required
def maintenance_list(request):
    """Lista de todos los mantenimientos"""
    maintenance_list = MaintenanceRecord.objects.select_related('equipment', 'technician').order_by('-scheduled_date')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        maintenance_list = maintenance_list.filter(status=status_filter)
    
    type_filter = request.GET.get('type')
    if type_filter:
        maintenance_list = maintenance_list.filter(maintenance_type=type_filter)
    
    # Paginación
    paginator = Paginator(maintenance_list, 20)
    page_number = request.GET.get('page')
    maintenance_records = paginator.get_page(page_number)
    
    context = {
        'title': 'Mantenimientos',
        'maintenance_records': maintenance_records,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    
    return render(request, 'equipment/maintenance_list.html', context)

@login_required
def usage_log_create(request, pk):
    """Crear registro de uso para un equipo"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        form = EquipmentUsageLogForm(request.POST, equipment=equipment, user=request.user)
        if form.is_valid():
            usage_log = form.save()
            messages.success(request, f'Registro de uso creado para {equipment.name}.')
            return redirect('equipment:detail', pk=equipment.pk)
    else:
        form = EquipmentUsageLogForm(equipment=equipment, user=request.user)
    
    context = {
        'title': f'Registrar Uso - {equipment.name}',
        'form': form,
        'equipment': equipment,
    }
    
    return render(request, 'equipment/usage_log_create.html', context)

@login_required
def dashboard(request):
    """Dashboard principal de equipos"""
    # Estadísticas generales
    stats = {
        'total_equipment': Equipment.objects.count(),
        'operational': Equipment.objects.filter(status='operational').count(),
        'in_maintenance': Equipment.objects.filter(status='maintenance').count(),
        'out_of_service': Equipment.objects.filter(status='out_of_service').count(),
    }
    
    # Equipos con mantenimiento vencido
    maintenance_due = Equipment.objects.filter(
        next_maintenance__lte=date.today(),
        status='operational'
    ).select_related('category', 'location')[:10]
    
    # Equipos con garantía por vencer (próximos 30 días)
    warranty_expiring = Equipment.objects.filter(
        warranty_expiry__lte=date.today() + timedelta(days=30),
        warranty_expiry__gte=date.today()
    ).select_related('category', 'location')[:10]
    
    # Alertas activas
    active_alerts = EquipmentAlert.objects.filter(
        is_active=True,
        is_resolved=False
    ).select_related('equipment').order_by('-priority', '-created_at')[:10]
    
    # Mantenimientos recientes
    recent_maintenance = MaintenanceRecord.objects.select_related(
        'equipment', 'technician'
    ).order_by('-created_at')[:10]
    
    context = {
        'title': 'Dashboard de Equipos',
        'stats': stats,
        'maintenance_due': maintenance_due,
        'warranty_expiring': warranty_expiring,
        'active_alerts': active_alerts,
        'recent_maintenance': recent_maintenance,
    }
    
    return render(request, 'equipment/dashboard.html', context)

@login_required
def categories_list(request):
    """Lista de categorías de equipos"""
    categories = EquipmentCategory.objects.annotate(
        equipment_count=Count('equipment')
    ).order_by('name')
    
    context = {
        'title': 'Categorías de Equipos',
        'categories': categories,
    }
    
    return render(request, 'equipment/categories.html', context)

@login_required
def locations_list(request):
    """Lista de ubicaciones"""
    locations = Location.objects.annotate(
        equipment_count=Count('equipment')
    ).order_by('name')
    
    context = {
        'title': 'Ubicaciones',
        'locations': locations,
    }
    
    return render(request, 'equipment/locations.html', context)

@login_required
def suppliers_list(request):
    """Lista de proveedores"""
    suppliers = Supplier.objects.annotate(
        equipment_count=Count('equipment')
    ).order_by('name')
    
    context = {
        'title': 'Proveedores',
        'suppliers': suppliers,
    }
    
    return render(request, 'equipment/suppliers.html', context)

# API Views
@login_required
def api_equipment_alerts(request, pk):
    """API para obtener alertas de un equipo"""
    try:
        equipment = Equipment.objects.get(pk=pk)
        alerts = equipment.alerts.filter(is_active=True, is_resolved=False)
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'type': alert.get_alert_type_display(),
                'priority': alert.get_priority_display(),
                'title': alert.title,
                'message': alert.message,
                'created_at': alert.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        return JsonResponse({'alerts': alerts_data})
    except Equipment.DoesNotExist:
        return JsonResponse({'error': 'Equipo no encontrado'}, status=404)


@login_required
def equipment_export(request):
    """Exportar lista de equipos a CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipos.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Código', 'Nombre', 'Marca', 'Modelo', 'Categoría', 'Estado', 'Ubicación'])
    
    equipments = Equipment.objects.select_related('category', 'location').all()
    for equipment in equipments:
        writer.writerow([
            equipment.asset_tag,
            equipment.name,
            equipment.brand or '',
            equipment.model or '',
            equipment.category.name if equipment.category else '',
            equipment.get_status_display(),
            equipment.location.name if equipment.location else ''
        ])
    
    return response


@login_required
def bulk_actions(request):
    """Acciones en lote para equipos"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.get('selected_equipment', '').split(',')
        selected_ids = [id for id in selected_ids if id.strip()]
        
        if not selected_ids:
            messages.error(request, 'No se seleccionaron equipos.')
            return redirect('equipment:list')
        
        equipments = Equipment.objects.filter(id__in=selected_ids)
        
        if action == 'export_selected':
            # Exportar equipos seleccionados
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="equipos_seleccionados.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Código', 'Nombre', 'Marca', 'Modelo', 'Categoría', 'Estado', 'Ubicación'])
            
            for equipment in equipments.select_related('category', 'location'):
                writer.writerow([
                    equipment.asset_tag,
                    equipment.name,
                    equipment.brand or '',
                    equipment.model or '',
                    equipment.category.name if equipment.category else '',
                    equipment.get_status_display(),
                    equipment.location.name if equipment.location else ''
                ])
            
            return response
            
        elif action == 'update_status':
            new_status = request.POST.get('new_status')
            if new_status:
                equipments.update(status=new_status)
                messages.success(request, f'Estado actualizado para {equipments.count()} equipos.')
            
        elif action == 'change_location':
            new_location_id = request.POST.get('new_location')
            if new_location_id:
                new_location = get_object_or_404(Location, id=new_location_id)
                equipments.update(location=new_location)
                messages.success(request, f'Ubicación cambiada para {equipments.count()} equipos.')
        
        messages.success(request, f'Acción "{action}" aplicada a {equipments.count()} equipos.')
    
    return redirect('equipment:list')

