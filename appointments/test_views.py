from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required  
def test_schedule_endpoint(request):
    """
    Test endpoint to verify API is working
    """
    return JsonResponse({
        'success': True,
        'message': 'API endpoint is working correctly',
        'method': request.method,
        'user': request.user.username
    })