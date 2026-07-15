"""
Configuration for Antigravity table generation system.
"""
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    url: str = "sqlite:///antigravity.db"
    echo: bool = False

@dataclass
class GenerationConfig:
    """Data generation configuration."""
    default_duration_minutes: int = 30
    rows_per_minute: int = 100
    max_concurrent_streams: int = 10

# Anomaly pattern definitions
ANOMALY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "ddos": {
        "description": "Distributed Denial of Service attack pattern",
        "characteristics": {
            "request_frequency_multiplier": 50.0,  # 50x normal frequency
            "ip_diversity": 0.1,  # Low diversity (10% of normal)
            "same_endpoint_probability": 0.8,  # 80% hit same endpoint
            "error_rate_multiplier": 5.0,  # 5x more errors
            "latency_multiplier": 3.0,  # 3x higher latency
        }
    },
    "sql_injection": {
        "description": "SQL injection attack pattern",
        "characteristics": {
            "malicious_payload_probability": 0.3,
            "error_rate_multiplier": 10.0,
            "specific_endpoints": ["/search", "/login", "/api/query"],
        }
    },
    "normal": {
        "description": "Normal user behavior",
        "characteristics": {
            "request_frequency_multiplier": 1.0,
            "ip_diversity": 1.0,
            "error_rate": 0.05,  # 5% error rate
        }
    }
}

# Default traffic log schema
TRAFFIC_LOG_SCHEMA = {
    "id": "integer",
    "timestamp": "datetime",
    "ip_address": "string",
    "user_id": "integer",
    "endpoint": "string",
    "method": "string",
    "status_code": "integer",
    "latency_ms": "float",
    "user_agent": "string",
    "geo_location": "string",
}

# Sample endpoints for generation
SAMPLE_ENDPOINTS = [
    "/",
    "/api/users",
    "/api/products",
    "/api/orders",
    "/search",
    "/login",
    "/logout",
    "/dashboard",
    "/settings",
    "/api/analytics",
]

# Sample user agents
SAMPLE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
]

# Sample geo locations
SAMPLE_GEO_LOCATIONS = [
    "US-CA", "US-NY", "UK-LON", "IN-MH", "JP-TK",
    "DE-BE", "FR-PA", "AU-NSW", "CA-ON", "BR-SP",
]

# HTTP methods
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Status codes and their probabilities
STATUS_CODES = {
    200: 0.80,  # Success
    201: 0.05,  # Created
    400: 0.03,  # Bad request
    401: 0.02,  # Unauthorized
    404: 0.05,  # Not found
    500: 0.03,  # Server error
    503: 0.02,  # Service unavailable
}
