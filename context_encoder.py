"""
Context encoder for analyzing existing data and computing live style vectors.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database_models import TrafficLog
import numpy as np
from collections import Counter
from utils import calculate_statistics


class LiveStyleVector:
    """Represents the current statistical profile of live data."""
    
    def __init__(self):
        self.requests_per_minute: float = 0.0
        self.avg_latency: float = 0.0
        self.status_code_distribution: Dict[int, float] = {}
        self.endpoint_distribution: Dict[str, float] = {}
        self.method_distribution: Dict[str, float] = {}
        self.geo_distribution: Dict[str, float] = {}
        self.ip_diversity: float = 0.0  # Unique IPs / Total requests
        self.avg_requests_per_ip: float = 0.0
        self.user_agent_diversity: float = 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requests_per_minute': self.requests_per_minute,
            'avg_latency': self.avg_latency,
            'status_code_distribution': self.status_code_distribution,
            'endpoint_distribution': self.endpoint_distribution,
            'method_distribution': self.method_distribution,
            'geo_distribution': self.geo_distribution,
            'ip_diversity': self.ip_diversity,
            'avg_requests_per_ip': self.avg_requests_per_ip,
            'user_agent_diversity': self.user_agent_diversity,
        }
    
    def __repr__(self):
        return (f"LiveStyleVector(rpm={self.requests_per_minute:.1f}, "
                f"latency={self.avg_latency:.1f}ms, "
                f"ip_diversity={self.ip_diversity:.2f})")


class ContextEncoder:
    """Encodes live database context into style vectors."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.cache: Optional[LiveStyleVector] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl_seconds = 60  # Cache for 60 seconds
    
    def compute_live_style_vector(
        self,
        lookback_minutes: int = 60,
        force_refresh: bool = False
    ) -> LiveStyleVector:
        """
        Compute the live style vector from recent database data.
        
        Args:
            lookback_minutes: How many minutes of historical data to analyze
            force_refresh: Force recompute even if cache is valid
            
        Returns:
            LiveStyleVector with current statistical profile
        """
        # Check cache
        if not force_refresh and self._is_cache_valid():
            return self.cache
        
        # Compute new vector
        vector = LiveStyleVector()
        
        # Get recent data
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        recent_logs = self.db.query(TrafficLog).filter(
            TrafficLog.timestamp >= cutoff_time
        ).all()
        
        if not recent_logs:
            # Return default values if no data
            return self._get_default_vector()
        
        # Calculate metrics
        total_requests = len(recent_logs)
        time_span_minutes = max(1, lookback_minutes)
        
        # Requests per minute
        vector.requests_per_minute = total_requests / time_span_minutes
        
        # Average latency
        latencies = [log.latency_ms for log in recent_logs]
        vector.avg_latency = np.mean(latencies)
        
        # Status code distribution
        status_codes = [log.status_code for log in recent_logs]
        status_counter = Counter(status_codes)
        vector.status_code_distribution = {
            code: count / total_requests
            for code, count in status_counter.items()
        }
        
        # Endpoint distribution
        endpoints = [log.endpoint for log in recent_logs]
        endpoint_counter = Counter(endpoints)
        vector.endpoint_distribution = {
            endpoint: count / total_requests
            for endpoint, count in endpoint_counter.most_common(10)
        }
        
        # Method distribution
        methods = [log.method for log in recent_logs]
        method_counter = Counter(methods)
        vector.method_distribution = {
            method: count / total_requests
            for method, count in method_counter.items()
        }
        
        # Geo distribution
        geo_locations = [log.geo_location for log in recent_logs if log.geo_location]
        if geo_locations:
            geo_counter = Counter(geo_locations)
            vector.geo_distribution = {
                geo: count / len(geo_locations)
                for geo, count in geo_counter.most_common(10)
            }
        
        # IP diversity
        unique_ips = len(set(log.ip_address for log in recent_logs))
        vector.ip_diversity = unique_ips / total_requests if total_requests > 0 else 0
        vector.avg_requests_per_ip = total_requests / max(1, unique_ips)
        
        # User agent diversity
        user_agents = [log.user_agent for log in recent_logs if log.user_agent]
        if user_agents:
            unique_user_agents = len(set(user_agents))
            vector.user_agent_diversity = unique_user_agents / len(user_agents)
        
        # Update cache
        self.cache = vector
        self.cache_timestamp = datetime.utcnow()
        
        return vector
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self.cache is None or self.cache_timestamp is None:
            return False
        
        age_seconds = (datetime.utcnow() - self.cache_timestamp).total_seconds()
        return age_seconds < self.cache_ttl_seconds
    
    def _get_default_vector(self) -> LiveStyleVector:
        """Get default vector when no data is available."""
        vector = LiveStyleVector()
        vector.requests_per_minute = 10.0
        vector.avg_latency = 150.0
        vector.status_code_distribution = {200: 0.8, 404: 0.1, 500: 0.1}
        vector.method_distribution = {'GET': 0.7, 'POST': 0.2, 'PUT': 0.1}
        vector.ip_diversity = 0.8
        vector.avg_requests_per_ip = 5.0
        return vector
    
    def get_baseline_statistics(self) -> Dict[str, Any]:
        """Get comprehensive baseline statistics."""
        vector = self.compute_live_style_vector()
        return {
            'live_style_vector': vector.to_dict(),
            'summary': {
                'activity_level': 'high' if vector.requests_per_minute > 100 else 'low',
                'performance': 'good' if vector.avg_latency < 200 else 'degraded',
                'traffic_diversity': 'diverse' if vector.ip_diversity > 0.5 else 'concentrated',
            }
        }
