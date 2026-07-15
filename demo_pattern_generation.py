"""
Demo: Pattern-Based Data Generation
Shows how to generate realistic synthetic data from sample datasets
"""
import pandas as pd
from universal_antigravity import UniversalAntigravity


def demo_pattern_generation():
    """Demonstrate pattern-based generation with various datasets."""
    
    system = UniversalAntigravity()
    
    print("="*80)
    print("PATTERN-BASED DATA GENERATION DEMO")
    print("="*80)
    print("\nThis demo shows how the system learns patterns from small samples")
    print("and generates larger synthetic datasets matching those patterns.")
    
    # Demo 1: Premier League Table
    print("\n" + "="*80)
    print("DEMO 1: Premier League Standings")
    print("="*80)
    
    # Create sample data
    sample_pl = pd.DataFrame({
        'team_name': ['Arsenal', 'Man City', 'Liverpool', 'Chelsea', 'Tottenham', 'Newcastle'],
        'position': [1, 2, 3, 4, 5, 6],
        'played': [20, 20, 20, 20, 20, 20],
        'points': [53, 51, 48, 43, 40, 38],
        'wins': [17, 16, 15, 13, 12, 11],
        'losses': [2, 3, 4, 6, 7, 8]
    })
    
    sample_pl.to_csv('sample_pl.csv', index=False)
    
    print(f"\nOriginal Sample ({len(sample_pl)} rows):")
    print(sample_pl)
    
    # Generate synthetic data
    result = system.process_from_sample('sample_pl.csv', n_rows=20)
    
    print(f"\n✓ Generated {result['generation_stats']['rows_generated']} synthetic rows")
    print(f"✓ Quality score: {result['sample_info']['quality_score']:.1f}/100")
    print(f"✓ Patterns learned: {result['patterns_learned']['patterns']}")
    
    # Show correlations
    if 'strong_correlations' in result['patterns_learned']:
        print("\nStrong Correlations Detected:")
        for col1, col2, corr in result['patterns_learned']['strong_correlations']:
            print(f"  {col1} ↔ {col2}: {corr:.3f}")
    
    # Display generated data
    synthetic_data = system.query(limit=10)
    synthetic_df = pd.DataFrame(synthetic_data)
    print(f"\nGenerated Data (first 10 rows):")
    print(synthetic_df)
    
    # Export
    system.export_to_csv('synthetic_pl.csv')
    
    # Demo 2: Stock Prices
    print("\n\n" + "="*80)
    print("DEMO 2: Stock Price History")
    print("="*80)
    
    sample_stocks = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'ticker': 'AAPL',
        'open': [180.5, 182.3, 181.9, 183.1, 184.5, 183.8, 185.2, 186.1, 185.7, 187.3],
        'high': [182.1, 183.5, 183.2, 184.8, 185.9, 185.1, 186.8, 187.5, 187.2, 188.9],
        'low': [179.8, 181.5, 181.2, 182.5, 183.9, 183.2, 184.6, 185.4, 185.1, 186.7],
        'close': [181.8, 182.9, 182.5, 184.2, 185.3, 184.5, 186.1, 186.8, 186.5, 188.1],
        'volume': [50000000, 52000000, 48000000, 51000000, 53000000, 49000000, 54000000, 55000000, 52000000, 56000000]
    })
    
    sample_stocks.to_csv('sample_stocks.csv', index=False)
    
    print(f"\nOriginal Sample ({len(sample_stocks)} rows):")
    print(sample_stocks.head())
    
    system.clear()
    result2 = system.process_from_sample('sample_stocks.csv', n_rows=30)
    
    print(f"\n✓ Generated {result2['generation_stats']['rows_generated']} synthetic price records")
    print(f"✓ Speed: {result2['generation_stats']['rows_per_second']:.0f} rows/second")
    
    # Show sample
    stock_data = system.query(limit=5)
    stock_df = pd.DataFrame(stock_data)
    print(f"\nGenerated Data (first 5 rows):")
    print(stock_df)
    
    # Export
    system.export_to_csv('synthetic_stocks.csv')
    
    # Summary
    print("\n\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\n✅ Pattern-based generation is working!")
    print("\nKey Features Demonstrated:")
    print("  1. ✓ Load sample CSV datasets")
    print("  2. ✓ Analyze statistical patterns (distributions, correlations)")
    print("  3. ✓ Generate synthetic data matching patterns")
    print("  4. ✓ Maintain relationships between columns")
    print("  5. ✓ Scale up: 6 rows → 20 rows, 10 rows → 30 rows")
    print("\nGenerated Files:")
    print("  - synthetic_pl.csv")
    print("  - synthetic_stocks.csv")
    print("="*80)


if __name__ == "__main__":
    demo_pattern_generation()
