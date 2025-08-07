from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Report, ReportTemplate, ReportShare

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'status', 'created_by', 
        'created_at', 'is_scheduled', 'file_size_display'
    ]
    list_filter = [
        'report_type', 'status', 'is_scheduled', 'created_at',
        'file_format'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'file_size_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'report_type', 'status')
        }),
        ('Fechas del Reporte', {
            'fields': ('date_from', 'date_to')
        }),
        ('Configuración', {
            'fields': ('file_format', 'filters', 'parameters'),
            'classes': ('collapse',)
        }),
        ('Programación', {
            'fields': ('is_scheduled', 'schedule_frequency', 'next_run'),
            'classes': ('collapse',)
        }),
        ('Archivo', {
            'fields': ('file_path', 'file_size_display'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Muestra el tamaño del archivo en formato legible"""
        size = obj.file_size
        if size == 0:
            return "Sin archivo"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    file_size_display.short_description = "Tamaño del Archivo"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'report_type', 'is_active', 'is_public', 
        'created_by', 'created_at'
    ]
    list_filter = ['report_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'report_type')
        }),
        ('Configuración', {
            'fields': ('template_config', 'default_filters'),
            'classes': ('collapse',)
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_public')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    list_display = [
        'report_title', 'shared_with', 'shared_by', 'can_edit', 
        'can_download', 'shared_at', 'expires_at', 'is_expired_display'
    ]
    list_filter = [
        'can_edit', 'can_download', 'shared_at', 'expires_at'
    ]
    search_fields = [
        'report__title', 'shared_with__username', 'shared_by__username'
    ]
    readonly_fields = ['shared_at', 'is_expired_display']
    date_hierarchy = 'shared_at'
    
    fieldsets = (
        ('Reporte', {
            'fields': ('report',)
        }),
        ('Usuarios', {
            'fields': ('shared_with', 'shared_by')
        }),
        ('Permisos', {
            'fields': ('can_edit', 'can_download')
        }),
        ('Expiración', {
            'fields': ('expires_at', 'is_expired_display')
        }),
        ('Metadatos', {
            'fields': ('shared_at',),
            'classes': ('collapse',)
        }),
    )
    
    def report_title(self, obj):
        """Muestra el título del reporte con enlace"""
        url = reverse('admin:reports_report_change', args=[obj.report.pk])
        return format_html('<a href="{}">{}</a>', url, obj.report.title)
    
    report_title.short_description = "Reporte"
    report_title.admin_order_field = 'report__title'
    
    def is_expired_display(self, obj):
        """Muestra si el compartir ha expirado"""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expirado</span>')
        elif obj.expires_at:
            return format_html('<span style="color: orange;">Expira: {}</span>', 
                             obj.expires_at.strftime('%d/%m/%Y %H:%M'))
        else:
            return format_html('<span style="color: green;">No expira</span>')
    
    is_expired_display.short_description = "Estado de Expiración"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'report', 'shared_with', 'shared_by'
        )
