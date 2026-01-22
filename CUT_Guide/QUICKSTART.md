# ⚡ Quick Start Guide - CUT-Guide MVP

**Get up and running in 5 minutes!**

---

## 📋 Prerequisites

```bash
✓ Python 3.8+
✓ pip (Python package manager)
✓ Git (optional)
```

---

## 🚀 Installation

### Step 1: Install Dependencies

```bash
pip install django==5.2.8
pip install django-extensions
pip install pillow
```

For GIS support (required):
```bash
# Ubuntu/Debian
sudo apt-get install gdal-bin libgdal-dev spatialite-bin

# macOS (Homebrew)
brew install gdal spatialite

# Windows - Use OSGeo4W installer
# Download: https://trac.osgeo.org/osgeo4w/
```

Then install Python GIS packages:
```bash
pip install gdal
pip install spatialite
```

### Step 2: Setup Database

```bash
cd CUT_Guide
python manage.py migrate
```

### Step 3: Create Admin User

```bash
python manage.py createsuperuser
# Follow prompts to create username/password
```

### Step 4: Start Server

```bash
python manage.py runserver
```

**Visit:** http://localhost:8000

---

## 🎯 First Steps

### 1. Access Admin Panel
- **URL**: http://localhost:8000/admin/
- **Login**: Use credentials from Step 3

### 2. Add Sample Data

#### Add Buildings
```
1. Go to Navigator → Buildings → Add Building
2. Fill in:
   - Name: "Administrative Block"
   - Code: "ADM"
   - Description: "Main administration building"
   - Latitude: -17.2833
   - Longitude: 30.2167
   - Total Floors: 4
3. Click Save
```

#### Add Rooms
```
1. Go to Navigator → Rooms → Add Room
2. Select Building and Floor
3. Enter Room Number (e.g., "A101")
4. Set coordinates
5. Save
```

#### Add Services
```
1. Go to Navigator → Service Points → Add Service Point
2. Fill in details:
   - Name: "Main Library"
   - Service Type: "Library"
   - Building and Location
   - Contact Phone
3. Save
```

### 3. View Your Campus

- **Homepage**: http://localhost:8000/
- **Buildings**: http://localhost:8000/
- **Services**: http://localhost:8000/services/
- **Search**: Use search bar (top right)

---

## 🗺️ Adding Pathways (For Navigation)

```
1. Go to Navigator → Pathways → Add Pathway
2. Select:
   - Start Point (Service Point)
   - End Point (Service Point)
   - Pathway Type (indoor_corridor, outdoor, etc.)
3. Enter:
   - Distance (meters)
   - Estimated Time (minutes)
   - Is Accessible (checkbox)
4. Draw route geometry (or leave blank for simple path)
5. Save
```

---

## 🧪 Test Features

### Test Search
1. Go to http://localhost:8000/search/?q=library
2. Should show matching results

### Test Directions
1. Add at least 2 service points
2. Go to http://localhost:8000/directions/1/2/
3. Should show route and directions

### Test API
```bash
# Find nearest service
curl "http://localhost:8000/api/nearest-service/?lat=-17.2833&lon=30.2167"

# Get nearby services
curl "http://localhost:8000/api/nearby-services/?lat=-17.2833&lon=30.2167&limit=5"
```

---

## 📁 Project Structure

```
CUT_Guide/
├── db.sqlite3              # Database (auto-created)
├── manage.py               # Django management
├── Navigator/              # App folder
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin setup
│   ├── routing.py         # Navigation engine
│   └── migrations/        # Database migrations
├── templates/             # HTML templates
│   ├── base.html          # Base layout
│   ├── home.html          # Homepage
│   └── ... (other templates)
├── static/                # CSS, JS, images
├── CUT_Guide/             # Project settings
│   ├── settings.py        # Django configuration
│   ├── urls.py            # Main URL config
│   └── ...
└── README_MVP.md          # Documentation
```

---

## 🔧 Common Tasks

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Create Backup
```bash
cp db.sqlite3 db.sqlite3.backup
```

### View Logs
```bash
# Django debug mode (already on in development)
# Check console output or set DEBUG = True in settings.py
```

### Add More Data
```bash
# Via admin panel (recommended)
# OR create management command for bulk import
# See SETUP_GUIDE.md for script examples
```

---

## 🌐 URLs Reference

| URL | Purpose |
|-----|---------|
| `/` | Homepage with map |
| `/building/1/` | View building |
| `/building/1/floor/2/` | View floor |
| `/building/1/room/5/` | View room |
| `/service/1/` | View service detail |
| `/services/` | Service directory |
| `/search/?q=query` | Search results |
| `/directions/1/5/` | Get directions |
| `/admin/` | Admin panel |
| `/api/nearest-service/` | API endpoint |
| `/api/nearby-services/` | API endpoint |

---

## 🎨 Customizing

### Change Colors
Edit `templates/base.html` CSS section

### Change Map Provider
Edit `templates/base.html` - change OpenStreetMap URL

### Add Your Campus Logo
Add logo image to `static/images/`
Update `templates/base.html` navbar

---

## ⚠️ Troubleshooting

### Error: "No module named 'django'"
```bash
pip install django==5.2.8
```

### Error: "django.contrib.gis" not found
```bash
pip install django[gis]
# OR
pip install gdal
```

### Error: "SpatiaLite not found"
```bash
# Install spatial database
pip install spatialite
```

### Database locked error
```bash
# Close other connections and restart
rm db.sqlite3
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

---

## 📚 Full Documentation

For detailed information:
- `README_MVP.md` - Architecture overview
- `SETUP_GUIDE.md` - Detailed setup
- `API_REFERENCE.md` - API documentation
- `ARCHITECTURE.md` - System design
- `COMPLETION_SUMMARY.md` - What's included

---

## 🚀 Deploy to Production

### Before Deploying:

1. **Update settings.py**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'generate-new-secure-key'
   ```

2. **Use PostgreSQL + PostGIS**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.contrib.gis.db.backends.postgis',
           'NAME': 'cut_guide_db',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'your_host',
           'PORT': '5432',
       }
   }
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Use production web server** (Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn CUT_Guide.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Setup reverse proxy** (Nginx)
   - Serve static files
   - Proxy requests to Gunicorn
   - Enable HTTPS

---

## 💡 Tips & Tricks

**Use Django shell for testing:**
```bash
python manage.py shell
>>> from Navigator.models import Building
>>> Building.objects.all()
>>> # Query and test here
```

**Check queries being executed:**
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Run tests:**
```bash
python manage.py test Navigator
```

---

## 📱 Mobile Testing

### Test on Mobile Device

1. Find your computer's IP:
   ```bash
   # Linux/Mac
   ifconfig | grep inet
   
   # Windows
   ipconfig
   ```

2. Start server on 0.0.0.0:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. Access from phone:
   ```
   http://YOUR_IP:8000
   ```

---

## 🆘 Getting Help

1. **Check documentation files**
2. **Review inline code comments**
3. **Check Django error messages** (helpful!)
4. **Enable DEBUG mode** for detailed errors
5. **Check browser console** for JS errors

---

## ✅ Success Checklist

- ✓ Database created and migrations applied
- ✓ Admin user created
- ✓ Server running without errors
- ✓ Can access homepage
- ✓ Can access admin panel
- ✓ Added sample buildings
- ✓ Added sample services
- ✓ Search functionality works
- ✓ Maps display correctly
- ✓ Ready to add your campus data!

---

## 🎉 Next Steps

1. **Gather Your Campus Data**
   - Building locations
   - Floor plans
   - Room information
   - Service point details

2. **Start Populating Data**
   - Use admin panel
   - Or create import script

3. **Test Extensively**
   - Test search
   - Test navigation
   - Test on mobile

4. **Deploy**
   - Follow production setup
   - Configure domain
   - Enable HTTPS
   - Setup backups

---

**Happy Navigating! 🗺️**

**Support**: Check documentation files or review code comments

*Last Updated: January 19, 2026*
