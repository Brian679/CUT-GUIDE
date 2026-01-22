from django.db import models
from django.utils import timezone


class Building(models.Model):
    """Campus building"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Location fields
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Building metadata
    total_floors = models.IntegerField(default=1)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    accessibility_features = models.TextField(blank=True, null=True, help_text="Wheelchair access, elevators, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Floor(models.Model):
    """Individual floor in a building with floorplan"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField()
    floor_name = models.CharField(max_length=100, blank=True, help_text="e.g., 'Ground Floor', 'Level 1'")
    
    # Floorplan image/map
    floorplan_image = models.ImageField(upload_to='floorplans/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('building', 'floor_number')
        ordering = ['building', 'floor_number']

    def __str__(self):
        return f"{self.building.name} - {self.floor_name or f'Floor {self.floor_number}'}"


class Room(models.Model):
    """Individual room within a building"""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='rooms')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='rooms')
    
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(
        max_length=50,
        choices=[
            ('office', 'Office'),
            ('classroom', 'Classroom'),
            ('lab', 'Laboratory'),
            ('lecture_hall', 'Lecture Hall'),
            ('meeting_room', 'Meeting Room'),
            ('storage', 'Storage'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    # Location fields
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Room metadata
    capacity = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    office_number = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., extension")
    accessibility_features = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('building', 'room_number')
        ordering = ['building', 'floor', 'room_number']

    def __str__(self):
        return f"{self.building.code}-{self.room_number} ({self.name})"


class ServicePoint(models.Model):
    """Campus facility or service"""
    SERVICE_TYPES = [
        ('library', 'Library'),
        ('admin_office', 'Administration Office'),
        ('water_point', 'Water Point'),
        ('toilet', 'Toilet/Restroom'),
        ('canteen', 'Canteen/Cafeteria'),
        ('lab', 'Laboratory'),
        ('classroom', 'Classroom'),
        ('office', 'Office'),
        ('parking', 'Parking'),
        ('medical', 'Medical/Health Center'),
        ('security', 'Security Post'),
        ('lost_and_found', 'Lost & Found'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Location relationships
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    
    # Location fields
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Service metadata
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    office_hours = models.TextField(blank=True, null=True, help_text="e.g., '9AM-5PM Mon-Fri'")
    accessibility_features = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['service_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"


class Pathway(models.Model):
    """Paths and corridors for navigation (indoor/outdoor)"""
    PATHWAY_TYPES = [
        ('outdoor', 'Outdoor Path'),
        ('indoor_corridor', 'Indoor Corridor'),
        ('staircase', 'Staircase'),
        ('ramp', 'Ramp/Slope'),
        ('elevator', 'Elevator'),
        ('escalator', 'Escalator'),
    ]
    
    name = models.CharField(max_length=100, blank=True)
    pathway_type = models.CharField(max_length=30, choices=PATHWAY_TYPES)
    
    # Start and end buildings/rooms
    start_point = models.ForeignKey(ServicePoint, on_delete=models.CASCADE, related_name='paths_from', null=True, blank=True)
    end_point = models.ForeignKey(ServicePoint, on_delete=models.CASCADE, related_name='paths_to', null=True, blank=True)
    
    # Metadata
    distance_meters = models.FloatField()
    estimated_time_minutes = models.FloatField()
    is_accessible = models.BooleanField(default=True, help_text="Wheelchair accessible")
    floor_from = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='paths_from_floor')
    floor_to = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='paths_to_floor')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_pathway_type_display()} - {self.distance_meters}m"


class Route(models.Model):
    """Pre-calculated or user-requested route between two points"""
    start_point = models.ForeignKey(ServicePoint, on_delete=models.CASCADE, related_name='route_starts')
    end_point = models.ForeignKey(ServicePoint, on_delete=models.CASCADE, related_name='route_ends')
    
    # Metrics
    distance_meters = models.FloatField()
    estimated_time_minutes = models.FloatField()
    
    # Route characteristics
    is_accessible = models.BooleanField(default=True, help_text="Wheelchair accessible route")
    route_type = models.CharField(
        max_length=50,
        choices=[
            ('indoor', 'Entirely Indoor'),
            ('outdoor', 'Entirely Outdoor'),
            ('mixed', 'Mixed Indoor/Outdoor'),
        ],
        default='mixed'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('start_point', 'end_point')

    def __str__(self):
        return f"{self.start_point.name} → {self.end_point.name}"


class ServiceArea(models.Model):
    """Service area for proximity-based identification"""
    service_point = models.OneToOneField(ServicePoint, on_delete=models.CASCADE, related_name='service_area')
    
    # Use buffer distance for simpler implementation
    buffer_radius_meters = models.IntegerField(default=100, help_text="Proximity radius in meters")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Service Area: {self.service_point.name}"
