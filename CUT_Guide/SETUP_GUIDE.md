# 🔄 CUT-Guide Migration & Setup Guide

## Pre-Migration Checklist

Before updating to the MVP version, ensure you have:

- ✅ Python 3.8 or higher
- ✅ Django 5.2.8
- ✅ Django GIS dependencies installed
- ✅ Database backup (recommended)

---

## Installation Steps

### 1. Install Required Packages

```bash
# Core Django GIS
pip install django==5.2.8
pip install django-extensions

# Spatial database drivers
pip install gdal  # or follow OS-specific instructions
pip install spatialite  # for development

# Image handling (for floorplans)
pip install pillow

# Optional: for PostGIS (production)
pip install psycopg2-binary
```

### 2. Update Django Settings

The settings.py has been updated to:
- Add `django.contrib.gis` to INSTALLED_APPS
- Configure SpatiaLite for development
- Configure PostGIS for production (commented out)

**For Production Setup:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cut_guide_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Create New Migrations

Since the models have been significantly updated:

```bash
# Backup current database (if you want to keep data)
cp db.sqlite3 db.sqlite3.backup

# Create fresh migration for all models
python manage.py makemigrations

# Review the migration file in Navigator/migrations/
# It will show all new spatial fields
```

### 4. Apply Migrations

```bash
# Apply the new migration
python manage.py migrate

# Verify migration was successful
python manage.py showmigrations Navigator
```

### 5. Create Admin Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 6. Test the Application

```bash
# Run development server
python manage.py runserver

# Visit:
# - http://localhost:8000/ - Homepage
# - http://localhost:8000/admin/ - Admin panel
# - http://localhost:8000/services/ - Services directory
```

---

## Data Migration (from Old Schema)

If you have existing data in the old schema:

### Option A: Manual Data Migration Script

Create a script to transfer data:

```python
# Navigator/management/commands/migrate_old_data.py

from django.core.management.base import BaseCommand
from Navigator.models import Building, Room, ServicePoint
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Migrate data from old schema to new GIS-enabled schema'

    def handle(self, *args, **options):
        # Buildings already have needed fields, just add new ones if missing
        for building in Building.objects.all():
            if not building.location:
                building.location = Point(
                    building.longitude,
                    building.latitude,
                    srid=4326
                )
                building.save()
                self.stdout.write(f'Updated {building.name}')

        # Similar for Rooms and ServicePoints
        for room in Room.objects.all():
            if not room.location:
                room.location = Point(
                    room.longitude,
                    room.latitude,
                    srid=4326
                )
                room.save()

        for service in ServicePoint.objects.all():
            if not service.location:
                service.location = Point(
                    service.longitude,
                    service.latitude,
                    srid=4326
                )
                service.save()

        self.stdout.write('Migration complete!')
```

Run it:
```bash
python manage.py migrate_old_data
```

### Option B: Fresh Start

If starting from scratch is acceptable:

```bash
# Delete old database
rm db.sqlite3

# Create new one
python manage.py migrate

# Add data via admin panel or import script
```

---

## Data Import Scripts

### Adding Buildings via Script

```python
# Navigator/management/commands/add_sample_buildings.py

from django.core.management.base import BaseCommand
from Navigator.models import Building
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Add sample buildings to database'

    def handle(self, *args, **options):
        buildings_data = [
            {
                'name': 'Administrative Block',
                'code': 'ADM',
                'description': 'Main administrative offices',
                'latitude': -17.2833,
                'longitude': 30.2167,
                'total_floors': 4,
                'accessibility_features': 'Wheelchair accessible, Elevator'
            },
            {
                'name': 'Science Building',
                'code': 'SCI',
                'description': 'Science and engineering laboratories',
                'latitude': -17.2835,
                'longitude': 30.2170,
                'total_floors': 3,
                'accessibility_features': 'Wheelchair accessible, Ramp'
            },
            # Add more buildings...
        ]

        for data in buildings_data:
            building, created = Building.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'total_floors': data['total_floors'],
                    'accessibility_features': data['accessibility_features'],
                    'location': Point(
                        data['longitude'],
                        data['latitude'],
                        srid=4326
                    )
                }
            )
            
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'{status}: {building.name}')
```

Run it:
```bash
python manage.py add_sample_buildings
```

---

## PostGIS Setup (Production)

### For PostgreSQL + PostGIS:

#### Ubuntu/Debian:
```bash
# Install PostgreSQL and PostGIS
sudo apt-get install postgresql postgresql-contrib postgis

# Create database and enable PostGIS
sudo -u postgres createdb cut_guide_db
sudo -u postgres psql -d cut_guide_db -c "CREATE EXTENSION postgis;"

# Create Django user
sudo -u postgres createuser djangouser
sudo -u postgres psql -c "ALTER USER djangouser WITH PASSWORD 'password';"
sudo -u postgres psql -c "ALTER USER djangouser CREATEDB;"
```

#### macOS:
```bash
# Using Homebrew
brew install postgresql postgis

# Initialize and create database
initdb /usr/local/var/postgres
createdb cut_guide_db
psql -d cut_guide_db -c "CREATE EXTENSION postgis;"
```

#### Windows:
- Download PostgreSQL installer with PostGIS from https://www.postgresql.org/download/windows/
- Run installer and enable PostGIS during installation
- Create database: `createdb cut_guide_db`
- Enable PostGIS: `psql -d cut_guide_db -c "CREATE EXTENSION postgis;"`

### Update Django Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cut_guide_db',
        'USER': 'djangouser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Common Issues & Solutions

### Issue: "django.contrib.gis" not found
**Solution:**
```bash
pip install django[gis]
# or install GDAL separately
```

### Issue: SpatiaLite library not found
**Solution (Ubuntu):**
```bash
sudo apt-get install libspatialite-dev
pip install spatialite
```

### Issue: Geometry field validation errors
**Solution:**
Ensure all spatial fields have `srid=4326` and use `Point()` for creation:
```python
from django.contrib.gis.geos import Point
location = Point(longitude, latitude, srid=4326)
```

### Issue: Migration conflicts
**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Squash migrations if too many
python manage.py squashmigrations Navigator 0001 0010
```

---

## Testing the Setup

### Run Tests
```bash
python manage.py test Navigator
```

### Check GIS Support
```python
python manage.py shell
>>> from django.contrib.gis.geos import Point
>>> p = Point(-17.2833, 30.2167, srid=4326)
>>> print(p)
POINT (-17.2833 30.2167)
```

### Verify Admin
1. Start server: `python manage.py runserver`
2. Go to http://localhost:8000/admin/
3. Login with superuser
4. Verify all new models appear in admin panel

---

## Deployment Checklist

Before deploying to production:

- ✅ Update `settings.py` for production (DEBUG=False, ALLOWED_HOSTS, etc.)
- ✅ Configure PostgreSQL + PostGIS
- ✅ Run `python manage.py collectstatic`
- ✅ Set up HTTPS/SSL
- ✅ Configure CORS if serving API to separate frontend
- ✅ Set up database backups
- ✅ Configure email backend for notifications
- ✅ Set up logging
- ✅ Use production web server (Gunicorn, uWSGI)
- ✅ Set up reverse proxy (Nginx)

---

## Backup & Recovery

### Backup Database
```bash
# SpatiaLite
python manage.py dumpdata > backup.json

# PostgreSQL
pg_dump cut_guide_db > backup.sql
```

### Restore Database
```bash
# SpatiaLite
python manage.py loaddata backup.json

# PostgreSQL
psql cut_guide_db < backup.sql
```

---

## Next Steps

1. **Data Entry**: Add buildings, floors, rooms, and services via admin panel
2. **Map Setup**: Define outdoor pathways using coordinates
3. **Floorplans**: Upload floorplan images for buildings
4. **Testing**: Test routing and navigation features
5. **Deployment**: Deploy to production server

---

## Support & Documentation

- Django GIS Docs: https://docs.djangoproject.com/en/stable/ref/contrib/gis/
- Leaflet.js Docs: https://leafletjs.com/
- PostGIS Docs: https://postgis.net/docs/

---

**Last Updated:** January 19, 2026
