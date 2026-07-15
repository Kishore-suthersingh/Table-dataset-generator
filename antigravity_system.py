"""
Main Antigravity system orchestrator.
Coordinates all 5 stages of the workflow.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from intent_parser import IntentParser, IntentContext
from context_encoder import ContextEncoder, LiveStyleVector
from dns_cd_engine import DNSCDEngine, GeneratedRow
from validator import Validator, ValidationResult
from virtual_table import VirtualTable
from database_models import SessionLocal, init_database, TrafficLog
from config import GenerationConfig


class AntigravitySystem:
    """
    Main orchestrator for the Antigravity synthetic data generation system.
    Implements the 5-stage workflow:
    1. Intent Parsing
    2. Context Acquisition
    3. Generation Loop (DNS-CD)
    4. Real-Time Governance (Validation)
    5. Deployment (Virtual Table)
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session if db_session else SessionLocal()
        self.config = GenerationConfig()
        
        # Initialize components
        self.intent_parser = IntentParser()
        self.context_encoder = ContextEncoder(self.db)
        self.generator = DNSCDEngine()
        self.validator = Validator(self.db, strict_mode=False)
        self.virtual_table = VirtualTable(table_name="antigravity.synthetic_logs")
        
        self.is_generating = False
        self.current_session: Optional[Dict[str, Any]] = None
    
    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Process a user prompt through all 5 stages.
        
        Args:
            prompt: Natural language prompt from user
            
        Returns:
            Dictionary with generation results and statistics
        """
        # Stage 1: Intent Parsing
        print(f"\n[Stage 1] Parsing intent from prompt...")
        intent = self.intent_parser.parse(prompt)
        print(f"  Parsed: {intent}")
        
        # Check for impossible requests
        impossible_error = self.validator.check_impossible_request(intent.additional_params)
        if impossible_error:
            return {
                'success': False,
                'error': impossible_error,
                'stage': 'validation'
            }
        
        # Stage 2: Context Acquisition
        print(f"\n[Stage 2] Acquiring live context...")
        live_vector = self.context_encoder.compute_live_style_vector(lookback_minutes=60)
        print(f"  Live Vector: {live_vector}")
        
        # Stage 3 & 4: Generation + Validation Loop
        print(f"\n[Stage 3 & 4] Starting generation and validation...")
        start_time = datetime.utcnow()
        
        generation_stats = {
            'generated': 0,
            'validated': 0,
            'corrected': 0,
            'rejected': 0,
        }
        
        # Generate stream of data
        for generated_row in self.generator.generate_stream(
            intent=intent,
            live_vector=live_vector,
            start_time=start_time,
            rows_per_minute=self.config.rows_per_minute
        ):
            generation_stats['generated'] += 1
            
            # Validate row (Stage 4)
            validation_result = self.validator.validate(generated_row)
            
            if validation_result.is_valid:
                generation_stats['validated'] += 1
                if validation_result.corrections:
                    generation_stats['corrected'] += 1
                
                # Stage 5: Insert into virtual table
                self.virtual_table.insert(validation_result.row)
            else:
                generation_stats['rejected'] += 1
            
            # Progress update
            if generation_stats['generated'] % 1000 == 0:
                print(f"  Generated {generation_stats['generated']} rows...")
        
        # Final statistics
        print(f"\n[Stage 5] Generation complete!")
        table_stats = self.virtual_table.get_statistics()
        validator_stats = self.validator.get_statistics()
        
        return {
            'success': True,
            'intent': intent,
            'live_vector': live_vector.to_dict(),
            'generation_stats': generation_stats,
            'validation_stats': validator_stats,
            'table_stats': table_stats,
            'duration_seconds': (datetime.utcnow() - start_time).total_seconds(),
        }
    
    def query_virtual_table(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query the virtual table."""
        if filters:
            return self.virtual_table.query_filter(filters, limit=limit)
        else:
            return self.virtual_table.query_all(limit=limit)
    
    def get_table_statistics(self) -> Dict[str, Any]:
        """Get virtual table statistics."""
        return self.virtual_table.get_statistics()
    
    def clear_virtual_table(self):
        """Clear all data from virtual table."""
        self.virtual_table.clear()
        print("Virtual table cleared.")
    
    def export_to_database(self, target_table: str = "traffic_logs") -> int:
        """
        Export virtual table data to the actual database.
        
        Args:
            target_table: Target table name
            
        Returns:
            Number of rows exported
        """
        rows = self.virtual_table.export_to_list()
        
        exported_count = 0
        for row in rows:
            try:
                # Create TrafficLog object
                log = TrafficLog(
                    timestamp=row['timestamp'],
                    ip_address=row['ip_address'],
                    user_id=row['user_id'],
                    endpoint=row['endpoint'],
                    method=row['method'],
                    status_code=row['status_code'],
                    latency_ms=row['latency_ms'],
                    user_agent=row['user_agent'],
                    geo_location=row['geo_location'],
                )
                self.db.add(log)
                exported_count += 1
            except Exception as e:
                print(f"Error exporting row: {e}")
        
        self.db.commit()
        print(f"Exported {exported_count} rows to {target_table}")
        return exported_count
    
    def close(self):
        """Close database connections."""
        if self.db:
            self.db.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Create system
    system = AntigravitySystem()
    
    # Example prompt
    prompt = "Simulate a DDOS attack pattern on our traffic logs mixed with normal user behavior for the next 30 minutes."
    
    # Process prompt
    result = system.process_prompt(prompt)
    
    # Print results
    print("\n" + "="*60)
    print("GENERATION RESULTS")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Generated: {result['generation_stats']['generated']} rows")
    print(f"Validated: {result['generation_stats']['validated']} rows")
    print(f"Corrected: {result['generation_stats']['corrected']} rows")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    
    print("\nTable Statistics:")
    print(f"  Total Rows: {result['table_stats']['total_rows']}")
    print(f"  Avg Latency: {result['table_stats']['statistics']['avg_latency']:.2f}ms")
    print(f"  Unique IPs: {result['table_stats']['statistics']['unique_ips']}")
    
    # Query some data
    print("\n" + "="*60)
    print("SAMPLE DATA (First 5 rows)")
    print("="*60)
    sample_data = system.query_virtual_table(limit=5)
    for i, row in enumerate(sample_data, 1):
        print(f"\nRow {i}:")
        print(f"  Timestamp: {row['timestamp']}")
        print(f"  IP: {row['ip_address']}")
        print(f"  Endpoint: {row['endpoint']}")
        print(f"  Status: {row['status_code']}")
        print(f"  Latency: {row['latency_ms']:.2f}ms")
    
    # Close
    system.close()
