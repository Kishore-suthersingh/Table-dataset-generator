"""
Pattern Learner - Learn statistical patterns from datasets
Extracts distributions, correlations, and value frequencies
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from scipy import stats


@dataclass
class NumericalPattern:
    """Statistical pattern for numerical columns."""
    column_name: str
    mean: float
    std: float
    min: float
    max: float
    median: float
    quantiles: List[float]  # [Q1, Q2, Q3]
    distribution_type: str  # 'normal', 'uniform', 'exponential', 'unknown'
    skewness: float
    kurtosis: float


@dataclass
class CategoricalPattern:
    """Pattern for categorical columns."""
    column_name: str
    unique_values: List[Any]
    value_counts: Dict[Any, int]
    value_frequencies: Dict[Any, float]  # Normalized probabilities
    most_common: List[Tuple[Any, int]]  # Top 10

# ... (PatternProfile and PatternLearner class definition remains same) ...

    def _learn_numerical_pattern(self, col: str) -> NumericalPattern:
        """Learn pattern for numerical column."""
        series = self.df[col].dropna()
        
        # Basic statistics
        mean = series.mean()
        std = series.std()
        min_val = series.min()
        max_val = series.max()
        median = series.median()
        quantiles = series.quantile([0.25, 0.5, 0.75]).tolist()
        
        # Shape statistics
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        # Detect distribution type
        distribution_type = self._detect_distribution(series)
        
        return NumericalPattern(
            column_name=col,
            mean=float(mean),
            std=float(std),
            min=float(min_val),
            max=float(max_val),
            median=float(median),
            quantiles=quantiles,
            distribution_type=distribution_type,
            skewness=float(skewness),
            kurtosis=float(kurtosis)
        )

# ... (PatternProfile and PatternLearner class definition remains same) ...





@dataclass
class PatternProfile:
    """Complete pattern profile of a dataset."""
    numerical_patterns: Dict[str, NumericalPattern] = field(default_factory=dict)
    categorical_patterns: Dict[str, CategoricalPattern] = field(default_factory=dict)
    temporal_patterns: Dict[str, TemporalPattern] = field(default_factory=dict)
    correlations: pd.DataFrame = None
    column_types: Dict[str, str] = field(default_factory=dict)
    row_count: int = 0


class PatternLearner:
    """Learn patterns from datasets for synthetic data generation."""
    
    def __init__(self, df: pd.DataFrame, column_types: Dict[str, str] = None):
        self.df = df
        self.column_types = column_types or {}
        self.pattern_profile = PatternProfile()
    
    def learn_patterns(self) -> PatternProfile:
        """Learn all patterns from the dataset."""
        print("\n[Pattern Learning] Starting analysis...")
        
        self.pattern_profile.row_count = len(self.df)
        self.pattern_profile.column_types = self.column_types
        
        # Learn patterns for each column type
        for col in self.df.columns:
            col_type = self.column_types.get(col, self._infer_type(col))
            
            if col_type == 'numeric':
                pattern = self._learn_numerical_pattern(col)
                self.pattern_profile.numerical_patterns[col] = pattern
                print(f"  ✓ {col}: numerical ({pattern.distribution_type})")
            
            elif col_type == 'categorical':
                pattern = self._learn_categorical_pattern(col)
                self.pattern_profile.categorical_patterns[col] = pattern
                print(f"  ✓ {col}: categorical ({len(pattern.unique_values)} unique)")
            
            elif col_type == 'datetime':
                pattern = self._learn_temporal_pattern(col)
                self.pattern_profile.temporal_patterns[col] = pattern
                print(f"  ✓ {col}: datetime (range: {pattern.date_range_days:.0f} days)")
        
        # Learn correlations between numerical columns
        numeric_cols = list(self.pattern_profile.numerical_patterns.keys())
        if len(numeric_cols) > 1:
            self.pattern_profile.correlations = self.df[numeric_cols].corr()
            print(f"  ✓ Computed correlations for {len(numeric_cols)} numerical columns")
        
        print("[Pattern Learning] Complete!")
        return self.pattern_profile
    
    def _infer_type(self, col: str) -> str:
        """Infer column type if not provided."""
        if pd.api.types.is_numeric_dtype(self.df[col]):
            return 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
            return 'datetime'
        else:
            return 'categorical'
    
    def _learn_numerical_pattern(self, col: str) -> NumericalPattern:
        """Learn pattern for numerical column."""
        series = self.df[col].dropna()
        
        # Basic statistics
        mean = series.mean()
        std = series.std()
        min_val = series.min()
        max_val = series.max()
        median = series.median()
        quantiles = series.quantile([0.25, 0.5, 0.75]).tolist()
        
        # Shape statistics
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        # Detect distribution type
        distribution_type = self._detect_distribution(series)
        
        return NumericalPattern(
            column_name=col,
            mean=float(mean),
            std=float(std),
            min=float(min_val),
            max=float(max_val),
            median=float(median),
            quantiles=quantiles,
            distribution_type=distribution_type,
            skewness=float(skewness),
            kurtosis=float(kurtosis)
        )
    
    def _detect_distribution(self, series: pd.Series) -> str:
        """Detect the best-fit distribution type."""
        # Normalize data
        normalized = (series - series.mean()) / series.std()
        
        # Test for normal distribution
        _, p_value = stats.normaltest(series)
        if p_value > 0.05:  # Not significantly different from normal
            return 'normal'
        
        # Check for uniform distribution  
        if abs(series.skew()) < 0.5 and abs(series.kurtosis()) < 1:
            return 'uniform'
        
        # Check for exponential (right-skewed)
        if series.skew() > 1:
            return 'exponential'
        
        return 'unknown'
    
    def _learn_categorical_pattern(self, col: str) -> CategoricalPattern:
        """Learn pattern for categorical column."""
        series = self.df[col].dropna()
        
        value_counts = series.value_counts()
        unique_values = value_counts.index.tolist()
        counts_dict = value_counts.to_dict()
        
        # Calculate frequencies (probabilities)
        total = value_counts.sum()
        frequencies = {val: count / total for val, count in counts_dict.items()}
        
        # Get most common values
        most_common = value_counts.head(10).items()
        most_common_list = [(val, int(count)) for val, count in most_common]
        
        return CategoricalPattern(
            column_name=col,
            unique_values=unique_values,
            value_counts=counts_dict,
            value_frequencies=frequencies,
            most_common=most_common_list
        )
    
    def _learn_temporal_pattern(self, col: str) -> TemporalPattern:
        """Learn pattern for datetime column."""
        series = pd.to_datetime(self.df[col].dropna())
        
        min_date = series.min()
        max_date = series.max()
        date_range = (max_date - min_date).total_seconds() / 86400  # Convert to days
        
        # Check if it includes time component
        has_time = not all(series.dt.time == pd.Timestamp('00:00:00').time())
        
        return TemporalPattern(
            column_name=col,
            min_date=min_date,
            max_date=max_date,
            date_range_days=date_range,
            has_time_component=has_time
        )
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of learned patterns."""
        summary = {
            'total_rows': self.pattern_profile.row_count,
            'column_count': len(self.df.columns),
            'patterns': {
                'numerical': len(self.pattern_profile.numerical_patterns),
                'categorical': len(self.pattern_profile.categorical_patterns),
                'temporal': len(self.pattern_profile.temporal_patterns)
            }
        }
        
        # Add correlation info
        if self.pattern_profile.correlations is not None:
            # Find strong correlations (|r| > 0.7)
            corr_matrix = self.pattern_profile.correlations
            strong_corr = []
            
            for i in range(len(corr_matrix)):
                for j in range(i+1, len(corr_matrix)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        col1 = corr_matrix.index[i]
                        col2 = corr_matrix.columns[j]
                        strong_corr.append((col1, col2, corr_val))
            
            summary['strong_correlations'] = strong_corr
        
        return summary


# Example usage
if __name__ == "__main__":
    # Create sample data
    df = pd.DataFrame({
        'position': [1, 2, 3, 4, 5],
        'points': [68, 65, 63, 58, 55],
        'wins': [21, 20, 19, 17, 16],
        'team_name': ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Tottenham'],
        'date': pd.date_range('2024-01-01', periods=5)
    })
    
    column_types = {
        'position': 'numeric',
        'points': 'numeric',
        'wins': 'numeric',
        'team_name': 'categorical',
        'date': 'datetime'
    }
    
    # Learn patterns
    learner = PatternLearner(df, column_types)
    profile = learner.learn_patterns()
    
    print("\n" + "="*60)
    print("PATTERN SUMMARY")
    print("="*60)
    summary = learner.get_pattern_summary()
    print(f"Rows: {summary['total_rows']}")
    print(f"Patterns: {summary['patterns']}")
    
    if 'strong_correlations' in summary:
        print("\nStrong Correlations:")
        for col1, col2, corr in summary['strong_correlations']:
            print(f"  {col1} ↔ {col2}: {corr:.3f}")
