"""
Utility functions for data generation and validation.
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np

def generate_ip_address(ipv4_probability: float = 0.9) -> str:
    """Generate a random IP address (IPv4 or IPv6)."""
    if random.random() < ipv4_probability:
        # Generate IPv4
        return ".".join(str(random.randint(0, 255)) for _ in range(4))
    else:
        # Generate IPv6 (simplified)
        return ":".join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(8))

def generate_timestamp(
    start_time: datetime,
    end_time: datetime,
    distribution: str = 'uniform'
) -> datetime:
    """Generate a timestamp within a given range."""
    delta = (end_time - start_time).total_seconds()
    
    if distribution == 'uniform':
        random_seconds = random.uniform(0, delta)
    elif distribution == 'normal':
        # Normal distribution centered at midpoint
        mean_seconds = delta / 2
        std_seconds = delta / 6
        random_seconds = np.random.normal(mean_seconds, std_seconds)
        random_seconds = max(0, min(delta, random_seconds))
    else:
        random_seconds = random.uniform(0, delta)
    
    return start_time + timedelta(seconds=random_seconds)

def weighted_choice(choices: Dict[Any, float]) -> Any:
    """Make a weighted random choice from a dictionary of {value: probability}."""
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights, k=1)[0]

def generate_user_id(min_id: int = 1000, max_id: int = 9999) -> int:
    """Generate a random user ID."""
    return random.randint(min_id, max_id)

def generate_latency(
    base_latency: float = 100.0,
    multiplier: float = 1.0,
    noise_factor: float = 0.3
) -> float:
    """
    Generate latency with noise.
    
    Args:
        base_latency: Base latency in milliseconds
        multiplier: Multiplier for anomaly patterns
        noise_factor: Random noise factor (0.3 = ±30%)
    """
    latency = base_latency * multiplier
    noise = latency * noise_factor * (random.random() * 2 - 1)
    return max(1.0, latency + noise)

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format."""
    parts = ip.split('.')
    if len(parts) == 4:
        # IPv4
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    elif ':' in ip:
        # IPv6 (basic check)
        return len(ip.split(':')) == 8
    return False

def validate_timestamp(timestamp: datetime, min_time: datetime, max_time: datetime) -> bool:
    """Validate timestamp is within range."""
    return min_time <= timestamp <= max_time

def validate_status_code(code: int) -> bool:
    """Validate HTTP status code."""
    return 100 <= code <= 599

def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of values."""
    if not values:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0}
    
    return {
        'mean': np.mean(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'median': np.median(values),
    }

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
