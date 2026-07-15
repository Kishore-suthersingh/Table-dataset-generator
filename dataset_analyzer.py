"""
Dataset Analyzer - Parse and analyze uploaded datasets
Supports CSV, Excel, JSON formats
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ColumnInfo:
    """Information about a single column."""
    name: str
    dtype: str  # 'numeric', 'categorical', 'datetime', 'text'
    unique_count: int
    null_count: int
    null_percentage: float
    sample_values: List[Any]


@dataclass
class DataQualityReport:
    """Data quality assessment."""
    total_rows: int
    total_columns: int
    columns_with_nulls: List[str]
    duplicate_rows: int
    quality_score: float  # 0-100


class DatasetAnalyzer:
    """Analyze datasets to prepare for pattern learning."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.df: pd.DataFrame = None
        self.column_info: Dict[str, ColumnInfo] = {}
        self.quality_report: DataQualityReport = None
    
    def load_dataset(self) -> pd.DataFrame:
        """Load dataset from file."""
        file_ext = self.file_path.suffix.lower()
        
        try:
            if file_ext == '.csv':
                self.df = pd.read_csv(self.file_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
            elif file_ext == '.json':
                self.df = pd.read_json(self.file_path)
            elif file_ext == '.parquet':
                self.df = pd.read_parquet(self.file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            print(f"✓ Loaded {len(self.df)} rows, {len(self.df.columns)} columns")
            return self.df
        
        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")
    
    def infer_column_types(self) -> Dict[str, ColumnInfo]:
        """Infer and categorize column types."""
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")
        
        for col in self.df.columns:
            dtype = self._categorize_dtype(col)
            unique_count = self.df[col].nunique()
            null_count = self.df[col].isnull().sum()
            null_pct = (null_count / len(self.df)) * 100
            
            # Get sample values (non-null)
            sample_values = self.df[col].dropna().head(10).tolist()
            
            self.column_info[col] = ColumnInfo(
                name=col,
                dtype=dtype,
                unique_count=unique_count,
                null_count=null_count,
                null_percentage=null_pct,
                sample_values=sample_values
            )
        
        return self.column_info
    
    def _categorize_dtype(self, col: str) -> str:
        """Categorize column into: numeric, categorical, datetime, text."""
        series = self.df[col]
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Try to convert to datetime
        if series.dtype == 'object':
            try:
                pd.to_datetime(series.dropna().head(100))
                return 'datetime'
            except:
                pass
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        
        # Categorical vs Text
        if series.dtype == 'object' or series.dtype == 'category':
            unique_ratio = series.nunique() / len(series)
            
            # If less than 50% unique values, likely categorical
            if unique_ratio < 0.5:
                return 'categorical'
            else:
                # Check average string length
                avg_len = series.dropna().astype(str).str.len().mean()
                if avg_len > 50:
                    return 'text'
                else:
                    return 'categorical'
        
        return 'text'  # Default
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistical summary."""
        if self.df is None:
            raise ValueError("Dataset not loaded.")
        
        stats = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'numeric_columns': self.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': self.df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
        }
        
        # Numeric stats
        if len(stats['numeric_columns']) > 0:
            stats['numeric_summary'] = self.df[stats['numeric_columns']].describe().to_dict()
        
        return stats
    
    def assess_data_quality(self) -> DataQualityReport:
        """Assess overall data quality."""
        if self.df is None:
            raise ValueError("Dataset not loaded.")
        
        total_rows = len(self.df)
        total_cols = len(self.df.columns)
        
        # Find columns with nulls
        cols_with_nulls = [col for col in self.df.columns if self.df[col].isnull().any()]
        
        # Count duplicate rows
        duplicate_rows = self.df.duplicated().sum()
        
        # Calculate quality score
        null_penalty = (sum(self.df.isnull().sum()) / (total_rows * total_cols)) * 50
        duplicate_penalty = (duplicate_rows / total_rows) * 30
        quality_score = max(0, 100 - null_penalty - duplicate_penalty)
        
        self.quality_report = DataQualityReport(
            total_rows=total_rows,
            total_columns=total_cols,
            columns_with_nulls=cols_with_nulls,
            duplicate_rows=duplicate_rows,
            quality_score=quality_score
        )
        
        return self.quality_report
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete analysis summary."""
        if self.df is None:
            self.load_dataset()
        
        if not self.column_info:
            self.infer_column_types()
        
        if not self.quality_report:
            self.assess_data_quality()
        
        return {
            'file_name': self.file_path.name,
            'basic_stats': self.get_basic_stats(),
            'column_info': {col: {
                'dtype': info.dtype,
                'unique': info.unique_count,
                'null_pct': f"{info.null_percentage:.1f}%",
                'samples': info.sample_values[:5]
            } for col, info in self.column_info.items()},
            'quality': {
                'score': f"{self.quality_report.quality_score:.1f}/100",
                'issues': {
                    'null_columns': len(self.quality_report.columns_with_nulls),
                    'duplicates': self.quality_report.duplicate_rows
                }
            }
        }


# Example usage
if __name__ == "__main__":
    # Test with a sample CSV
    analyzer = DatasetAnalyzer("sample_data.csv")
    analyzer.load_dataset()
    
    print("\n" + "="*60)
    print("COLUMN TYPES")
    print("="*60)
    column_info = analyzer.infer_column_types()
    for col, info in column_info.items():
        print(f"{col}: {info.dtype} ({info.unique_count} unique, {info.null_percentage:.1f}% null)")
    
    print("\n" + "="*60)
    print("QUALITY REPORT")
    print("="*60)
    quality = analyzer.assess_data_quality()
    print(f"Quality Score: {quality.quality_score:.1f}/100")
    print(f"Duplicate Rows: {quality.duplicate_rows}")
    print(f"Columns with Nulls: {len(quality.columns_with_nulls)}")
