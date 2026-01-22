# 🏗️ CUT-Guide Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER (Frontend)                    │
├─────────────────────────────────────────────────────────────────┤
│  Mobile Browser │ Desktop Browser │ Native Mobile App (Future)   │
│  (Bootstrap UI) │   (Leaflet Map) │    (API Consumer)           │
└────────┬─────────────────────────────────┬──────────────────────┘
         │                                  │
         │ HTTP/HTTPS                       │ JSON REST API
         │                                  │
┌────────▼──────────────────────────────────▼──────────────────────┐
│                    DJANGO APPLICATION LAYER                      │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  URL Router (/urls.py)                                         │
│  ├── / (home)                                                  │
│  ├── /building/<id>/                                          │
│  ├── /building/<id>/floor/<floor_id>/                         │
│  ├── /building/<id>/room/<room_id>/                           │
│  ├── /service/<id>/                                           │
│  ├── /services/                                               │
│  ├── /search/?q=query                                         │
│  ├── /directions/<start_id>/<end_id>/                         │
│  └── /api/*                                                   │
│                                                                  │
│  Views Layer (/views.py)                                       │
│  ├── home() - Dashboard with stats                           │
│  ├── building_detail() - Building info                        │
│  ├── floor_detail() - Floor layout                            │
│  ├── room_detail() - Room information                         │
│  ├── service_detail() - Service info + nearby               │
│  ├── service_points() - Service directory                     │
│  ├── search() - Search functionality                          │
│  ├── directions() - Navigation instructions                   │
│  ├── api_find_nearest_service() - API endpoint               │
│  ├── api_nearby_services() - API endpoint                    │
│  └── api_route_geometry() - API endpoint                     │
│                                                                  │
│  Routing Engine (/routing.py)                                 │
│  ├── PathFinder class                                         │
│  ├── Dijkstra's Algorithm                                    │
│  ├── find_shortest_path()                                    │
│  ├── find_nearest_service()                                  │
│  ├── find_nearby_services()                                  │
│  └── Accessibility filtering                                │
│                                                                  │
│  Template Rendering (/templates/)                             │
│  ├── base.html (Leaflet + Bootstrap)                         │
│  ├── home.html (Dashboard)                                   │
│  ├── building_detail.html                                    │
│  ├── floor_detail.html                                       │
│  ├── room_detail.html                                        │
│  ├── service_detail.html                                     │
│  ├── service_points.html                                     │
│  ├── directions.html                                         │
│  └── search_results.html                                     │
│                                                                  │
└─────────────────┬──────────────────────────────────────────────┘
                  │
                  │ ORM Queries
                  │
┌─────────────────▼──────────────────────────────────────────────┐
│                    MODEL LAYER (/models.py)                    │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Core Models (with GIS support):                              │
│                                                                  │
│  Building                                                      │
│  ├── name, code, description                                 │
│  ├── location (GIS Point)                                    │
│  ├── outline (GIS Polygon)                                   │
│  ├── total_floors, contact_phone                            │
│  └── accessibility_features                                 │
│                                                                  │
│  Floor                                                        │
│  ├── building (FK)                                          │
│  ├── floor_number, floor_name                               │
│  └── floorplan_image                                        │
│                                                                  │
│  Room                                                         │
│  ├── building (FK), floor (FK)                             │
│  ├── room_number, name, room_type                          │
│  ├── location (GIS Point)                                  │
│  ├── capacity, office_number                               │
│  └── accessibility_features                                │
│                                                                  │
│  ServicePoint                                               │
│  ├── name, service_type (expanded types)                   │
│  ├── building (FK), room (FK), floor (FK)                 │
│  ├── location (GIS Point)                                  │
│  ├── contact_phone, office_hours                           │
│  └── accessibility_features                                │
│                                                                  │
│  Pathway                                                      │
│  ├── pathway_type (outdoor/indoor/elevator/etc)           │
│  ├── start_point (FK ServicePoint)                         │
│  ├── end_point (FK ServicePoint)                           │
│  ├── route_geometry (GIS LineString)                       │
│  ├── distance_meters, estimated_time_minutes              │
│  ├── is_accessible                                        │
│  └── floor_from, floor_to (for multi-floor)              │
│                                                                  │
│  Route (Cached routes)                                      │
│  ├── start_point (FK), end_point (FK)                     │
│  ├── route_geometry (GIS LineString)                       │
│  ├── distance_meters, estimated_time_minutes              │
│  ├── is_accessible, route_type                            │
│  └── created_at, updated_at                               │
│                                                                  │
│  ServiceArea                                                  │
│  ├── service_point (1:1 FK)                               │
│  ├── coverage_area (GIS Polygon)                           │
│  └── buffer_radius_meters                                  │
│                                                                  │
└─────────────────┬──────────────────────────────────────────────┘
                  │
                  │ Spatial Queries
                  │ (Distance, Intersection, Proximity)
                  │
┌─────────────────▼──────────────────────────────────────────────┐
│              DATABASE LAYER (Spatial Database)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Development:                 Production:                      │
│  ┌──────────────────┐        ┌──────────────────────┐          │
│  │ SQLite           │        │ PostgreSQL 12+       │          │
│  │ + SpatiaLite     │        │ + PostGIS Extension  │          │
│  │ (Embedded)       │        │ (Server-based)       │          │
│  │ db.sqlite3       │        │ cut_guide_db         │          │
│  └──────────────────┘        └──────────────────────┘          │
│                                                                  │
│  Tables:                                                        │
│  ├── Navigator_building       (with GIS indexes)              │
│  ├── Navigator_floor                                          │
│  ├── Navigator_room           (with spatial index)            │
│  ├── Navigator_servicepoint   (with spatial index)            │
│  ├── Navigator_pathway        (with route geometry)           │
│  ├── Navigator_route          (cached routes)                 │
│  └── Navigator_servicearea    (polygon coverage)              │
│                                                                  │
│  Spatial Indexes:                                             │
│  └── All Point/Polygon fields indexed for fast queries       │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
User Request
    │
    ├─→ [URL Router] ──→ Determines View
    │
    ├─→ [View Function]
    │
    ├─→ [ORM Query]
    │
    ├─→ [Routing Engine] (if navigation needed)
    │   ├─→ PathFinder.build_graph()
    │   ├─→ Dijkstra's Algorithm
    │   └─→ Returns path/distance/time
    │
    ├─→ [Database Query]
    │   └─→ Spatial operations if needed
    │
    ├─→ [Template Rendering]
    │   ├─→ With Leaflet.js map
    │   └─→ With Bootstrap responsive design
    │
    └─→ HTML/JSON Response ──→ Client Browser/App
```

---

## Component Interaction Matrix

```
                 Views  Models  Routing  Templates  Admin
URLs             ✓      -       -        -          -
Views            -      ✓       ✓        ✓          -
Models           -      -       ✓        ✓          ✓
Routing Engine   -      ✓       -        -          -
Templates        -      ✓       -        -          -
Admin            -      ✓       -        -          -
API Endpoints    -      ✓       ✓        -          -
Database         -      ✓       ✓        -          ✓

Legend: ✓ = Direct Interaction
```

---

## Request Flow: Getting Directions

```
1. User visits: /directions/1/5/?accessibility=true

2. URL Router matches route
   └─→ directions(request, start_id=1, end_id=5)

3. View Function
   ├─→ Get ServicePoint(id=1) - start
   ├─→ Get ServicePoint(id=5) - end
   ├─→ Call PathFinder.find_shortest_path(1, 5, accessibility=True)
   │
   └─→ PathFinder Processing
       ├─→ Build graph from Pathways
       ├─→ Filter for accessible=True
       ├─→ Apply Dijkstra's algorithm
       ├─→ Get route from cache or calculate
       ├─→ Get/create Route record
       └─→ Return {distance, time, steps, pathways}

4. Context Created
   ├─→ start_service
   ├─→ end_service
   ├─→ route
   ├─→ steps (turn-by-turn)
   └─→ total_distance, total_time

5. Template Rendered
   ├─→ base.html (layout + Leaflet setup)
   ├─→ directions.html (content)
   ├─→ Leaflet.js draws map
   ├─→ Markers placed (start/end)
   ├─→ Path line drawn
   └─→ Directions displayed

6. HTML Response sent to browser
```

---

## API Request Flow: Find Nearest Service

```
1. Client sends: /api/nearest-service/?lat=-17.2833&lon=30.2167&type=library

2. View Function: api_find_nearest_service(request)
   ├─→ Extract parameters (lat, lon, type, radius, accessibility)
   ├─→ Validate parameters
   ├─→ Create Point(lon, lat, srid=4326)
   │
   └─→ PathFinder Processing
       ├─→ Query all services
       ├─→ Annotate with Distance() function
       ├─→ Filter by radius
       ├─→ Apply type filter if provided
       ├─→ Apply accessibility filter if requested
       ├─→ Order by distance
       ├─→ Get first result
       └─→ Return service details

3. Response formatted as JSON
   {
     "id": 1,
     "name": "Main Library",
     "type": "Library",
     "latitude": -17.2833,
     "longitude": 30.2167,
     "description": "...",
     "contact": "+263...",
     "office_hours": "9AM-5PM"
   }

4. JSON sent to client (mobile app, etc)
```

---

## Database Schema (Simplified)

```
Building (1) ──→ (M) Floor
    ↓
    └──→ (M) Room ──→ (M) ServicePoint
             ↓
         (1) Floor


ServicePoint (connections):
    ├─→ (1) Building
    ├─→ (1) Room
    ├─→ (1) Floor
    └─→ (1) ServiceArea


Pathway (navigation):
    ├─→ (1) start_point (ServicePoint)
    ├─→ (1) end_point (ServicePoint)
    ├─→ (1) floor_from (Floor)
    └─→ (1) floor_to (Floor)


Route (cached):
    ├─→ (1) start_point (ServicePoint)
    ├─→ (1) end_point (ServicePoint)
    └─→ Many related Pathways


Spatial Fields:
    ├── Building: location (Point), outline (Polygon)
    ├── Room: location (Point)
    ├── ServicePoint: location (Point)
    ├── Pathway: route_geometry (LineString)
    ├── Route: route_geometry (LineString)
    └── ServiceArea: coverage_area (Polygon)
```

---

## Technology Stack Visualization

```
┌──────────────────────────────────────────────────────┐
│                   Presentation Layer                  │
│  ┌────────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ Bootstrap5 │  │ Leaflet  │  │   JavaScript    │  │
│  │   CSS      │  │   Maps   │  │   (ES6+)        │  │
│  └────────────┘  └──────────┘  └─────────────────┘  │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│              Application Layer (Django)              │
│  ┌──────────────────────────────────────────────┐   │
│  │ Python 3.8+ | Django 5.2.8 | GeoDjango     │   │
│  └──────────────────────────────────────────────┘   │
│  ┌────────────┐  ┌───────────┐  ┌──────────────┐   │
│  │   Views    │  │  Models   │  │   Routing    │   │
│  │  (12+)     │  │   (8)     │  │  (Dijkstra)  │   │
│  └────────────┘  └───────────┘  └──────────────┘   │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│           Data & Business Logic Layer                │
│  ┌──────────────────────────────────────────────┐   │
│  │ ORM | GIS Queries | Spatial Operations      │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────┐
│            Database Layer (Spatial)                  │
│  ┌────────────────┐        ┌──────────────────┐    │
│  │ SpatiaLite     │   OR   │ PostgreSQL +     │    │
│  │ (Development)  │        │ PostGIS (Prod)   │    │
│  └────────────────┘        └──────────────────┘    │
└──────────────────────────────────────────────────────┘
```

---

## Traffic Flow During Peak Usage

```
     100 Requests/minute
            │
            ├─→ 30% Search queries ──→ Full-text search
            ├─→ 40% Map views ───────→ Building/Service details
            ├─→ 20% Directions ──────→ Routing engine (cached)
            └─→ 10% API calls ──────→ JSON responses

Processing per request:
  Search: ~50ms (database query)
  Map View: ~30ms (ORM + template)
  Directions: ~5ms (cached) or ~200ms (calculated)
  API: ~10ms (lightweight)
```

---

## Scalability Architecture

```
Current (Single Server):
  Django App
      ↓
  SQLite/SpatiaLite (single connection)

Future (Multi-server):
  Load Balancer
      ↓
  ┌───────┬───────┬───────┐
  ↓       ↓       ↓       ↓
Django  Django  Django  Django
Cache (Redis)
      ↓
  PostgreSQL + PostGIS (replicated)
      ↓
  ┌───────────┐  ┌────────────┐
  │ Read Only │  │ Read/Write │
  │ Replicas  │  │   Master   │
  └───────────┘  └────────────┘
```

---

## Security Layers

```
┌─────────────────────────────────────────┐
│          Security Measures               │
├─────────────────────────────────────────┤
│ 1. CSRF Protection (Django middleware)  │
│ 2. XSS Prevention (Template escaping)   │
│ 3. SQL Injection Prevention (ORM)       │
│ 4. Authentication (session-based)       │
│ 5. HTTPS (production requirement)       │
│ 6. CORS (for API access control)        │
│ 7. Rate Limiting (future enhancement)   │
│ 8. Data Validation (form/API level)     │
└─────────────────────────────────────────┘
```

---

## Performance Optimization Points

```
Frontend Optimization:
  ├─→ Lazy load maps
  ├─→ Minify CSS/JS
  ├─→ Browser caching
  └─→ CDN for static files

Backend Optimization:
  ├─→ Database indexes (spatial)
  ├─→ Route caching
  ├─→ Query optimization
  ├─→ Connection pooling
  └─→ Cache framework (Redis)

Database Optimization:
  ├─→ Spatial indexes (GIST/BRIN)
  ├─→ Denormalization for reads
  ├─→ Partition large tables
  └─→ Regular VACUUM/ANALYZE
```

---

**Architecture Documentation**  
*Last Updated: January 19, 2026*
