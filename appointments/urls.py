from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('list/', views.appointment_list, name='list'),
    path('create/', views.appointment_create, name='create'),
    path('today/', views.todays_appointments, name='todays_appointments'),
    path('schedule/', views.doctor_schedule_config, name='schedule_config'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/edit/', views.appointment_edit, name='edit'),
    path('<int:appointment_id>/cancel/', views.appointment_cancel, name='cancel'),
    path('<int:appointment_id>/reschedule/', views.appointment_reschedule, name='reschedule'),
    path('<int:appointment_id>/complete/', views.appointment_complete, name='complete'),
    
    # AJAX endpoints
    path('api/events/', views.calendar_events, name='calendar_events'),
    path('api/available-slots/', views.available_slots, name='available_slots'),
    path('api/quick-appointment/', views.quick_appointment, name='quick_appointment'),
    path('api/update-appointment/', views.update_appointment_time, name='update_appointment_time'),
    path('api/appointment-details/<int:appointment_id>/', views.appointment_details_ajax, name='appointment_details_ajax'),
    
    # Schedule management endpoints
    path('api/create-schedule/', views.create_schedule, name='create_schedule'),
    path('api/update-schedule/', views.update_schedule, name='update_schedule'),
    path('api/delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
]