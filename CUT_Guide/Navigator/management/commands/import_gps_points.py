import json
from django.core.management.base import BaseCommand
from Navigator.models import ServicePoint, Building


class Command(BaseCommand):
    help = 'Import GPS points from JSON file into ServicePoints'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Loaded {len(data)} points from {json_file}'))
            
            created_count = 0
            skipped_count = 0
            
            # Get or create a default building for campus locations
            building, _ = Building.objects.get_or_create(
                code='CUT',
                defaults={
                    'name': 'CUT Campus',
                    'description': 'Chinhoyi University of Technology',
                    'latitude': -17.28332,
                    'longitude': 30.21668,
                    'total_floors': 1
                }
            )
            
            for item in data:
                try:
                    location_id = item.get('ID', '').strip()
                    latitude = item.get('Latitude')
                    longitude = item.get('Longitude')
                    
                    # Skip if missing critical data
                    if not location_id or latitude is None or longitude is None:
                        skipped_count += 1
                        continue
                    
                    # Determine service type from location name
                    location_name = location_id.lower()
                    service_type = 'other'
                    
                    if 'toilet' in location_name or 'wc' in location_name:
                        service_type = 'toilet'
                    elif 'admin' in location_name or 'registry' in location_name or 'regestry' in location_name:
                        service_type = 'admin_office'
                    elif 'library' in location_name or 'lybrary' in location_name:
                        service_type = 'library'
                    elif 'clinic' in location_name or 'medical' in location_name:
                        service_type = 'medical'
                    elif 'dining' in location_name or 'cafe' in location_name or 'canteen' in location_name:
                        service_type = 'canteen'
                    elif 'lab' in location_name or 'laboratory' in location_name or 'stem' in location_name:
                        service_type = 'lab'
                    elif 'bank' in location_name or 'zb' in location_name:
                        service_type = 'admin_office'
                    elif 'hostel' in location_name:
                        service_type = 'admin_office'
                    elif 'block' in location_name or 'room' in location_name:
                        service_type = 'office'
                    
                    # Create or update the ServicePoint
                    service, created = ServicePoint.objects.update_or_create(
                        name=location_id,
                        defaults={
                            'service_type': service_type,
                            'description': f'GPS Point: {location_id}',
                            'building': building,
                            'latitude': latitude,
                            'longitude': longitude,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {location_id} ({service_type})')
                    
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f'  ⚠ Skipped: {location_id} - {str(e)}'[:100]))
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Import completed!'))
            self.stdout.write(f'  Created: {created_count}')
            self.stdout.write(f'  Skipped: {skipped_count}')
            self.stdout.write(self.style.SUCCESS(f'  Total: {created_count + skipped_count}'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'✗ File not found: {json_file}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'✗ Invalid JSON file: {json_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
