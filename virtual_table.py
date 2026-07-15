"""
Virtual table system for storing and querying generated synthetic data.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque
from threading import Lock
from dns_cd_engine import GeneratedRow


class VirtualTable:
    """
    In-memory virtual table that holds generated synthetic data.
    Provides SQL-like query interface and streaming access.
    """
    
    def __init__(self, table_name: str = "synthetic_logs", max_rows: int = 100000):
        self.table_name = table_name
        self.max_rows = max_rows
        self.rows: deque = deque(maxlen=max_rows)  # Auto-expire old data
        self.lock = Lock()
        self.row_count = 0
        self.metadata = {
            'created_at': datetime.utcnow(),
            'last_updated': datetime.utcnow(),
        }
    
    def insert(self, row: GeneratedRow) -> int:
        """
        Insert a generated row into the virtual table.
        
        Args:
            row: GeneratedRow to insert
            
        Returns:
            Row ID
        """
        with self.lock:
            self.row_count += 1
            row_dict = {
                'id': self.row_count,
                'timestamp': row.timestamp,
                'ip_address': row.ip_address,
                'user_id': row.user_id,
                'endpoint': row.endpoint,
                'method': row.method,
                'status_code': row.status_code,
                'latency_ms': row.latency_ms,
                'user_agent': row.user_agent,
                'geo_location': row.geo_location,
            }
            self.rows.append(row_dict)
            self.metadata['last_updated'] = datetime.utcnow()
            return self.row_count
    
    def insert_batch(self, rows: List[GeneratedRow]) -> List[int]:
        """Insert multiple rows in batch."""
        row_ids = []
        for row in rows:
            row_id = self.insert(row)
            row_ids.append(row_id)
        return row_ids
    
    def query_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query all rows (or up to limit).
        
        Args:
            limit: Maximum number of rows to return
            
        Returns:
            List of row dictionaries
        """
        with self.lock:
            rows = list(self.rows)
            if limit:
                rows = rows[-limit:]  # Get most recent
            return rows
    
    def query_filter(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query with filters.
        
        Args:
            filters: Dictionary of field: value filters
            limit: Maximum number of rows to return
            
        Returns:
            Filtered rows
        """
        with self.lock:
            results = []
            for row in self.rows:
                match = True
                for field, value in filters.items():
                    if field not in row or row[field] != value:
                        match = False
                        break
                if match:
                    results.append(row)
                    if limit and len(results) >= limit:
                        break
            return results
    
    def query_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query rows within a time range."""
        with self.lock:
            results = []
            for row in self.rows:
                if start_time <= row['timestamp'] <= end_time:
                    results.append(row)
                    if limit and len(results) >= limit:
                        break
            return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get table statistics."""
        with self.lock:
            total_rows = len(self.rows)
            
            if total_rows == 0:
                return {
                    'total_rows': 0,
                    'table_name': self.table_name,
                    'metadata': self.metadata,
                }
            
            # Calculate statistics
            status_codes = [row['status_code'] for row in self.rows]
            latencies = [row['latency_ms'] for row in self.rows]
            endpoints = [row['endpoint'] for row in self.rows]
            
            from collections import Counter
            status_code_dist = Counter(status_codes)
            endpoint_dist = Counter(endpoints)
            
            return {
                'total_rows': total_rows,
                'table_name': self.table_name,
                'metadata': self.metadata,
                'statistics': {
                    'avg_latency': sum(latencies) / len(latencies),
                    'min_latency': min(latencies),
                    'max_latency': max(latencies),
                    'status_code_distribution': dict(status_code_dist.most_common(5)),
                    'top_endpoints': dict(endpoint_dist.most_common(5)),
                    'unique_ips': len(set(row['ip_address'] for row in self.rows)),
                }
            }
    
    def clear(self):
        """Clear all rows from the table."""
        with self.lock:
            self.rows.clear()
            self.row_count = 0
            self.metadata['last_updated'] = datetime.utcnow()
    
    def get_row_count(self) -> int:
        """Get current number of rows."""
        with self.lock:
            return len(self.rows)
    
    def export_to_list(self) -> List[Dict[str, Any]]:
        """Export all rows as a list."""
        return self.query_all()
