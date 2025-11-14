from django.urls import path
from django.contrib.auth.views import LogoutView

from User import views


urlpatterns = [
    path('register/', views.sign_up, name='register'),
    path('login/', views.sign_in, name='login'),
    path('log_out/', LogoutView.as_view(next_page='home'), name='logout'),
    path('activate/<int:user_id>/<str:token>/', views.activate_user),
    

    
    
]