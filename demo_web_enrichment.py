"""
Demo: Web Enrichment Feature
Shows how web enrichment improves synthetic data generation
"""
import pandas as pd
from universal_antigravity import UniversalAntigravity


def demo_web_enrichment():
    """Demonstrate web enrichment with Premier League example."""
    
    print("="*80)
    print("WEB ENRICHMENT DEMO")
    print("="*80)
    print("\nThis demo shows how web enrichment expands your sample dataset")
    print("with reference data to create more diverse synthetic data.")
    
    # Create a small sample with only 3 teams
    sample = pd.DataFrame({
        'team_name': ['Arsenal', 'Man City', 'Liverpool'],
        'position': [1, 2, 3],
        'points': [68, 65, 63]
    })
    
    sample.to_csv('sample_small_pl.csv', index=False)
    
    print(f"\n{'='*80}")
    print("ORIGINAL SAMPLE (3 teams only)")
    print("="*80)
    print(sample)
    
    system = UniversalAntigravity()
    
    # Test 1: WITHOUT web enrichment
    print(f"\n\n{'='*80}")
    print("TEST 1: WITHOUT WEB ENRICHMENT")
    print("="*80)
    
    result1 = system.process_from_sample('sample_small_pl.csv', n_rows=10, use_web_enrichment=False)
    
    data1 = system.query(limit=10)
    teams_generated_1 = set([row['team_name'] for row in data1])
    
    print(f"\n✓ Generated {len(data1)} rows")
    print(f"✓ Unique teams in output: {len(teams_generated_1)}")
    print(f"✓ Teams: {teams_generated_1}")
    print("\n⚠️ Limited to original 3 teams only!")
    
    # Test 2: WITH web enrichment
    print(f"\n\n{'='*80}")
    print("TEST 2: WITH WEB ENRICHMENT")
    print("="*80)
    
    system.clear()
    result2 = system.process_from_sample('sample_small_pl.csv', n_rows=20, use_web_enrichment=True)
    
    data2 = system.query(limit=20)
    teams_generated_2 = set([row['team_name'] for row in data2])
    
    print(f"\n✓ Generated {len(data2)} rows")
    print(f"✓ Unique teams in output: {len(teams_generated_2)}")
    print(f"✓ Teams: {teams_generated_2}")
    
    if 'enrichment_info' in result2:
        print("\n📊 Enrichment Stats:")
        print(f"  Original rows: {result2['enrichment_info']['original_rows']}")
        print(f"  Enriched rows: {result2['enrichment_info']['enriched_rows']}")
        print(f"  Added rows: {result2['enrichment_info']['added_rows']}")
        print(f"  Reference sources: {result2['enrichment_info']['reference_sources']}")
    
    print("\n✅ Enriched with full Premier League team list (20 teams)!")
    
    # Show sample output
    print(f"\n{'='*80}")
    print("SAMPLE ENRICHED OUTPUT")
    print("="*80)
    
    sample_df = pd.DataFrame(data2[:10])
    print(sample_df[['team_name', 'position', 'points']])
    
    # Export
    system.export_to_csv('enriched_output.csv')
    
    # Summary
    print(f"\n\n{'='*80}")
    print("COMPARISON SUMMARY")
    print("="*80)
    
    print(f"\nWithout Web Enrichment:")
    print(f"  Input: 3 teams → Output: {len(teams_generated_1)} unique teams")
    
    print(f"\nWith Web Enrichment:")
    print(f"  Input: 3 teams → Output: {len(teams_generated_2)} unique teams")
    
    improvement = ((len(teams_generated_2) - len(teams_generated_1)) / len(teams_generated_1)) * 100
    print(f"\n📈 Improvement: +{improvement:.0f}% more diverse data!")
    
    print("\n✅ Web enrichment makes synthetic data more realistic!")
    print("="*80)


if __name__ == "__main__":
    demo_web_enrichment()
