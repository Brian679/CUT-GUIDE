"""
Campus navigation routing module using Dijkstra's algorithm.
Supports both indoor and outdoor navigation.
"""

import heapq
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import ServicePoint, Pathway, Route


class PathFinder:
    """
    Implements Dijkstra's shortest path algorithm for campus navigation.
    Supports accessibility filtering and multi-floor navigation.
    """
    
    def __init__(self, accessibility_required=False):
        self.accessibility_required = accessibility_required
        self.graph = {}
        self.distances = {}
        self.previous = {}
        
    def build_graph(self):
        """Build graph from pathways and service points"""
        # Get all service points (nodes)
        service_points = ServicePoint.objects.all()
        
        for sp in service_points:
            self.graph[sp.id] = []
            self.distances[sp.id] = float('inf')
            
        # Get all pathways (edges)
        pathways = Pathway.objects.all()
        if self.accessibility_required:
            pathways = pathways.filter(is_accessible=True)
            
        for pathway in pathways:
            if pathway.start_point and pathway.end_point:
                # Add bidirectional edges
                self.graph[pathway.start_point.id].append({
                    'to': pathway.end_point.id,
                    'distance': pathway.distance_meters,
                    'time': pathway.estimated_time_minutes,
                    'pathway': pathway
                })
                self.graph[pathway.end_point.id].append({
                    'to': pathway.start_point.id,
                    'distance': pathway.distance_meters,
                    'time': pathway.estimated_time_minutes,
                    'pathway': pathway
                })
    
    def find_shortest_path(self, start_id, end_id):
        """
        Find shortest path between two service points using Dijkstra's algorithm.
        Returns: (distance_meters, estimated_time_minutes, path_ids, pathways)
        """
        self.build_graph()
        
        # Initialize
        self.distances[start_id] = 0
        self.previous[start_id] = None
        priority_queue = [(0, start_id)]
        visited = set()
        
        # Dijkstra's algorithm
        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)
            
            if current_id in visited:
                continue
                
            visited.add(current_id)
            
            if current_id == end_id:
                break
            
            # Check neighbors
            for neighbor in self.graph.get(current_id, []):
                neighbor_id = neighbor['to']
                distance = neighbor['distance']
                
                if neighbor_id not in visited:
                    new_distance = self.distances[current_id] + distance
                    
                    if new_distance < self.distances[neighbor_id]:
                        self.distances[neighbor_id] = new_distance
                        self.previous[neighbor_id] = (current_id, neighbor)
                        heapq.heappush(priority_queue, (new_distance, neighbor_id))
        
        # Reconstruct path
        if self.distances[end_id] == float('inf'):
            return None  # No path found
        
        path = []
        pathways = []
        current_id = end_id
        total_time = 0
        
        while current_id is not None:
            path.append(current_id)
            if self.previous[current_id]:
                prev_id, edge_data = self.previous[current_id]
                pathways.append(edge_data['pathway'])
                total_time += edge_data['time']
            current_id = self.previous[current_id][0] if self.previous[current_id] else None
        
        path.reverse()
        
        return {
            'path_ids': path,
            'distance_meters': self.distances[end_id],
            'estimated_time_minutes': total_time,
            'pathways': pathways
        }
    
    def find_nearest_service(self, user_location, service_type=None, radius_meters=100):
        """
        Find nearest service point to user location.
        
        Args:
            user_location: Point object with user's coordinates
            service_type: Optional service type filter
            radius_meters: Search radius
            
        Returns:
            ServicePoint or None
        """
        query = ServicePoint.objects.annotate(
            distance=Distance('location', user_location)
        ).filter(
            distance__lte=radius_meters
        ).order_by('distance')
        
        if service_type:
            query = query.filter(service_type=service_type)
        
        if self.accessibility_required:
            query = query.filter(accessibility_features__isnull=False)
        
        return query.first()
    
    def find_nearby_services(self, user_location, service_type=None, radius_meters=200, limit=5):
        """
        Find multiple nearby service points.
        """
        query = ServicePoint.objects.annotate(
            distance=Distance('location', user_location)
        ).filter(
            distance__lte=radius_meters
        ).order_by('distance')[:limit]
        
        if service_type:
            query = query.filter(service_type=service_type)
        
        if self.accessibility_required:
            query = query.filter(accessibility_features__isnull=False)
        
        return list(query)


def get_or_create_route(start_point_id, end_point_id, accessibility_required=False):
    """
    Get cached route or create new one using pathfinding.
    """
    try:
        # Try to get cached route
        route = Route.objects.get(
            start_point_id=start_point_id,
            end_point_id=end_point_id
        )
        return route
    except Route.DoesNotExist:
        pass
    
    # Calculate new route
    try:
        start_point = ServicePoint.objects.get(id=start_point_id)
        end_point = ServicePoint.objects.get(id=end_point_id)
    except ServicePoint.DoesNotExist:
        return None
    
    pathfinder = PathFinder(accessibility_required=accessibility_required)
    result = pathfinder.find_shortest_path(start_point_id, end_point_id)
    
    if not result:
        return None
    
    # Create and save route
    route = Route.objects.create(
        start_point=start_point,
        end_point=end_point,
        distance_meters=result['distance_meters'],
        estimated_time_minutes=result['estimated_time_minutes'],
        is_accessible=accessibility_required
    )
    
    return route
