from django.urls import path
from . import views

app_name = 'eventpollapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/vote/<int:date_option_id>/', views.vote_date, name='vote_date'),
    path('events/<int:event_id>/finalize/', views.finalize_event_date, name='finalize_event_date'),
    path('events/<int:event_id>/requirements/add/', views.add_requirement, name='add_requirement'),
    path('requirements/<int:requirement_id>/toggle/', views.toggle_requirement_completion, name='toggle_requirement_completion'),
    path('events/<int:event_id>/comments/add/', views.add_comment, name='add_comment'),
    path('events/<int:event_id>/participation/', views.update_participation, name='update_participation'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('<int:event_id>/edit/', views.edit_event, name='edit_event'),
]