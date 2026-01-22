from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Building, Room, ServicePoint, Floor, Pathway, Route
import json


def home(request):
    """Homepage with campus overview and search"""
    buildings = Building.objects.all().order_by('name')
    services = ServicePoint.objects.all().order_by('service_type', 'name')
    
    # Prepare JSON data for map
    import json
    buildings_data = [{
        'id': b.id,
        'name': b.name,
        'code': b.code,
        'latitude': b.latitude,
        'longitude': b.longitude,
        'total_floors': b.total_floors,
    } for b in buildings]
    
    services_data = [{
        'id': s.id,
        'name': s.name,
        'service_type': s.get_service_type_display(),
        'latitude': s.latitude,
        'longitude': s.longitude,
    } for s in services]
    
    # Count statistics for the dashboard
    context = {
        'buildings': buildings,
        'services': services,
        'building_count': buildings.count(),
        'service_count': services.count(),
        'floor_count': Floor.objects.count(),
        'buildings_json': json.dumps(buildings_data),
        'services_json': json.dumps(services_data),
        # CUT Campus coordinates (Chinhoyi, Zimbabwe)
        'campus_lat': -17.28332,
        'campus_lon': 30.21668,
        'campus_zoom': 16,
        'model_type': 'Building',
    }
    return render(request, 'home.html', context)


def about(request):
    """About page with app information"""
    context = {
        'app_version': '1.0',
        'institution': 'Chinhoyi University of Technology',
        'campus_location': 'Chinhoyi, Zimbabwe',
    }
    return render(request, 'about.html', context)


def building_detail(request, building_id):
    """View details for a specific building with floors and rooms"""
    building = get_object_or_404(Building, id=building_id)
    floors = building.floors.all().order_by('floor_number')
    rooms = building.rooms.all().order_by('floor__floor_number', 'room_number')
    services = ServicePoint.objects.filter(building=building)
    
    context = {
        'building': building,
        'floors': floors,
        'rooms': rooms,
        'services': services,
    }
    return render(request, 'building_detail.html', context)


def floor_detail(request, building_id, floor_id):
    """View specific floor with rooms and services"""
    building = get_object_or_404(Building, id=building_id)
    floor = get_object_or_404(Floor, id=floor_id, building=building)
    rooms = floor.rooms.all().order_by('room_number')
    services = floor.services.all()
    
    context = {
        'building': building,
        'floor': floor,
        'rooms': rooms,
        'services': services,
        'floorplan_url': floor.floorplan_image.url if floor.floorplan_image else None,
    }
    return render(request, 'floor_detail.html', context)


def room_detail(request, building_id, room_id):
    """View room details"""
    building = get_object_or_404(Building, id=building_id)
    room = get_object_or_404(Room, id=room_id, building=building)
    services_in_room = room.services.all()
    
    context = {
        'building': building,
        'room': room,
        'services': services_in_room,
    }
    return render(request, 'room_detail.html', context)


def service_points(request):
    """List all service points with filtering"""
    services = ServicePoint.objects.all().order_by('service_type', 'name')
    
    # Filter by service type if provided
    service_type = request.GET.get('type', None)
    if service_type:
        services = services.filter(service_type=service_type)
    
    # Filter by accessibility
    if request.GET.get('accessibility') == 'true':
        services = services.exclude(accessibility_features__isnull=True)
    
    # Group by type for display
    service_types = ServicePoint.SERVICE_TYPES
    
    context = {
        'services': services,
        'service_types': service_types,
        'selected_type': service_type,
    }
    return render(request, 'service_points.html', context)


def service_detail(request, service_id):
    """View service point details"""
    service = get_object_or_404(ServicePoint, id=service_id)
    
    # Find nearby services using basic distance calculation
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    # Calculate distances to all other services
    all_services = ServicePoint.objects.exclude(id=service.id)
    services_with_distance = []
    
    for s in all_services:
        distance = haversine_distance(
            service.latitude, service.longitude,
            s.latitude, s.longitude
        )
        services_with_distance.append((s, distance))
    
    # Sort by distance and get top 5
    services_with_distance.sort(key=lambda x: x[1])
    nearby_services = [(s, round(dist, 3)) for s, dist in services_with_distance[:5]]
    
    # Google Maps directions URL for current service
    google_maps_url = f"https://www.google.com/maps/dir/?api=1&destination={service.latitude},{service.longitude}&travelmode=walking"
    
    context = {
        'service': service,
        'nearby_services': nearby_services,
        'google_maps_url': google_maps_url,
    }
    return render(request, 'service_detail.html', context)


def search(request):
    """Search buildings, rooms, and service points"""
    query = request.GET.get('q', '')
    results = []

    if query:
        buildings = Building.objects.filter(Q(name__icontains=query) | Q(code__icontains=query))
        rooms = Room.objects.filter(Q(name__icontains=query) | Q(room_number__icontains=query))
        services = ServicePoint.objects.filter(Q(name__icontains=query) | Q(service_type__icontains=query))
        
        # Add model type info to each result for template display
        for building in buildings:
            building.model_type = 'Building'
        for room in rooms:
            room.model_type = 'Room'
        for service in services:
            service.model_type = 'ServicePoint'
        
        results = list(buildings) + list(rooms) + list(services)

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search_results.html', context)


def directions(request, start_id, end_id):
    """Get directions between two service points"""
    start_service = get_object_or_404(ServicePoint, id=start_id)
    end_service = get_object_or_404(ServicePoint, id=end_id)
    
    # Check for accessibility requirement
    accessibility_required = request.GET.get('accessibility') == 'true'
    
    # Get or calculate route
    route = get_or_create_route(start_id, end_id, accessibility_required)
    
    # Get pathways for detailed directions
    pathfinder = PathFinder(accessibility_required=accessibility_required)
    path_result = pathfinder.find_shortest_path(start_id, end_id)
    
    if not path_result:
        context = {'error': 'No accessible route found.'}
        return render(request, 'directions.html', context)
    
    # Build step-by-step directions
    steps = []
    for idx, pathway in enumerate(path_result['pathways'], 1):
        steps.append({
            'number': idx,
            'instruction': f"Take the {pathway.get_pathway_type_display().lower()}",
            'distance': pathway.distance_meters,
            'time': pathway.estimated_time_minutes,
        })
    
    context = {
        'start_service': start_service,
        'end_service': end_service,
        'route': route,
        'steps': steps,
        'total_distance': path_result['distance_meters'],
        'total_time': path_result['estimated_time_minutes'],
        'accessibility_required': accessibility_required,
    }
    return render(request, 'directions.html', context)


def api_find_nearest_service(request):
    """API endpoint to find nearest service point"""
    try:
        latitude = float(request.GET.get('lat'))
        longitude = float(request.GET.get('lon'))
        service_type = request.GET.get('type', None)
        radius = int(request.GET.get('radius', 200))
        accessibility = request.GET.get('accessibility') == 'true'
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    # Create point from coordinates
    user_location = Point(longitude, latitude, srid=4326)
    
    # Use pathfinder to find nearest service
    pathfinder = PathFinder(accessibility_required=accessibility)
    nearest = pathfinder.find_nearest_service(user_location, service_type, radius)
    
    if not nearest:
        return JsonResponse({'error': 'No services found'}, status=404)
    
    return JsonResponse({
        'id': nearest.id,
        'name': nearest.name,
        'type': nearest.get_service_type_display(),
        'latitude': float(nearest.latitude),
        'longitude': float(nearest.longitude),
        'description': nearest.description,
        'contact': nearest.contact_phone,
        'office_hours': nearest.office_hours,
    })


def api_nearby_services(request):
    """API endpoint for nearby services"""
    try:
        latitude = float(request.GET.get('lat'))
        longitude = float(request.GET.get('lon'))
        service_type = request.GET.get('type', None)
        radius = int(request.GET.get('radius', 500))
        limit = int(request.GET.get('limit', 5))
        accessibility = request.GET.get('accessibility') == 'true'
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
    
    user_location = Point(longitude, latitude, srid=4326)
    
    pathfinder = PathFinder(accessibility_required=accessibility)
    services = pathfinder.find_nearby_services(user_location, service_type, radius, limit)
    
    return JsonResponse({
        'services': [
            {
                'id': s.id,
                'name': s.name,
                'type': s.get_service_type_display(),
                'latitude': float(s.latitude),
                'longitude': float(s.longitude),
            }
            for s in services
        ]
    })


def api_route_geometry(request, start_id, end_id):
    """API endpoint to get route geometry (for map display)"""
    route = get_object_or_404(Route, start_point_id=start_id, end_point_id=end_id)
    
    if route.route_geometry:
        coords = list(route.route_geometry.coords)
        return JsonResponse({
            'coordinates': coords,
            'distance': route.distance_meters,
            'time': route.estimated_time_minutes,
        })
    return JsonResponse({'error': 'Route not found'}, status=404)


# =====================================================
# AUTHENTICATION VIEWS
# =====================================================

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_page = request.GET.get('next', '/')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'auth/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f'Welcome to CUT Guide, {username}!')
        return redirect('/')
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('/')


@login_required(login_url='login')
def profile_view(request):
    """User profile page"""
    return render(request, 'auth/profile.html', {'user': request.user})
    
    return JsonResponse({'error': 'Route geometry not available'}, status=404)


