"""
Pattern-Based Generator - Generate synthetic data matching learned patterns
Uses statistical distributions and frequencies from pattern profiles
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import timedelta
import random

from pattern_learner import PatternProfile, NumericalPattern, CategoricalPattern, TemporalPattern


class PatternBasedGenerator:
    """Generate synthetic data based on learned patterns."""
    
    def __init__(self, pattern_profile: PatternProfile):
        self.profile = pattern_profile
        self.generated_df = None
    
    def generate_dataset(self, n_rows: int) -> pd.DataFrame:
        """Generate a complete dataset with n_rows rows."""
        print(f"\n[Generating] Creating {n_rows} synthetic rows...")
        
        data = {}
        
        # Generate numerical columns
        for col, pattern in self.profile.numerical_patterns.items():
            data[col] = self._generate_numerical_column(pattern, n_rows)
            print(f"  ✓ {col}: numerical")
        
        # Generate categorical columns
        for col, pattern in self.profile.categorical_patterns.items():
            data[col] = self._generate_categorical_column(pattern, n_rows)
            print(f"  ✓ {col}: categorical")
        
        # Generate temporal columns
        for col, pattern in self.profile.temporal_patterns.items():
            data[col] = self._generate_temporal_column(pattern, n_rows)
            print(f"  ✓ {col}: temporal")
        
        self.generated_df = pd.DataFrame(data)
        
        # Apply correlations if needed
        if self.profile.correlations is not None and len(self.profile.numerical_patterns) > 1:
            self._apply_correlations()
            print(f"  ✓ Applied correlations")
        
        print(f"[Generating] Complete! Generated {len(self.generated_df)} rows")
        return self.generated_df
    
    def _generate_numerical_column(self, pattern: NumericalPattern, n_rows: int) -> np.ndarray:
        """Generate numerical column based on learned pattern."""
        if pattern.distribution_type == 'normal':
            # Generate from normal distribution
            values = np.random.normal(pattern.mean, pattern.std, n_rows)
            # Clip to observed range
            values = np.clip(values, pattern.min, pattern.max)
        
        elif pattern.distribution_type == 'uniform':
            # Generate from uniform distribution
            values = np.random.uniform(pattern.min, pattern.max, n_rows)
        
        elif pattern.distribution_type == 'exponential':
            # Generate from exponential (right-skewed)
            scale = pattern.mean - pattern.min
            values = pattern.min + np.random.exponential(scale, n_rows)
            values = np.clip(values, pattern.min, pattern.max)
        
        else:
            # Unknown distribution - use normal as fallback
            values = np.random.normal(pattern.mean, pattern.std, n_rows)
            values = np.clip(values, pattern.min, pattern.max)
        
        # Preserve integer type if original was integer
        if pattern.std > 0 and (pattern.max - pattern.min) / pattern.std > 10:
            # Likely integer data
            values = np.round(values)
        
        return values
    
    def _generate_categorical_column(self, pattern: CategoricalPattern, n_rows: int) -> List[Any]:
        """Generate categorical column based on value frequencies."""
        # Sample from the learned frequency distribution
        values = random.choices(
            population=pattern.unique_values,
            weights=[pattern.value_frequencies[val] for val in pattern.unique_values],
            k=n_rows
        )
        return values
    
    def _generate_temporal_column(self, pattern: TemporalPattern, n_rows: int) -> pd.Series:
        """Generate datetime column based on learned pattern."""
        # Generate uniformly distributed dates within the range
        total_seconds = pattern.date_range_days * 86400
        random_seconds = np.random.uniform(0, total_seconds, n_rows)
        
        dates = [pattern.min_date + timedelta(seconds=float(s)) for s in random_seconds]
        
        # If original didn't have time component, truncate to date only
        if not pattern.has_time_component:
            dates = [pd.Timestamp(d.date()) for d in dates]
        
        return pd.Series(dates)
    
    def _apply_correlations(self):
        """Adjust numerical columns to maintain correlations."""
        # Get numerical columns
        numeric_cols = list(self.profile.numerical_patterns.keys())
        
        if len(numeric_cols) < 2:
            return
        
        # Get current values
        current_data = self.generated_df[numeric_cols].values
        
        # Get target correlation matrix
        target_corr = self.profile.correlations.values
        
        # Apply Chol Sky decomposition to introduce correlations
        # This is a simplified approach - for production, use more sophisticated methods
        try:
            # Standardize current data
            mean = current_data.mean(axis=0)
            std = current_data.std(axis=0)
            standardized = (current_data - mean) / std
            
            # Compute Cholesky decomposition of target correlation
            L = np.linalg.cholesky(target_corr)
            
            # Apply transformation
            correlated = standardized @ L.T
            
            # De-standardize
            final = correlated * std + mean
            
            # Update dataframe
            for i, col in enumerate(numeric_cols):
                pattern = self.profile.numerical_patterns[col]
                # Clip to original range
                self.generated_df[col] = np.clip(final[:, i], pattern.min, pattern.max)
        
        except np.linalg.LinAlgError:
            # If correlation matrix is not positive definite, skip
            print("  ! Warning: Could not apply correlations (matrix not positive definite)")
            pass


# Example usage
if __name__ == "__main__":
    from pattern_learner import PatternLearner
    
    # Create sample data
    original_df = pd.DataFrame({
        'position': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'points': [68, 65, 63, 58, 55, 52, 49, 45, 42, 38],
        'wins': [21, 20, 19, 17, 16, 15, 14, 13, 12, 11],
        'team_name': ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Tottenham', 
                      'Newcastle', 'Brighton', 'Aston Villa', 'West Ham', 'Palace']
    })
    
    column_types = {
        'position': 'numeric',
        'points': 'numeric',
        'wins': 'numeric',
        'team_name': 'categorical'
    }
    
    print("="*60)
    print("PATTERN-BASED GENERATION DEMO")
    print("="*60)
    print(f"\nOriginal Dataset: {len(original_df)} rows")
    print(original_df.head())
    
    # Learn patterns
    learner = PatternLearner(original_df, column_types)
    profile = learner.learn_patterns()
    
    # Generate new data
    generator = PatternBasedGenerator(profile)
    synthetic_df = generator.generate_dataset(n_rows=20)
    
    print(f"\n{'='*60}")
    print("GENERATED DATASET")
    print("="*60)
    print(f"Generated: {len(synthetic_df)} rows")
    print(synthetic_df.head(10))
    
    # Compare statistics
    print(f"\n{'='*60}")
    print("COMPARISON")
    print("="*60)
    print("\nOriginal Statistics:")
    print(original_df.describe())
    print("\nGenerated Statistics:")
    print(synthetic_df.describe())
