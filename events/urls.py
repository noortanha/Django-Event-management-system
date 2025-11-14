"""
URL configuration for event_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from events import views


urlpatterns = [
    
   
    path('events/create/', views.event_create, name='event_create'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:id>/', views.event_details, name='event_details'),
    path('events/update/<int:id>/', views.event_update, name='event_update'),
    path('events/delete/<int:id>/', views.event_delete, name='event_delete'),
    path('events/today/', views.today_events, name='today_events'),

    path('events/upcoming/', views.upcoming_events, name='upcoming_events'),
    path('events/past/', views.past_events, name='past_events'),
    path('events/by_category/', views.events_by_category, name='events_by_category'),

   
    path('category/add/', views.add_category, name='add_category'),
    path('category/update/<int:id>/', views.update_category, name='update_category'),
    path('category/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('category/list/', views.category_list, name='category_list'),

    path('participants/', views.participant_list, name='participant_list'),
    path('participants/delete/<int:id>/', views.delete_participant, name='delete_participant'),

    path('dashboard/', views.dashboard_redirect, name='dashboard-redirect'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer-dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant-dashboard'),

    path('rsvp/<int:event_id>/', views.rsvp_event, name='rsvp_event'),


    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('organizer/dashboard/', views.organizer_dashboard, name='organizer-dashboard'),
    path('participant/dashboard/', views.participant_dashboard, name='participant-dashboard'),
    
]
    
    
   

