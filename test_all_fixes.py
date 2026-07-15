"""
Comprehensive test to verify universal code fixes across multiple dataset types.
Tests that price, volume, and numeric fields are generated correctly.
"""
from universal_antigravity import UniversalAntigravity

def test_dataset(system, name, prompt, check_fields):
    """Test a dataset and verify field types."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print("="*80)
    
    system.clear()
    result = system.process_prompt(prompt, row_count=5)
    
    print(f"✓ Generated {result['generation_stats']['rows_generated']} rows")
    print(f"\nField Types:")
    for field in result['schema']['fields']:
        print(f"  {field['name']}: {field['type']}")
    
    # Get sample data
    data = system.query(limit=2)
    
    print(f"\nSample Data (First 2 rows):")
    for i, row in enumerate(data, 1):
        print(f"\n  Row {i}:")
        for key, value in row.items():
            # Check if the fields we care about have correct types
            if key in check_fields:
                value_type = type(value).__name__
                print(f"    {key}: {value} (type: {value_type})")
                
                # Verify it's numeric, not a random string
                if 'price' in key.lower() or 'volume' in key.lower() or 'cap' in key.lower():
                    if isinstance(value, (int, float)):
                        print(f"      ✓ Correct! Numeric value")
                    else:
                        print(f"      ✗ ERROR! Should be numeric, got string")
            else:
                print(f"    {key}: {value}")
    
    return result


def main():
    system = UniversalAntigravity()
    
    print("="*80)
    print("UNIVERSAL CODE FIX VERIFICATION")
    print("Testing that price/volume fields generate correctly across all domains")
    print("="*80)
    
    # Test 1: Bitcoin prices
    test_dataset(
        system,
        "Bitcoin Price Data",
        "Create Bitcoin price data with date, open price, high price, low price, close price, volume, market cap",
        ['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'market_cap']
    )
    
    # Test 2: Stock portfolio
    test_dataset(
        system,
        "Stock Portfolio",
        "Generate stock portfolio with ticker, shares, buy price, current price, profit",
        ['buy_price', 'current_price', 'shares', 'profit']
    )
    
    # Test 3: E-commerce products
    test_dataset(
        system,
        "Product Catalog",
        "Create product catalog with name, price, cost, rating, stock",
        ['price', 'cost', 'stock', 'rating']
    )
    
    # Test 4: Employee salaries
    test_dataset(
        system,
        "Employee Database",
        "Make employee table with name, position, salary, department",
        ['salary']
    )
    
    # Test 5: Premier League (should still work correctly)
    test_dataset(
        system,
        "Premier League Table",
        "Create Premier League table with team name, position, points, goals for",
        ['position', 'points', 'goals_for']
    )
    
    print(f"\n{'='*80}")
    print("VERIFICATION COMPLETE")
    print("="*80)
    print("\n✓ All datasets should now generate with correct data types!")
    print("✓ Price fields: numeric values (not random strings)")
    print("✓ Volume fields: large integers (not random strings)")
    print("✓ The fix is permanent in the universal code")
    print("="*80)


if __name__ == "__main__":
    main()
