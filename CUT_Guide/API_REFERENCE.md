# 📡 CUT-Guide API Reference & Examples

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

---

## Authentication

Currently, the API uses Django's session-based authentication. For mobile apps, consider implementing token-based authentication (JWT).

---

## API Endpoints

### 🏠 Homepage & Dashboard

**GET //**
Returns the main campus overview page with map and statistics.

```html
URL: http://localhost:8000/
Method: GET
Response: HTML page with dashboard
```

---

### 🏢 Buildings

#### Get All Buildings
```
URL: /
Method: GET
Response: Homepage with building list
```

#### Get Building Details
```
URL: /building/<int:building_id>/
Method: GET
Parameters:
  - building_id (required): Integer ID of the building

Response: HTML page with:
  - Building info
  - Floors list
  - Rooms in building
  - Services in building
  - Map view
```

Example:
```
http://localhost:8000/building/1/
```

---

### 📊 Floors

#### Get Floor Details
```
URL: /building/<int:building_id>/floor/<int:floor_id>/
Method: GET
Parameters:
  - building_id (required): ID of the building
  - floor_id (required): ID of the floor

Response: HTML page with:
  - Floorplan image (if available)
  - Rooms on the floor
  - Services on the floor
```

Example:
```
http://localhost:8000/building/1/floor/2/
```

---

### 🚪 Rooms

#### Get Room Details
```
URL: /building/<int:building_id>/room/<int:room_id>/
Method: GET
Parameters:
  - building_id (required): ID of the building
  - room_id (required): ID of the room

Response: HTML page with:
  - Room information
  - Capacity and type
  - Location map
  - Services in the room
```

Example:
```
http://localhost:8000/building/1/room/5/
```

---

### 🧭 Services

#### Get All Services
```
URL: /services/
Method: GET
Query Parameters (optional):
  - type: Filter by service type (library, admin_office, etc.)
  - accessibility: true/false - Filter by accessibility

Response: HTML page with:
  - Map of all services
  - Filtered service list
  - Filter controls
```

Examples:
```
http://localhost:8000/services/
http://localhost:8000/services/?type=library
http://localhost:8000/services/?accessibility=true
http://localhost:8000/services/?type=admin_office&accessibility=true
```

#### Get Service Details
```
URL: /service/<int:service_id>/
Method: GET
Parameters:
  - service_id (required): ID of the service point

Response: HTML page with:
  - Service information
  - Contact details
  - Accessibility info
  - Location map
  - Nearby services
```

Example:
```
http://localhost:8000/service/1/
```

---

### 🗺️ Navigation & Directions

#### Get Directions
```
URL: /directions/<int:start_id>/<int:end_id>/
Method: GET
Parameters:
  - start_id (required): Service point ID (start location)
  - end_id (required): Service point ID (destination)

Query Parameters (optional):
  - accessibility: true/false - Request accessible route

Response: HTML page with:
  - Map showing route
  - Turn-by-turn directions
  - Total distance and time
  - Step-by-step instructions
```

Examples:
```
http://localhost:8000/directions/1/5/
http://localhost:8000/directions/1/5/?accessibility=true
```

---

### 🔍 Search

#### Search Campus
```
URL: /search/
Method: GET
Query Parameters:
  - q (required): Search query string

Response: HTML page with:
  - Buildings matching query
  - Rooms matching query
  - Services matching query
  - Clickable results with links
```

Examples:
```
http://localhost:8000/search/?q=library
http://localhost:8000/search/?q=lab
http://localhost:8000/search/?q=room101
```

---

## 📡 JSON API Endpoints

### Find Nearest Service

```
URL: /api/nearest-service/
Method: GET
Parameters:
  - lat (required): User latitude
  - lon (required): User longitude
  - type (optional): Service type filter
  - radius (optional): Search radius in meters (default: 200)
  - accessibility (optional): true/false

Response: JSON
{
  "id": 1,
  "name": "Main Library",
  "type": "Library",
  "latitude": -17.2833,
  "longitude": 30.2167,
  "description": "Campus library with...",
  "contact": "+263 772 123456",
  "office_hours": "9AM-5PM Mon-Fri"
}
```

Examples:
```bash
# Find nearest library
curl "http://localhost:8000/api/nearest-service/?lat=-17.2833&lon=30.2167&type=library"

# Find nearest service (any type) within 500m
curl "http://localhost:8000/api/nearest-service/?lat=-17.2833&lon=30.2167&radius=500"

# Find nearest accessible facility
curl "http://localhost:8000/api/nearest-service/?lat=-17.2833&lon=30.2167&accessibility=true"
```

---

### Find Nearby Services

```
URL: /api/nearby-services/
Method: GET
Parameters:
  - lat (required): User latitude
  - lon (required): User longitude
  - type (optional): Service type filter
  - radius (optional): Search radius in meters (default: 500)
  - limit (optional): Max results (default: 5)
  - accessibility (optional): true/false

Response: JSON
{
  "services": [
    {
      "id": 1,
      "name": "Main Library",
      "type": "Library",
      "latitude": -17.2833,
      "longitude": 30.2167
    },
    {
      "id": 2,
      "name": "IT Support",
      "type": "Office",
      "latitude": -17.2835,
      "longitude": 30.2170
    }
  ]
}
```

Examples:
```bash
# Find 5 nearest services
curl "http://localhost:8000/api/nearby-services/?lat=-17.2833&lon=30.2167&limit=5"

# Find 10 libraries within 1000m
curl "http://localhost:8000/api/nearby-services/?lat=-17.2833&lon=30.2167&type=library&radius=1000&limit=10"

# Find accessible services
curl "http://localhost:8000/api/nearby-services/?lat=-17.2833&lon=30.2167&accessibility=true&limit=5"
```

---

### Get Route Geometry

```
URL: /api/route-geometry/<int:start_id>/<int:end_id>/
Method: GET
Parameters:
  - start_id (required): Start service point ID
  - end_id (required): End service point ID

Response: JSON
{
  "coordinates": [
    [-17.2833, 30.2167],
    [-17.2834, 30.2168],
    [-17.2835, 30.2170]
  ],
  "distance": 250.5,
  "time": 3.5
}
```

Examples:
```bash
# Get route from building 1 to building 5
curl "http://localhost:8000/api/route-geometry/1/5/"
```

---

## 📊 Service Types

Available service type codes:
- `library` - Library
- `admin_office` - Administration Office
- `water_point` - Water Point
- `toilet` - Toilet/Restroom
- `canteen` - Canteen/Cafeteria
- `lab` - Laboratory
- `classroom` - Classroom
- `office` - Office
- `parking` - Parking
- `medical` - Medical/Health Center
- `security` - Security Post
- `lost_and_found` - Lost & Found
- `other` - Other

---

## 🔧 Room Types

Available room type codes:
- `office` - Office
- `classroom` - Classroom
- `lab` - Laboratory
- `lecture_hall` - Lecture Hall
- `meeting_room` - Meeting Room
- `storage` - Storage
- `other` - Other

---

## 🚶 Pathway Types

Available pathway type codes:
- `outdoor` - Outdoor Path
- `indoor_corridor` - Indoor Corridor
- `staircase` - Staircase
- `ramp` - Ramp/Slope
- `elevator` - Elevator
- `escalator` - Escalator

---

## 📱 Mobile Integration Examples

### JavaScript/Fetch API

```javascript
// Find nearest library
async function findNearestLibrary(lat, lon) {
  const url = `/api/nearest-service/?lat=${lat}&lon=${lon}&type=library`;
  const response = await fetch(url);
  return await response.json();
}

// Get nearby services
async function getNearbyServices(lat, lon, limit = 5) {
  const url = `/api/nearby-services/?lat=${lat}&lon=${lon}&limit=${limit}`;
  const response = await fetch(url);
  return await response.json();
}

// Get route geometry for map display
async function getRouteGeometry(startId, endId) {
  const url = `/api/route-geometry/${startId}/${endId}/`;
  const response = await fetch(url);
  return await response.json();
}
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function ServiceFinder() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get user location
    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      setLoading(true);
      
      // Fetch nearby services
      const response = await fetch(
        `/api/nearby-services/?lat=${latitude}&lon=${longitude}&limit=5`
      );
      const data = await response.json();
      setServices(data.services);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Nearby Services</h2>
      <ul>
        {services.map(service => (
          <li key={service.id}>
            <a href={`/service/${service.id}/`}>
              {service.name} - {service.type}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Python (Requests)

```python
import requests

BASE_URL = "http://localhost:8000"

def find_nearest_service(lat, lon, service_type=None, radius=200):
    """Find nearest service point"""
    params = {
        'lat': lat,
        'lon': lon,
        'radius': radius
    }
    if service_type:
        params['type'] = service_type
    
    response = requests.get(f"{BASE_URL}/api/nearest-service/", params=params)
    return response.json()

def get_nearby_services(lat, lon, limit=5):
    """Get nearby services"""
    params = {
        'lat': lat,
        'lon': lon,
        'limit': limit
    }
    response = requests.get(f"{BASE_URL}/api/nearby-services/", params=params)
    return response.json()

# Usage
nearest = find_nearest_service(-17.2833, 30.2167, service_type='library')
print(nearest)

nearby = get_nearby_services(-17.2833, 30.2167, limit=10)
print(nearby)
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid parameters"
}
```

### 404 Not Found
```json
{
  "error": "No services found"
}
```

### 500 Server Error
```json
{
  "error": "Server error occurred"
}
```

---

## 🔗 Response Formats

### Coordinates Format
All coordinates are in **[latitude, longitude]** format (WGS 84, SRID 4326).

Example:
```
Chinhoyi: [-17.2833, 30.2167]
```

### Distance Unit
- **distance_meters**: Distance in meters
- **estimated_time_minutes**: Time in minutes (walking speed: ~1.4 m/s)

---

## 📈 Rate Limiting

Currently, there is no rate limiting. Consider implementing for production:
- Max 100 requests/minute per IP
- Max 1000 requests/hour per IP

---

## 🔐 CORS Configuration

To enable CORS for mobile/web clients:

```python
# settings.py
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

---

## 📝 Testing the API

### Using cURL

```bash
# Test nearest service
curl -v "http://localhost:8000/api/nearest-service/?lat=-17.2833&lon=30.2167"

# Test nearby services
curl -v "http://localhost:8000/api/nearby-services/?lat=-17.2833&lon=30.2167&limit=5"

# Test route geometry
curl -v "http://localhost:8000/api/route-geometry/1/5/"
```

### Using Postman

1. Import collection: Create new requests for each endpoint
2. Set method to GET
3. Add query parameters
4. Send request
5. View response

---

## 🚀 Future Enhancements

Planned API additions:
- POST endpoints for mobile app feedback
- Real-time traffic/crowding data
- Indoor positioning via Bluetooth beacons
- Turn-by-turn voice navigation
- Accessibility preference filtering

---

**Last Updated:** January 19, 2026
