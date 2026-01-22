
# Register your models here.
from django.contrib import admin
from .models import Building, Room, ServicePoint, Route, Floor, Pathway, ServiceArea


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'total_floors')
    search_fields = ('name', 'code')
    list_filter = ('total_floors',)


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('building', 'floor_number', 'floor_name')
    list_filter = ('building',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'name', 'building', 'room_type')
    search_fields = ('name', 'room_number')
    list_filter = ('building', 'room_type')


@admin.register(ServicePoint)
class ServicePointAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'building')
    search_fields = ('name', 'service_type')
    list_filter = ('service_type', 'building')


@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    list_display = ('pathway_type', 'distance_meters', 'is_accessible')
    list_filter = ('pathway_type', 'is_accessible')


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('start_point', 'end_point', 'distance_meters', 'is_accessible')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ('service_point', 'buffer_radius_meters')
