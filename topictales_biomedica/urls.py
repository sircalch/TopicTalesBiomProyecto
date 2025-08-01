"""
TopicTales Biomédica - Main URL Configuration
Medical Management System with modular subscription plans
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Admin customization
admin.site.site_header = "TopicTales Biomédica - Administración"
admin.site.site_title = "TopicTales Biomédica"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication and user management
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    # Core medical modules
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('medical-records/', include('medical_records.urls', namespace='medical_records')),
    
    # Medical specialties
    path('specialties/', include('specialties.urls', namespace='specialties')),
    
    # Equipment management
    path('equipment/', include('equipment.urls', namespace='equipment')),
    
    # Reports and analytics
    path('reports/', include('reports.urls', namespace='reports')),
    
    # Billing and sales
    path('billing/', include('billing.urls', namespace='billing')),
    
    # API endpoints
    path('api/v1/', include('api.urls', namespace='api')),
]

# Media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (if installed)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers
handler404 = 'accounts.views.handler404'
handler500 = 'accounts.views.handler500'
handler403 = 'accounts.views.handler403'
