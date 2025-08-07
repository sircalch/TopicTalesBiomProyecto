"""
Language switching views
"""
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def set_language(request):
    """Set the language preference"""
    language = request.POST.get('language', 'es')
    next_url = request.POST.get('next', '/')
    
    # Validate language
    if language not in ['es', 'en']:
        language = 'es'
    
    # Store in session
    request.session['django_language'] = language
    
    # Redirect back
    return redirect(next_url)

@csrf_exempt
@require_POST
def set_language_ajax(request):
    """Set language via AJAX"""
    language = request.POST.get('language', 'es')
    
    # Validate language
    if language not in ['es', 'en']:
        language = 'es'
    
    # Store in session
    request.session['django_language'] = language
    
    return JsonResponse({'success': True, 'language': language})