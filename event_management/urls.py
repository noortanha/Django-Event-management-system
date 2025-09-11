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
    path("", views.home, name="home"),

    path("events/create", views.event_create, name="event_create"),
    path("events/event_list", views.event_list, name="event_list"),
    path("events/event_details/<int:id>/", views.event_details, name= "event_details"),
    path("events/update/<int:id>/",views.event_update, name="event_update"),
    path('events/<int:id>/add_participant/', views.add_participant_to_event, name='add_participant_to_event'),
    path("events/upcoming/", views.upcoming_events, name="upcoming_events"),
    path("events/past/", views.past_events, name="past_events"),
    path("participants/" , views.participant_list, name="participant_list"),
    path("participants/add", views.add_participant, name="add_participant"),
    path("participants/update/<int:id>/", views.update_participant, name="update_participants"),
    path("participants/delete/<int:id>/", views.delete_participant, name="delete_participant"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/add", views.add_category, name="add_category"),
    path("categories/delete/<int:id>", views.delete_category, name="delete_category"),
    path('categories/update/<int:id>/', views.update_category,name='update_category'),
    path("dashboard", views.dashboard, name="dashboard"),
    
    path("categories/events_by_category/<int:id>", views.events_by_category,name="events_by_category")
    
   
]
