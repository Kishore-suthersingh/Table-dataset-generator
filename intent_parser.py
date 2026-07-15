"""
Intent parser for extracting entities and anomaly patterns from user prompts.
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import timedelta
from config import ANOMALY_PATTERNS

@dataclass
class IntentContext:
    """Structured representation of parsed user intent."""
    anomaly_type: str  # "ddos", "sql_injection", "normal"
    target_schema: str  # "traffic_logs"
    duration_minutes: int
    baseline_behavior: str  # "normal"
    mix_ratio: float  # 0.0 to 1.0 (ratio of anomaly to normal)
    additional_params: Dict[str, Any]
    
    def __repr__(self):
        return (f"IntentContext(anomaly={self.anomaly_type}, "
                f"duration={self.duration_minutes}m, "
                f"mix_ratio={self.mix_ratio:.2f})")


class IntentParser:
    """Parser for extracting intent from natural language prompts."""
    
    def __init__(self):
        self.anomaly_patterns = ANOMALY_PATTERNS
        
        # Pattern matching rules
        self.duration_patterns = [
            (r'(\d+)\s*minutes?', lambda m: int(m.group(1))),
            (r'(\d+)\s*hours?', lambda m: int(m.group(1)) * 60),
            (r'(\d+)\s*seconds?', lambda m: max(1, int(m.group(1)) // 60)),
        ]
        
        self.anomaly_keywords = {
            'ddos': ['ddos', 'denial of service', 'traffic spike', 'flood'],
            'sql_injection': ['sql injection', 'sql inject', 'malicious query'],
            'normal': ['normal', 'regular', 'baseline', 'typical'],
        }
        
        self.schema_keywords = {
            'traffic_logs': ['traffic', 'log', 'request', 'http'],
        }
    
    def parse(self, prompt: str) -> IntentContext:
        """
        Parse a user prompt into structured intent.
        
        Args:
            prompt: Natural language prompt from user
            
        Returns:
            IntentContext with extracted entities
        """
        prompt_lower = prompt.lower()
        
        # Extract anomaly type
        anomaly_type = self._extract_anomaly_type(prompt_lower)
        
        # Extract target schema
        target_schema = self._extract_target_schema(prompt_lower)
        
        # Extract duration
        duration_minutes = self._extract_duration(prompt_lower)
        
        # Extract mix ratio
        mix_ratio = self._extract_mix_ratio(prompt_lower, anomaly_type)
        
        # Extract baseline behavior
        baseline = self._extract_baseline(prompt_lower)
        
        # Additional parameters
        additional_params = self._extract_additional_params(prompt_lower)
        
        return IntentContext(
            anomaly_type=anomaly_type,
            target_schema=target_schema,
            duration_minutes=duration_minutes,
            baseline_behavior=baseline,
            mix_ratio=mix_ratio,
            additional_params=additional_params,
        )
    
    def _extract_anomaly_type(self, prompt: str) -> str:
        """Extract anomaly type from prompt."""
        for anomaly_type, keywords in self.anomaly_keywords.items():
            for keyword in keywords:
                if keyword in prompt:
                    return anomaly_type
        return 'normal'
    
    def _extract_target_schema(self, prompt: str) -> str:
        """Extract target schema/table from prompt."""
        for schema, keywords in self.schema_keywords.items():
            for keyword in keywords:
                if keyword in prompt:
                    return schema
        return 'traffic_logs'  # Default
    
    def _extract_duration(self, prompt: str) -> int:
        """Extract duration from prompt."""
        for pattern, extractor in self.duration_patterns:
            match = re.search(pattern, prompt)
            if match:
                return extractor(match)
        return 30  # Default 30 minutes
    
    def _extract_mix_ratio(self, prompt: str, anomaly_type: str) -> float:
        """
        Extract the mix ratio of anomaly to normal traffic.
        Returns value between 0.0 (all normal) and 1.0 (all anomaly).
        """
        if anomaly_type == 'normal':
            return 0.0
        
        # Look for explicit ratio mentions
        ratio_pattern = r'(\d+)%?\s*(?:anomaly|attack|malicious)'
        match = re.search(ratio_pattern, prompt)
        if match:
            percentage = int(match.group(1))
            return min(1.0, percentage / 100.0)
        
        # Look for keywords indicating mix
        if 'mixed with' in prompt or 'combined with' in prompt:
            return 0.3  # 30% anomaly by default
        elif 'mostly normal' in prompt:
            return 0.1  # 10% anomaly
        elif 'mostly attack' in prompt or 'mostly anomaly' in prompt:
            return 0.8  # 80% anomaly
        
        # Default: 50-50 mix
        return 0.5
    
    def _extract_baseline(self, prompt: str) -> str:
        """Extract baseline behavior type."""
        if 'normal' in prompt or 'regular' in prompt:
            return 'normal'
        return 'normal'
    
    def _extract_additional_params(self, prompt: str) -> Dict[str, Any]:
        """Extract additional parameters from prompt."""
        params = {}
        
        # Extract specific IP if mentioned
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_match = re.search(ip_pattern, prompt)
        if ip_match:
            params['specific_ip'] = ip_match.group(0)
        
        # Extract specific endpoint if mentioned
        endpoint_pattern = r'\/[a-z\/]+(?:\s|$)'
        endpoint_match = re.search(endpoint_pattern, prompt)
        if endpoint_match:
            params['specific_endpoint'] = endpoint_match.group(0).strip()
        
        return params
    
    def get_anomaly_characteristics(self, anomaly_type: str) -> Dict[str, Any]:
        """Get the characteristic profile for an anomaly type."""
        return self.anomaly_patterns.get(anomaly_type, self.anomaly_patterns['normal'])


# Example usage
if __name__ == "__main__":
    parser = IntentParser()
    
    # Test examples
    test_prompts = [
        "Simulate a DDOS attack pattern on our traffic logs mixed with normal user behavior for the next 30 minutes.",
        "Generate normal traffic for 1 hour",
        "Create SQL injection attempts on the /login endpoint for 15 minutes with 20% attack rate",
    ]
    
    for prompt in test_prompts:
        context = parser.parse(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Parsed: {context}")
