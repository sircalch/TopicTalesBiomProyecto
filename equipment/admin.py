from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import (
    EquipmentCategory, Location, Supplier, Equipment,
    MaintenanceRecord, EquipmentUsageLog, CalibrationRecord, EquipmentAlert
)

@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def equipment_count(self, obj):
        return obj.equipment_set.count()
    equipment_count.short_description = "Equipos"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'floor', 'room_number', 'equipment_count', 'is_active']
    list_filter = ['is_active', 'floor']
    search_fields = ['name', 'description', 'room_number']
    readonly_fields = ['created_at']
    
    def equipment_count(self, obj):
        return obj.equipment_set.count()
    equipment_count.short_description = "Equipos"

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'equipment_count', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'contact_person', 'is_active')
        }),
        ('Contacto', {
            'fields': ('phone', 'email', 'address', 'website')
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def equipment_count(self, obj):
        return obj.equipment_set.count()
    equipment_count.short_description = "Equipos"

class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    readonly_fields = ['total_cost']
    fields = ['maintenance_type', 'scheduled_date', 'status', 'technician', 'total_cost']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'model', 'brand', 'serial_number', 'category', 
        'location', 'status', 'condition', 'maintenance_due_display', 'warranty_status'
    ]
    list_filter = [
        'category', 'location', 'supplier', 'status', 'condition',
        'created_at', 'purchase_date'
    ]
    search_fields = [
        'name', 'model', 'brand', 'serial_number', 'asset_tag'
    ]
    readonly_fields = [
        'asset_tag', 'created_at', 'updated_at', 'warranty_status',
        'maintenance_due_display', 'warranty_days_remaining'
    ]
    inlines = [MaintenanceRecordInline]
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'model', 'brand', 'serial_number', 'asset_tag')
        }),
        ('Categorización', {
            'fields': ('category', 'supplier', 'location')
        }),
        ('Estado', {
            'fields': ('status', 'condition')
        }),
        ('Información Financiera', {
            'fields': ('purchase_price', 'purchase_date', 'warranty_expiry', 'warranty_status'),
            'classes': ('collapse',)
        }),
        ('Mantenimiento', {
            'fields': ('last_maintenance', 'next_maintenance', 'maintenance_frequency_days', 'maintenance_due_display'),
            'classes': ('collapse',)
        }),
        ('Especificaciones', {
            'fields': ('specifications', 'manual_url', 'description', 'notes'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def maintenance_due_display(self, obj):
        if obj.maintenance_due:
            days = obj.days_until_maintenance
            if days is not None and days < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">Vencido ({} días)</span>',
                    abs(days)
                )
        elif obj.next_maintenance:
            days = obj.days_until_maintenance
            if days is not None:
                if days <= 7:
                    return format_html(
                        '<span style="color: orange;">En {} días</span>',
                        days
                    )
                else:
                    return format_html(
                        '<span style="color: green;">En {} días</span>',
                        days
                    )
        return "No programado"
    
    maintenance_due_display.short_description = "Mantenimiento"
    
    def warranty_status(self, obj):
        if obj.is_warranty_valid:
            days = obj.warranty_days_remaining
            if days <= 30:
                return format_html(
                    '<span style="color: orange;">Expira en {} días</span>',
                    days
                )
            else:
                return format_html('<span style="color: green;">Vigente</span>')
        elif obj.warranty_expiry:
            return format_html('<span style="color: red;">Expirada</span>')
        return "Sin garantía"
    
    warranty_status.short_description = "Estado de Garantía"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'location', 'supplier', 'created_by'
        )

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'maintenance_type', 'scheduled_date', 'status',
        'technician', 'total_cost', 'completed_date'
    ]
    list_filter = [
        'maintenance_type', 'status', 'scheduled_date', 'completed_date'
    ]
    search_fields = [
        'equipment__name', 'equipment__serial_number', 'description',
        'technician__first_name', 'technician__last_name'
    ]
    readonly_fields = ['total_cost', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('equipment', 'maintenance_type', 'status')
        }),
        ('Fechas', {
            'fields': ('scheduled_date', 'completed_date', 'next_maintenance_date')
        }),
        ('Personal', {
            'fields': ('technician', 'supervisor')
        }),
        ('Trabajo Realizado', {
            'fields': ('description', 'work_performed', 'parts_replaced')
        }),
        ('Costos', {
            'fields': ('labor_cost', 'parts_cost', 'total_cost'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'equipment', 'technician', 'supervisor'
        )

@admin.register(EquipmentUsageLog)
class EquipmentUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'user', 'start_time', 'end_time',
        'duration_display', 'purpose', 'patient_name'
    ]
    list_filter = ['start_time', 'end_time']
    search_fields = [
        'equipment__name', 'user__first_name', 'user__last_name',
        'purpose', 'patient_name'
    ]
    readonly_fields = ['duration_display', 'created_at']
    date_hierarchy = 'start_time'
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours = int(duration // 60)
            minutes = int(duration % 60)
            return f"{hours}h {minutes}m"
        return "En curso"
    
    duration_display.short_description = "Duración"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'equipment', 'user'
        )

@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'scheduled_date', 'performed_date', 'status',
        'passed', 'technician', 'cost'
    ]
    list_filter = ['status', 'passed', 'scheduled_date', 'performed_date']
    search_fields = [
        'equipment__name', 'equipment__serial_number',
        'technician__first_name', 'technician__last_name',
        'external_company', 'certificate_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('equipment', 'status', 'passed')
        }),
        ('Fechas', {
            'fields': ('scheduled_date', 'performed_date', 'next_calibration_date')
        }),
        ('Personal y Empresa', {
            'fields': ('technician', 'external_company', 'cost')
        }),
        ('Detalles Técnicos', {
            'fields': ('calibration_standards', 'measurements_before', 'measurements_after', 'adjustments_made'),
            'classes': ('collapse',)
        }),
        ('Certificación', {
            'fields': ('certificate_number', 'certificate_file'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EquipmentAlert)
class EquipmentAlertAdmin(admin.ModelAdmin):
    list_display = [
        'equipment', 'alert_type', 'priority', 'title',
        'is_active', 'is_resolved', 'created_at', 'resolved_by'
    ]
    list_filter = [
        'alert_type', 'priority', 'is_active', 'is_resolved',
        'created_at', 'resolved_at'
    ]
    search_fields = [
        'equipment__name', 'title', 'message'
    ]
    readonly_fields = ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('equipment', 'alert_type', 'priority')
        }),
        ('Contenido', {
            'fields': ('title', 'message')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'equipment', 'resolved_by'
        )
    
    actions = ['resolve_alerts']
    
    def resolve_alerts(self, request, queryset):
        updated = queryset.filter(is_resolved=False).update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} alertas resueltas.')
    
    resolve_alerts.short_description = "Resolver alertas seleccionadas"
