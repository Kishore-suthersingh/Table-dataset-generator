"""
Test: Strict Type Preservation in Pattern Generation
Verifies that integer columns in sample result in integer columns in synthetic data (not floats).
"""
import pandas as pd
import numpy as np
from pattern_learner import PatternLearner
from pattern_based_generator import PatternBasedGenerator

def test_strict_types():
    print("="*60)
    print("TEST: STRICT TYPE PRESERVATION")
    print("="*60)
    
    # Create valid sample data with mixed types
    # Age: Integer
    # Salary: Float (with decimals)
    # Name: String
    # GPA: Float (but looks like int? no, 3.5)
    
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],  # Explicit integers
        'salary': [50000.50, 60000.75, 75000.25, 80000.00, 90000.50], # Floats
        'years_experience': [1.0, 2.0, 5.0, 8.0, 10.0], # Floats that are actually integers
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
    })
    
    print("\n[Input] Sample Data Types:")
    print(df.dtypes)
    print("\nSample Data:")
    print(df)
    
    # 1. Learn Patterns
    print("\n[Step 1] Learning patterns...")
    learner = PatternLearner(df)
    profile = learner.learn_patterns()
    
    print("\nLearned Type Info:")
    for col, pattern in profile.numerical_patterns.items():
        print(f"  {col}: is_integer={pattern.is_integer}")
        
        
    # 2. Generate Data
    print("\n[Step 2] Generating synthetic data...")
    generator = PatternBasedGenerator(profile)
    synthetic = generator.generate_dataset(n_rows=5)
    
    print("\n[Output] Synthetic Data Types:")
    print(synthetic.dtypes)
    print("\nSynthetic Data:")
    print(synthetic)
    
    # 3. Verify
    print("\n[Verification]")
    
    # Check 'age' (Should be int32 or int64)
    age_is_int = pd.api.types.is_integer_dtype(synthetic['age'])
    print(f"  ✓ 'age' is integer type: {age_is_int}")
    
    # Check 'salary' (Should be float)
    salary_is_float = pd.api.types.is_float_dtype(synthetic['salary'])
    print(f"  ✓ 'salary' is float type: {salary_is_float}")
    
    # Check 'years_experience' (Input was float 1.0, 2.0 -> Should be detected as integer)
    # This is a cool edge case: 1.0 is technically float but semantically integer
    exp_is_int = pd.api.types.is_integer_dtype(synthetic['years_experience'])
    is_exp_integer_pattern = profile.numerical_patterns['years_experience'].is_integer
    print(f"  ✓ 'years_experience' pattern detected as integer: {is_exp_integer_pattern}")
    print(f"  ✓ 'years_experience' output is integer type: {exp_is_int}")
    
    if age_is_int and salary_is_float and exp_is_int:
        print("\n✅ SUCCESS: Strict type preservation working correctly!")
    else:
        print("\n❌ FAILED: Types not preserved correctly.")

if __name__ == "__main__":
    test_strict_types()
