from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Building navigation
    path('building/<int:building_id>/', views.building_detail, name='building_detail'),
    path('building/<int:building_id>/floor/<int:floor_id>/', views.floor_detail, name='floor_detail'),
    path('building/<int:building_id>/room/<int:room_id>/', views.room_detail, name='room_detail'),
    
    # Services
    path('services/', views.service_points, name='service_points'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    
    # Navigation & Directions
    path('directions/<int:start_id>/<int:end_id>/', views.directions, name='directions'),
    path('search/', views.search, name='search'),
    
    # API endpoints
    path('api/nearest-service/', views.api_find_nearest_service, name='api_nearest_service'),
    path('api/nearby-services/', views.api_nearby_services, name='api_nearby_services'),
    path('api/route-geometry/<int:start_id>/<int:end_id>/', views.api_route_geometry, name='api_route_geometry'),
]
