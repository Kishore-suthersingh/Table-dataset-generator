"""
DNS-CD (Diffusion with Consistency Distillation) Engine
Generates synthetic tabular data by combining live style vectors with anomaly patterns.
"""
from typing import Dict, Any, List, Generator
from datetime import datetime, timedelta
import random
import numpy as np
from dataclasses import dataclass

from context_encoder import LiveStyleVector
from intent_parser import IntentContext
from config import (
    ANOMALY_PATTERNS, SAMPLE_ENDPOINTS, SAMPLE_USER_AGENTS,
    SAMPLE_GEO_LOCATIONS, HTTP_METHODS, STATUS_CODES
)
from utils import (
    generate_ip_address, generate_timestamp, weighted_choice,
    generate_user_id, generate_latency
)


@dataclass
class GeneratedRow:
    """Represents a single generated table row."""
    timestamp: datetime
    ip_address: str
    user_id: int
    endpoint: str
    method: str
    status_code: int
    latency_ms: float
    user_agent: str
    geo_location: str


class NoiseVector:
    """Represents anomaly characteristics to inject into generation."""
    
    def __init__(self, anomaly_type: str, characteristics: Dict[str, Any]):
        self.anomaly_type = anomaly_type
        self.characteristics = characteristics
    
    def get_characteristic(self, key: str, default: Any = 1.0) -> Any:
        """Get a characteristic value with fallback to default."""
        return self.characteristics.get(key, default)


class SymbolicSkeleton:
    """
    Logic layer that enforces hard constraints on generated data.
    Ensures structural validity (timestamp ordering, valid formats, etc.)
    """
    
    def __init__(self):
        self.last_timestamp: datetime = datetime.utcnow()
        self.min_time_delta_ms = 1  # Minimum time between events
    
    def enforce_timestamp_ordering(self, candidate_timestamp: datetime) -> datetime:
        """Ensure timestamps are monotonically increasing."""
        if candidate_timestamp <= self.last_timestamp:
            # Force ordering by adding minimum delta
            candidate_timestamp = self.last_timestamp + timedelta(milliseconds=self.min_time_delta_ms)
        
        self.last_timestamp = candidate_timestamp
        return candidate_timestamp
    
    def validate_ip_format(self, ip: str) -> str:
        """Ensure IP address has valid format."""
        # Basic validation - could be enhanced
        if not ip or '.' not in ip:
            return generate_ip_address()
        return ip
    
    def validate_status_code(self, code: int) -> int:
        """Ensure status code is valid."""
        if code < 100 or code > 599:
            return 200  # Default to success
        return code
    
    def validate_latency(self, latency: float) -> float:
        """Ensure latency is positive."""
        return max(1.0, latency)


class DNSCDEngine:
    """
    Core generation engine that combines live style vectors with anomaly patterns
    to produce synthetic data via one-shot inference.
    """
    
    def __init__(self):
        self.skeleton = SymbolicSkeleton()
    
    def generate_stream(
        self,
        intent: IntentContext,
        live_vector: LiveStyleVector,
        start_time: datetime,
        rows_per_minute: int = 100
    ) -> Generator[GeneratedRow, None, None]:
        """
        Generate a stream of synthetic rows.
        
        Args:
            intent: Parsed user intent with anomaly type and parameters
            live_vector: Current statistical profile from live data
            start_time: Start time for generation
            rows_per_minute: Target generation rate
            
        Yields:
            GeneratedRow objects
        """
        # Get anomaly characteristics
        anomaly_chars = ANOMALY_PATTERNS.get(intent.anomaly_type, ANOMALY_PATTERNS['normal'])
        noise_vector = NoiseVector(intent.anomaly_type, anomaly_chars['characteristics'])
        
        # Calculate total rows to generate
        total_rows = intent.duration_minutes * rows_per_minute
        end_time = start_time + timedelta(minutes=intent.duration_minutes)
        
        # Adjust RPM based on anomaly multiplier
        if intent.anomaly_type == 'ddos':
            effective_rpm = rows_per_minute * noise_vector.get_characteristic('request_frequency_multiplier', 1.0)
            effective_rpm = int(effective_rpm)
        else:
            effective_rpm = rows_per_minute
        
        # Generate rows
        for i in range(int(effective_rpm * intent.duration_minutes)):
            # Determine if this row should be anomalous
            is_anomaly = random.random() < intent.mix_ratio
            
            # Generate row using consistency distillation
            row = self._one_shot_inference(
                live_vector=live_vector,
                noise_vector=noise_vector if is_anomaly else NoiseVector('normal', ANOMALY_PATTERNS['normal']['characteristics']),
                start_time=start_time,
                end_time=end_time,
                intent=intent
            )
            
            yield row
    
    def _one_shot_inference(
        self,
        live_vector: LiveStyleVector,
        noise_vector: NoiseVector,
        start_time: datetime,
        end_time: datetime,
        intent: IntentContext
    ) -> GeneratedRow:
        """
        One-shot inference: Map combined vector to a valid table row in milliseconds.
        This combines the live statistical profile with the anomaly pattern.
        """
        # Generate timestamp
        base_timestamp = generate_timestamp(start_time, end_time, distribution='uniform')
        timestamp = self.skeleton.enforce_timestamp_ordering(base_timestamp)
        
        # Generate IP address (with diversity control)
        if noise_vector.anomaly_type == 'ddos':
            # DDOS: Low IP diversity
            ip_diversity_factor = noise_vector.get_characteristic('ip_diversity', 1.0)
            if random.random() > ip_diversity_factor:
                # Reuse a "bot" IP
                ip_address = self._get_attack_ip()
            else:
                ip_address = generate_ip_address()
        else:
            ip_address = generate_ip_address()
        
        ip_address = self.skeleton.validate_ip_format(ip_address)
        
        # Generate user_id
        user_id = generate_user_id()
        
        # Generate endpoint
        if noise_vector.anomaly_type == 'ddos':
            # DDOS: High probability of hitting same endpoint
            same_endpoint_prob = noise_vector.get_characteristic('same_endpoint_probability', 0.5)
            if random.random() < same_endpoint_prob:
                endpoint = intent.additional_params.get('specific_endpoint', '/api/products')
            else:
                endpoint = self._sample_from_distribution(live_vector.endpoint_distribution, SAMPLE_ENDPOINTS)
        elif noise_vector.anomaly_type == 'sql_injection':
            # SQL injection: Target specific vulnerable endpoints
            specific_endpoints = noise_vector.get_characteristic('specific_endpoints', SAMPLE_ENDPOINTS)
            endpoint = random.choice(specific_endpoints)
        else:
            # Normal: Use live distribution
            endpoint = self._sample_from_distribution(live_vector.endpoint_distribution, SAMPLE_ENDPOINTS)
        
        # Generate method
        method = self._sample_from_distribution(live_vector.method_distribution, HTTP_METHODS)
        
        # Generate status code (with error rate multiplier)
        error_multiplier = noise_vector.get_characteristic('error_rate_multiplier', 1.0)
        if error_multiplier > 1.0:
            # Increase error probability
            if random.random() < 0.1 * error_multiplier:
                status_code = weighted_choice({400: 0.3, 404: 0.3, 500: 0.2, 503: 0.2})
            else:
                status_code = weighted_choice(STATUS_CODES)
        else:
            status_code = weighted_choice(STATUS_CODES)
        
        status_code = self.skeleton.validate_status_code(status_code)
        
        # Generate latency
        latency_multiplier = noise_vector.get_characteristic('latency_multiplier', 1.0)
        latency_ms = generate_latency(
            base_latency=live_vector.avg_latency if live_vector.avg_latency > 0 else 100.0,
            multiplier=latency_multiplier,
            noise_factor=0.3
        )
        latency_ms = self.skeleton.validate_latency(latency_ms)
        
        # Generate user_agent
        user_agent = self._sample_from_distribution({}, SAMPLE_USER_AGENTS)
        
        # Generate geo_location
        geo_location = self._sample_from_distribution(live_vector.geo_distribution, SAMPLE_GEO_LOCATIONS)
        
        return GeneratedRow(
            timestamp=timestamp,
            ip_address=ip_address,
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            user_agent=user_agent,
            geo_location=geo_location
        )
    
    def _sample_from_distribution(
        self,
        distribution: Dict[str, float],
        fallback_list: List[str]
    ) -> str:
        """Sample from a probability distribution or fallback to random choice."""
        if distribution:
            # Use the live distribution
            return weighted_choice(distribution)
        else:
            # Fallback to random choice
            return random.choice(fallback_list)
    
    def _get_attack_ip(self) -> str:
        """Get a consistent 'attack' IP for DDOS simulation."""
        # Use a small pool of attacker IPs
        attack_ips = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "10.0.0.50",
            "10.0.0.51",
        ]
        return random.choice(attack_ips)
