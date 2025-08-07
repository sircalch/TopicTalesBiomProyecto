from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import User, Organization, Subscription, UserProfile, Notification


class CustomLoginView(LoginView):
    """
    Custom login view for TopicTales Biomédica
    """
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Intentar redirigir al dashboard, si no existe ir al admin
        try:
            from django.urls import reverse
            return reverse('dashboard:index')
        except:
            return '/admin/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar Sesión - TopicTales Biomédica'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido, {form.get_user().get_full_name()}!')
        return super().form_valid(form)


@login_required
def profile(request):
    """
    User profile view
    """
    return render(request, 'accounts/profile.html', {
        'title': 'Mi Perfil',
        'user': request.user,
    })


@login_required
def settings(request):
    """
    User settings view
    """
    return render(request, 'accounts/settings.html', {
        'title': 'Configuración',
    })


@login_required
def users_list(request):
    """
    List all users in the organization (admin only)
    """
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para ver esta página.')
        return redirect('dashboard:index')
    
    organization = request.user.profile.organization
    users = User.objects.filter(profile__organization=organization)
    
    return render(request, 'accounts/users.html', {
        'title': 'Usuarios',
        'users': users,
    })


@login_required
def create_user(request):
    """
    Create new user (admin only)
    """
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard:index')
    
    return render(request, 'accounts/create_user.html', {
        'title': 'Crear Usuario',
    })


@login_required
def edit_user(request, user_id):
    """
    Edit user (admin only)
    """
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, id=user_id, profile__organization=request.user.profile.organization)
    
    return render(request, 'accounts/edit_user.html', {
        'title': 'Editar Usuario',
        'edit_user': user,
    })


@login_required
def organization_settings(request):
    """
    Organization settings (admin only)
    """
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para ver esta página.')
        return redirect('dashboard:index')
    
    organization = request.user.profile.organization
    
    return render(request, 'accounts/organization.html', {
        'title': 'Configuración de la Organización',
        'organization': organization,
    })


@login_required
def subscription_info(request):
    """
    Subscription information (admin only)
    """
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para ver esta página.')
        return redirect('dashboard:index')
    
    subscription = request.user.profile.organization.subscription
    
    return render(request, 'accounts/subscription.html', {
        'title': 'Información de Suscripción',
        'subscription': subscription,
    })


@login_required
def upgrade_plan(request):
    """
    Upgrade subscription plan
    """
    subscription = request.user.profile.organization.subscription
    
    return render(request, 'accounts/upgrade.html', {
        'title': 'Actualizar Plan',
        'subscription': subscription,
    })


@login_required
def export_users(request):
    """Exportar usuarios a CSV"""
    import csv
    from django.http import HttpResponse
    
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard:index')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Email', 'Nombre', 'Organización', 'Estado', 'Último Acceso'])
    
    organization = request.user.profile.organization
    users = User.objects.filter(profile__organization=organization)
    
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.get_full_name(),
            user.profile.organization.name if user.profile.organization else '',
            'Activo' if user.is_active else 'Inactivo',
            user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca'
        ])
    
    return response


@login_required
def bulk_user_actions(request):
    """Acciones en lote para usuarios"""
    if not request.user.is_administrative_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.get('selected_users', '').split(',')
        selected_ids = [id for id in selected_ids if id.strip()]
        
        if not selected_ids:
            messages.error(request, 'No se seleccionaron usuarios.')
            return redirect('accounts:users')
        
        users = User.objects.filter(id__in=selected_ids, profile__organization=request.user.profile.organization)
        
        if action == 'activate':
            users.update(is_active=True)
            messages.success(request, f'{users.count()} usuarios activados.')
            
        elif action == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f'{users.count()} usuarios desactivados.')
            
        elif action == 'export_selected':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="usuarios_seleccionados.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Usuario', 'Email', 'Nombre', 'Estado'])
            
            for user in users:
                writer.writerow([
                    user.username,
                    user.email,
                    user.get_full_name(),
                    'Activo' if user.is_active else 'Inactivo'
                ])
            
            return response
    
    return redirect('accounts:users')


# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    """Custom 403 error handler"""
    return render(request, 'errors/403.html', status=403)


# Notification views
@login_required
def notifications_list(request):
    """Get user notifications as JSON for navbar dropdown"""
    notifications = Notification.objects.filter(
        user=request.user,
        is_dismissed=False
    ).order_by('-created_at')[:10]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'icon': notification.get_icon(),
            'priority_class': notification.get_priority_class(),
            'action_url': notification.action_url or '#'
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': notifications.filter(is_read=False).count()
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    try:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return JsonResponse({
            'success': True,
            'marked_count': count
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def create_sample_notifications(request):
    """Create sample notifications for testing (dev only)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Create sample notifications
    sample_notifications = [
        {
            'title': 'Cita próxima',
            'message': 'Tienes una cita con Juan Pérez en 30 minutos',
            'notification_type': 'appointment',
            'priority': 'high'
        },
        {
            'title': 'Nuevo paciente registrado',
            'message': 'María García se ha registrado como nueva paciente',
            'notification_type': 'patient',
            'priority': 'medium'
        },
        {
            'title': 'Recordatorio',
            'message': 'No olvides revisar los expedientes pendientes',
            'notification_type': 'reminder',
            'priority': 'low'
        },
        {
            'title': 'Mensaje importante',
            'message': 'El sistema se actualizará mañana a las 2:00 AM',
            'notification_type': 'system',
            'priority': 'high'
        },
    ]
    
    created_count = 0
    for notif_data in sample_notifications:
        notification = Notification.objects.create(
            user=request.user,
            **notif_data
        )
        created_count += 1
    
    return JsonResponse({
        'success': True,
        'created': created_count,
        'message': f'Se crearon {created_count} notificaciones de prueba'
    })
