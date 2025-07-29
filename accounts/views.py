from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import User, Organization, Subscription, UserProfile


class CustomLoginView(LoginView):
    """
    Custom login view for TopicTales Biomédica
    """
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard:index')
    
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
    
    return render(request, 'accounts/users_list.html', {
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
