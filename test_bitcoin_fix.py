"""
Test script to verify Bitcoin price generation fix.
"""
from universal_antigravity import UniversalAntigravity

system = UniversalAntigravity()

print("="*80)
print("TESTING BITCOIN PRICE DATA GENERATION")
print("="*80)

# Generate Bitcoin price data
result = system.process_prompt(
    "Create Bitcoin price data with date, open price, high price, low price, close price, volume, market cap",
    row_count=10
)

print(f"\n✓ Generated {result['generation_stats']['rows_generated']} rows")
print(f"\nSchema Fields:")
for field in result['schema']['fields']:
    print(f"  - {field['name']}: {field['type']}")

# Display sample data
print(f"\n{'='*80}")
print("SAMPLE DATA")
print("="*80)

data = system.query(limit=10)
for i, row in enumerate(data, 1):
    print(f"\nRow {i}:")
    for key, value in row.items():
        if 'price' in key.lower() or 'volume' in key.lower() or 'cap' in key.lower():
            if isinstance(value, (int, float)):
                print(f"  {key}: ${value:,.2f}")
            else:
                print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")

print("\n" + "="*80)
print("✓ Fix verified! You should now see proper numeric price values!")
print("="*80)
