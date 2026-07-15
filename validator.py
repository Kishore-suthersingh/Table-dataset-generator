"""
Validator for real-time governance and data quality assurance.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from database_models import User, TrafficLog
from dns_cd_engine import GeneratedRow
import numpy as np


class ValidationResult:
    """Result of validation with any corrections applied."""
    
    def __init__(self, is_valid: bool, row: GeneratedRow, errors: List[str] = None, corrections: List[str] = None):
        self.is_valid = is_valid
        self.row = row
        self.errors = errors or []
        self.corrections = corrections or []
    
    def __repr__(self):
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, errors={len(self.errors)}, corrections={len(self.corrections)})"


class Validator:
    """
    Real-time governance system that validates generated data.
    Implements:
    - Referential integrity checks
    - Business logic rules
    - Differentiable logic loss (auto-correction)
    """
    
    def __init__(self, db_session: Optional[Session] = None, strict_mode: bool = False):
        self.db = db_session
        self.strict_mode = strict_mode  # If True, reject invalid rows; if False, auto-correct
        self.validation_stats = {
            'total_validated': 0,
            'valid': 0,
            'corrected': 0,
            'rejected': 0,
        }
    
    def validate(self, row: GeneratedRow) -> ValidationResult:
        """
        Validate a generated row against all rules.
        
        Args:
            row: Generated row to validate
            
        Returns:
            ValidationResult with validation status and any corrections
        """
        self.validation_stats['total_validated'] += 1
        
        errors = []
        corrections = []
        corrected_row = row
        
        # 1. Referential integrity checks
        ref_errors, ref_corrections, corrected_row = self._check_referential_integrity(corrected_row)
        errors.extend(ref_errors)
        corrections.extend(ref_corrections)
        
        # 2. Business logic rules
        logic_errors, logic_corrections, corrected_row = self._check_business_logic(corrected_row)
        errors.extend(logic_errors)
        corrections.extend(logic_corrections)
        
        # 3. Data format validation
        format_errors, format_corrections, corrected_row = self._check_data_formats(corrected_row)
        errors.extend(format_errors)
        corrections.extend(format_corrections)
        
        # Determine result
        if errors and self.strict_mode:
            self.validation_stats['rejected'] += 1
            return ValidationResult(is_valid=False, row=row, errors=errors)
        elif corrections:
            self.validation_stats['corrected'] += 1
            return ValidationResult(is_valid=True, row=corrected_row, errors=errors, corrections=corrections)
        else:
            self.validation_stats['valid'] += 1
            return ValidationResult(is_valid=True, row=corrected_row)
    
    def _check_referential_integrity(self, row: GeneratedRow) -> Tuple[List[str], List[str], GeneratedRow]:
        """Check referential integrity (e.g., foreign key constraints)."""
        errors = []
        corrections = []
        
        # Check if user_id exists (if we have DB access)
        if self.db:
            user_exists = self.db.query(User).filter(User.id == row.user_id).first()
            if not user_exists:
                errors.append(f"User ID {row.user_id} does not exist")
                if not self.strict_mode:
                    # Create a default user_id or use nullable
                    row = GeneratedRow(
                        timestamp=row.timestamp,
                        ip_address=row.ip_address,
                        user_id=None,  # Set to None if invalid
                        endpoint=row.endpoint,
                        method=row.method,
                        status_code=row.status_code,
                        latency_ms=row.latency_ms,
                        user_agent=row.user_agent,
                        geo_location=row.geo_location
                    )
                    corrections.append(f"Set user_id to None (user not found)")
        
        return errors, corrections, row
    
    def _check_business_logic(self, row: GeneratedRow) -> Tuple[List[str], List[str], GeneratedRow]:
        """Check business logic rules."""
        errors = []
        corrections = []
        
        # Rule 1: Latency must be positive
        if row.latency_ms <= 0:
            errors.append(f"Invalid latency: {row.latency_ms}")
            if not self.strict_mode:
                # Differentiable logic loss: Project to nearest valid value
                row = GeneratedRow(
                    timestamp=row.timestamp,
                    ip_address=row.ip_address,
                    user_id=row.user_id,
                    endpoint=row.endpoint,
                    method=row.method,
                    status_code=row.status_code,
                    latency_ms=abs(row.latency_ms) if row.latency_ms < 0 else 1.0,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Corrected latency to {row.latency_ms}")
        
        # Rule 2: Latency should be reasonable (< 10 seconds)
        if row.latency_ms > 10000:
            errors.append(f"Unreasonably high latency: {row.latency_ms}ms")
            if not self.strict_mode:
                # Cap at maximum reasonable value
                row = GeneratedRow(
                    timestamp=row.timestamp,
                    ip_address=row.ip_address,
                    user_id=row.user_id,
                    endpoint=row.endpoint,
                    method=row.method,
                    status_code=row.status_code,
                    latency_ms=10000.0,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Capped latency at 10000ms")
        
        # Rule 3: Status code must be valid HTTP code
        if row.status_code < 100 or row.status_code > 599:
            errors.append(f"Invalid status code: {row.status_code}")
            if not self.strict_mode:
                row = GeneratedRow(
                    timestamp=row.timestamp,
                    ip_address=row.ip_address,
                    user_id=row.user_id,
                    endpoint=row.endpoint,
                    method=row.method,
                    status_code=200,  # Default to success
                    latency_ms=row.latency_ms,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Corrected status code to 200")
        
        # Rule 4: Timestamp must be in the past or near-present (not future)
        if row.timestamp > datetime.utcnow():
            errors.append(f"Future timestamp: {row.timestamp}")
            if not self.strict_mode:
                row = GeneratedRow(
                    timestamp=datetime.utcnow(),
                    ip_address=row.ip_address,
                    user_id=row.user_id,
                    endpoint=row.endpoint,
                    method=row.method,
                    status_code=row.status_code,
                    latency_ms=row.latency_ms,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Corrected timestamp to current time")
        
        return errors, corrections, row
    
    def _check_data_formats(self, row: GeneratedRow) -> Tuple[List[str], List[str], GeneratedRow]:
        """Check data format validity."""
        errors = []
        corrections = []
        
        # Check IP address format (basic)
        if not row.ip_address or '.' not in row.ip_address:
            errors.append(f"Invalid IP format: {row.ip_address}")
            if not self.strict_mode:
                from utils import generate_ip_address
                new_ip = generate_ip_address()
                row = GeneratedRow(
                    timestamp=row.timestamp,
                    ip_address=new_ip,
                    user_id=row.user_id,
                    endpoint=row.endpoint,
                    method=row.method,
                    status_code=row.status_code,
                    latency_ms=row.latency_ms,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Generated new valid IP: {new_ip}")
        
        # Check endpoint format
        if not row.endpoint or not row.endpoint.startswith('/'):
            errors.append(f"Invalid endpoint format: {row.endpoint}")
            if not self.strict_mode:
                row = GeneratedRow(
                    timestamp=row.timestamp,
                    ip_address=row.ip_address,
                    user_id=row.user_id,
                    endpoint='/' if not row.endpoint else f'/{row.endpoint}',
                    method=row.method,
                    status_code=row.status_code,
                    latency_ms=row.latency_ms,
                    user_agent=row.user_agent,
                    geo_location=row.geo_location
                )
                corrections.append(f"Corrected endpoint format")
        
        return errors, corrections, row
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total = self.validation_stats['total_validated']
        if total == 0:
            return self.validation_stats
        
        return {
            **self.validation_stats,
            'valid_percentage': (self.validation_stats['valid'] / total) * 100,
            'corrected_percentage': (self.validation_stats['corrected'] / total) * 100,
            'rejected_percentage': (self.validation_stats['rejected'] / total) * 100,
        }
    
    def check_impossible_request(self, intent_params: Dict[str, Any]) -> Optional[str]:
        """
        Check if a request is impossible and return helpful feedback.
        
        Args:
            intent_params: Parameters from user intent
            
        Returns:
            Error message if impossible, None otherwise
        """
        # Check for impossible constraints
        if 'status_code_digits' in intent_params:
            digits = intent_params['status_code_digits']
            if digits != 3:
                return f"HTTP status codes must be 3 digits. Requested: {digits} digits."
        
        if 'negative_latency' in intent_params and intent_params['negative_latency']:
            return "Latency cannot be negative. Please specify a positive value."
        
        if 'future_date' in intent_params and intent_params['future_date'] > datetime.utcnow():
            return "Cannot generate historical data with future timestamps."
        
        return None
