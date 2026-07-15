"""
Enhanced Universal Antigravity System with Pattern-Based Generation
Supports both natural language prompts AND sample dataset analysis
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

from dynamic_schema import SchemaParser, SchemaDefinition
from universal_generator import UniversalDataGenerator
from virtual_table import VirtualTable
from dataset_analyzer import DatasetAnalyzer
from pattern_learner import PatternLearner
from pattern_based_generator import PatternBasedGenerator


class UniversalAntigravity:
    """
    Universal system with two modes:
    1. Natural language prompts → Random generation
    2. Sample dataset upload → Pattern-based generation
    """
    
    def __init__(self):
        self.schema_parser = SchemaParser()
        self.current_schema: Optional[SchemaDefinition] = None
        self.generator: Optional[UniversalDataGenerator] = None
        self.virtual_table: Optional[VirtualTable] = None
        self.generation_history: List[Dict[str, Any]] = []
        
        # Pattern-based generation
        self.pattern_profile = None
        self.pattern_generator = None
    
    def process_prompt(self, prompt: str, row_count: int = 100) -> Dict[str, Any]:
        """
        Generate from natural language prompt (original method).
        """
        start_time = datetime.utcnow()
        
        # Step 1: Parse schema from prompt
        print(f"\n[Step 1] Parsing schema from prompt...")
        self.current_schema = self.schema_parser.parse_natural_language(prompt)
        print(f"  Schema: {self.current_schema}")
        print(f"  Fields: {[f.name for f in self.current_schema.fields]}")
        
        # Step 2: Create generator for this schema
        print(f"\n[Step 2] Initializing data generator...")
        self.generator = UniversalDataGenerator(self.current_schema)
        
        # Step 3: Create virtual table
        print(f"\n[Step 3] Creating virtual table...")
        self.virtual_table = VirtualTable(
            table_name=self.current_schema.table_name,
            max_rows=100000
        )
        
        # Step 4: Generate data
        print(f"\n[Step 4] Generating {row_count} rows...")
        generated_count = 0
        
        for row in self.generator.generate_stream(row_count):
            if 'id' not in row:
                row['id'] = generated_count + 1
            
            row_dict = {'id': row.get('id', generated_count + 1), **row}
            self.virtual_table.rows.append(row_dict)
            generated_count += 1
            
            if generated_count % 1000 == 0:
                print(f"  Generated {generated_count} rows...")
        
        # Step 5: Calculate statistics
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            'success': True,
            'mode': 'prompt',
            'schema': {
                'table_name': self.current_schema.table_name,
                'description': self.current_schema.description,
                'field_count': len(self.current_schema.fields),
                'fields': [
                    {'name': f.name, 'type': f.field_type.value, 'description': f.description}
                    for f in self.current_schema.fields
                ]
            },
            'generation_stats': {
                'rows_generated': generated_count,
                'rows_requested': row_count,
                'duration_seconds': duration,
                'rows_per_second': generated_count / duration if duration > 0 else 0,
            },
            'table_stats': {
                'total_rows': len(self.virtual_table.rows),
                'table_name': self.current_schema.table_name,
            }
        }
        
        print(f"\n[Complete] Generated {generated_count} rows in {duration:.2f}s")
        return result
    
    def process_from_sample(self, sample_file_path: str, n_rows: int = 100, use_web_enrichment: bool = False) -> Dict[str, Any]:
        """
        Generate from sample dataset (pattern-based generation).
        
        Args:
            sample_file_path: Path to CSV/Excel/JSON file
            n_rows: Number of synthetic rows to generate
            use_web_enrichment: If True, search web for reference data to enrich patterns
        """
        start_time = datetime.utcnow()
        
        print(f"\n{'='*60}")
        print("PATTERN-BASED GENERATION")
        if use_web_enrichment:
            print("(With Web Enrichment)")
        print("="*60)
        
        # Step 1: Analyze sample dataset
        print(f"\n[Step 1] Analyzing sample dataset...")
        analyzer = DatasetAnalyzer(sample_file_path)
        sample_df = analyzer.load_dataset()
        column_info = analyzer.infer_column_types()
        quality = analyzer.assess_data_quality()
        
        print(f"  Sample size: {len(sample_df)} rows, {len(sample_df.columns)} columns")
        print(f"  Quality score: {quality.quality_score:.1f}/100")
        
        # Step 1.5: Optional Web Enrichment
        enriched_df = sample_df
        enrichment_info = {}
        
        if use_web_enrichment:
            print(f"\n[Step 1.5] Enriching with web context...")
            from web_enricher import WebContextEnricher
            
            column_types = {col: info.dtype for col, info in column_info.items()}
            enricher = WebContextEnricher(sample_df, column_types)
            enriched_df = enricher.enrich()
            
            enrichment_info = {
                'original_rows': len(sample_df),
                'enriched_rows': len(enriched_df),
                'added_rows': len(enriched_df) - len(sample_df),
                'reference_sources': [ref.source for ref in enricher.reference_datasets]
            }
        
        # Step 2: Learn patterns (from enriched data if applicable)
        print(f"\n[Step 2] Learning statistical patterns...")
        column_types = {col: info.dtype for col, info in column_info.items()}
        learner = PatternLearner(enriched_df, column_types)
        self.pattern_profile = learner.learn_patterns()
        
        # Step 3: Generate synthetic data
        print(f"\n[Step 3] Generating {n_rows} synthetic rows...")
        self.pattern_generator = PatternBasedGenerator(self.pattern_profile)
        synthetic_df = self.pattern_generator.generate_dataset(n_rows)
        
        # Step 4: Store in virtual table
        print(f"\n[Step 4] Storing in virtual table...")
        self.virtual_table = VirtualTable(table_name="pattern_generated")
        
        for idx, row in synthetic_df.iterrows():
            row_dict = row.to_dict()
            row_dict['id'] = idx + 1
            self.virtual_table.rows.append(row_dict)
        
        # Step 5: Calculate statistics
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Get pattern summary
        pattern_summary = learner.get_pattern_summary()
        
        result = {
            'success': True,
            'mode': 'pattern',
            'web_enrichment_used': use_web_enrichment,
            'sample_info': {
                'file_name': analyzer.file_path.name,
                'sample_rows': len(sample_df),
                'quality_score': quality.quality_score,
            },
            'patterns_learned': pattern_summary,
            'generation_stats': {
                'rows_generated': len(synthetic_df),
                'rows_requested': n_rows,
                'duration_seconds': duration,
                'rows_per_second': len(synthetic_df) / duration if duration > 0 else 0,
            },
            'schema': {
                'columns': list(synthetic_df.columns),
                'field_count': len(synthetic_df.columns),
            }
        }
        
        # Add enrichment info if used
        if use_web_enrichment:
            result['enrichment_info'] = enrichment_info
        
        print(f"\n[Complete] Generated {len(synthetic_df)} rows in {duration:.2f}s")
        print("="*60)
        
        return result
    
    def query(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query the virtual table."""
        if not self.virtual_table:
            return []
        
        if filters:
            return self.virtual_table.query_filter(filters, limit=limit)
        else:
            return self.virtual_table.query_all(limit=limit)
    
    def get_schema_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current schema."""
        if not self.current_schema:
            return None
        
        return {
            'table_name': self.current_schema.table_name,
            'description': self.current_schema.description,
            'fields': [
                {
                    'name': f.name,
                    'type': f.field_type.value,
                    'description': f.description,
                    'constraints': {
                        'min_value': f.constraints.min_value if f.constraints else None,
                        'max_value': f.constraints.max_value if f.constraints else None,
                        'required': f.constraints.required if f.constraints else True,
                    }
                }
                for f in self.current_schema.fields
            ]
        }
    
    def export_to_csv(self, filename: str):
        """Export generated data to CSV file."""
        if not self.virtual_table or not self.virtual_table.rows:
            print("No data to export")
            return
        
        import csv
        
        rows = self.virtual_table.query_all()
        if not rows:
            return
        
        fieldnames = list(rows[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ Exported {len(rows)} rows to {filename}")
    
    def clear(self):
        """Clear current data and reset."""
        if self.virtual_table:
            self.virtual_table.clear()
        self.current_schema = None
        self.generator = None
        self.pattern_profile = None
        self.pattern_generator = None


# Example usage
if __name__ == "__main__":
    system = UniversalAntigravity()
    
    print("="*80)
    print("UNIVERSAL ANTIGRAVITY - TWO MODES DEMO")
    print("="*80)
    
    # Mode 1: Natural Language Prompt
    print("\n>>> MODE 1: Generate from Natural Language prompt")
    result1 = system.process_prompt(
        "Create a student records table with name, age, grade, GPA",
        row_count=10
    )
    print(f"\nGenerated: {result1['generation_stats']['rows_generated']} rows")
    
    # Mode 2: Pattern-Based (from sample)
    # First, create a sample CSV
    sample_df = pd.DataFrame({
        'team_name': ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Tottenham'],
        'position': [1, 2, 3, 4, 5],
        'points': [68, 65, 63, 58, 55],
        'wins': [21, 20, 19, 17, 16]
    })
    sample_df.to_csv('sample_premier_league.csv', index=False)
    
    print("\n\n>>> MODE 2: Generate from Sample Dataset")
    system.clear()
    result2 = system.process_from_sample('sample_premier_league.csv', n_rows=20)
    
    print(f"\nSample: {result2['sample_info']['sample_rows']} rows")
    print(f"Generated: {result2['generation_stats']['rows_generated']} rows")
    
    # Show generated data
    data = system.query(limit=5)
    print("\nSample Generated Data:")
    for i, row in enumerate(data, 1):
        print(f"  {i}. {row}")
