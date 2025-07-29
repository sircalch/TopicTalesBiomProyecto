from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('list/', views.appointment_list, name='list'),
    path('create/', views.appointment_create, name='create'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/edit/', views.appointment_edit, name='edit'),
    path('<int:appointment_id>/cancel/', views.appointment_cancel, name='cancel'),
    path('<int:appointment_id>/reschedule/', views.appointment_reschedule, name='reschedule'),
    path('<int:appointment_id>/complete/', views.appointment_complete, name='complete'),
    
    # AJAX endpoints
    path('api/events/', views.calendar_events, name='calendar_events'),
    path('api/available-slots/', views.available_slots, name='available_slots'),
    path('api/quick-appointment/', views.quick_appointment, name='quick_appointment'),
]