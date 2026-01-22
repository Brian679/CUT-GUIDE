# CUT-Guide Campus GIS Navigation System

## 📍 MVP Application Redesign Summary

This document outlines the transformation of the CUT-Guide application to align with the Campus GIS Navigation MVP specification.

---

## 🎯 What Changed

### **Database Models (Enhanced with GIS Support)**

#### New Models Added:
1. **Floor** - Individual floors within buildings with floorplan support
2. **Pathway** - Indoor/outdoor paths and corridors for navigation  
3. **ServiceArea** - Service coverage areas for proximity-based identification

#### Enhanced Models:
- **Building**: Added GIS Point/Polygon fields, accessibility features, contact info, floor count
- **Room**: Added floor reference, room type, capacity, office number, accessibility features
- **ServicePoint**: Expanded service types, added accessibility & contact info, floor/room references
- **Route**: Added route geometry, accessibility flag, and route type classification

### **Routing & Navigation Engine**

Created `routing.py` with `PathFinder` class implementing:
- **Dijkstra's Algorithm** for shortest path calculation
- **Accessibility-aware routing** for wheelchair users
- **Service proximity detection** - find nearest/nearby services
- **Multi-floor navigation** support

Key Functions:
```python
PathFinder.find_shortest_path(start_id, end_id)
PathFinder.find_nearest_service(location, service_type, radius)
PathFinder.find_nearby_services(location, service_type, radius, limit)
```

### **Updated Views & API Endpoints**

#### New Views:
- `floor_detail()` - View specific floor with rooms & services
- `room_detail()` - View individual room details
- `service_detail()` - Enhanced service point view with nearby services
- `directions()` - Step-by-step navigation between points

#### New API Endpoints:
- `GET /api/nearest-service/` - Find nearest service point
- `GET /api/nearby-services/` - Get nearby services list
- `GET /api/route-geometry/<start_id>/<end_id>/` - Get route coordinates

#### Enhanced Views:
- `service_points()` - Added filtering by type and accessibility
- `search()` - Improved with model_type tracking
- `home()` - Enhanced dashboard with statistics

### **Frontend Enhancements**

#### Base Template (`base.html`):
- Integrated **Leaflet.js** for interactive maps
- Added responsive design for mobile
- Sticky navigation bar
- Enhanced styling with gradients and animations
- Custom map initialization functions

#### New Templates:
1. **home.html** - Interactive campus overview with statistics & map
2. **floor_detail.html** - Floor layout with floorplan image support
3. **room_detail.html** - Detailed room information with map
4. **service_detail.html** - Service point details with nearby services
5. **directions.html** - Turn-by-turn navigation display
6. **Updated service_points.html** - Service directory with filtering & map

#### UI Features:
- 📍 Interactive campus map with Leaflet
- 🧭 Service filtering by type and accessibility
- ♿ Accessibility badges and information
- 📊 Floor/room navigation
- 📱 Mobile-responsive design
- 🗺️ Turn-by-turn directions
- 📈 Campus statistics dashboard

### **GIS Integration**

#### Spatial Database Setup:
- Configured Django GIS with **SpatiaLite** (dev) / **PostGIS** (production)
- Models use `PointField` for locations and `LineStringField` for paths
- `PolygonField` for building footprints and service areas
- Distance calculations for proximity searches

#### Coordinates:
- SRID 4326 (WGS 84) for all spatial fields
- Support for latitude/longitude queries

### **URL Routes**

New URL patterns added:
```python
path('building/<int:building_id>/floor/<int:floor_id>/', floor_detail)
path('building/<int:building_id>/room/<int:room_id>/', room_detail)
path('service/<int:service_id>/', service_detail)
path('directions/<int:start_id>/<int:end_id>/', directions)
path('api/nearest-service/', api_find_nearest_service)
path('api/nearby-services/', api_nearby_services)
path('api/route-geometry/<int:start_id>/<int:end_id>/', api_route_geometry)
```

---

## 🏗️ Architecture

### **MVC Structure**
```
Models (GIS-enabled)
    ↓
Views (with routing logic)
    ↓
Templates (Leaflet maps)
    ↓
API Endpoints (JSON responses)
```

### **Key Components**

1. **Routing Engine** (`routing.py`)
   - Implements Dijkstra's algorithm
   - Handles pathfinding with accessibility constraints
   - Service proximity detection

2. **GIS Layer**
   - Spatial data storage
   - Distance calculations
   - Coordinate transformations

3. **Interactive Frontend**
   - Leaflet-based mapping
   - Real-time filtering
   - Responsive design

---

## 🚀 MVP Features Implemented

✅ **Interactive Campus Map** - Digitized buildings and pathways
✅ **Searchable Directory** - Find buildings, rooms, services by name/code/type
✅ **Indoor-Outdoor Navigation** - Dijkstra-powered routing algorithm
✅ **Mobile-Friendly Interface** - Responsive Bootstrap design
✅ **Service Area Identification** - Find nearest services by proximity
✅ **Accessibility Support** - Filter by accessibility features
✅ **Floor Management** - Multi-floor support with floorplans
✅ **API Endpoints** - RESTful interfaces for mobile apps

---

## 📋 Data Model Overview

```
Building (1) ──→ (N) Floor
    ↓
    └──→ (N) Room
    └──→ (N) ServicePoint
    └──→ (N) Pathway

Room (1) ──→ (N) ServicePoint
Floor (1) ──→ (N) ServicePoint

ServicePoint (1) ──→ (1) ServiceArea

Pathway connects ServicePoints with routing info
Route caches pre-calculated paths between ServicePoints
```

---

## ⚙️ Technology Stack

**Backend:**
- Django 5.2.8
- Python 3.8+
- GeoDjango (GIS)

**Database:**
- SQLite + SpatiaLite (Development)
- PostgreSQL + PostGIS (Production)

**Frontend:**
- HTML5 / CSS3
- Bootstrap 5.3
- Leaflet.js (Maps)
- JavaScript (ES6)

**Key Libraries:**
- `django.contrib.gis` - Spatial database support
- `leaflet` - Interactive mapping

---

## 🔧 Setup Instructions

### Requirements
```bash
pip install django==5.2.8
pip install django-extensions
pip install pillow  # For floorplan images
```

### Database Setup (Development)
```bash
python manage.py migrate
python manage.py createsuperuser
```

### For Production (PostgreSQL + PostGIS)
Update settings.py to use PostGIS backend and install PostGIS on your database server.

---

## 📱 Mobile-First Design

- Responsive Bootstrap layout
- Touch-friendly interface
- Optimized map interactions
- Location-based services via API
- Works on all modern browsers

---

## 🔍 Search & Discovery

**Search Capabilities:**
- By building name or code
- By room number
- By service type (library, admin office, water point, etc.)
- By accessibility features

**Filter Options:**
- Service type dropdown
- Accessibility filter
- Location-based proximity

---

## 🗺️ Navigation & Routing

**Features:**
- Shortest path calculation (Dijkstra)
- Accessibility-aware routes
- Multi-floor navigation support
- Distance and time estimates
- Step-by-step turn-by-turn directions

**Example Usage:**
```python
from Navigator.routing import PathFinder

pf = PathFinder(accessibility_required=True)
result = pf.find_shortest_path(start_id=1, end_id=5)
# Returns: distance, time, path IDs, pathways
```

---

## 📊 API Documentation

### Nearest Service
```
GET /api/nearest-service/?lat=value&lon=value&type=library&radius=200&accessibility=true
Response: {id, name, type, latitude, longitude, description, contact, office_hours}
```

### Nearby Services
```
GET /api/nearby-services/?lat=value&lon=value&type=library&radius=500&limit=5
Response: {services: [{id, name, type, latitude, longitude}, ...]}
```

### Route Geometry
```
GET /api/route-geometry/1/5/
Response: {coordinates: [[lat,lon], ...], distance, time}
```

---

## 🎓 Next Steps (Future Enhancements)

Phase 2 (Future):
- ❌ iOS app
- ❌ Real-time crowd density
- ❌ Bluetooth indoor positioning
- ❌ Augmented reality navigation
- ❌ Advanced analytics dashboard
- ❌ Multi-campus support
- ❌ AI-based recommendations

---

## 📈 Success Metrics (MVP)

Target KPIs:
- ✓ ≥ 95% routing accuracy
- ✓ < 2 seconds response time
- ✓ ≥ 80% user satisfaction
- ✓ Improved navigation efficiency vs static maps

---

## 👥 Development Team

Designed for **Chinhoyi University of Technology (CUT)**
Campus Navigation System - Version 1.0 MVP

---

## 📝 Notes

- The application uses Leaflet.js with OpenStreetMap tiles for development
- For production, consider using Mapbox or similar service
- Spatial indexes on GIS fields recommended for large datasets
- Regular backups of geographic data recommended
- Consider adding caching for frequently accessed routes

---

**Last Updated:** January 19, 2026
**Status:** MVP Phase 1 Complete ✅
