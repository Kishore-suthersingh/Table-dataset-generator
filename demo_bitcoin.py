"""
Bitcoin Price Dataset Generator
Demonstrates universal Antigravity system for cryptocurrency data.
"""
from universal_antigravity import UniversalAntigravity
from datetime import datetime


def generate_bitcoin_prices():
    """Generate synthetic Bitcoin price dataset."""
    
    print("="*80)
    print("BITCOIN PRICE DATASET GENERATOR")
    print("="*80)
    
    system = UniversalAntigravity()
    
    # Generate Bitcoin price data with natural language prompt
    prompt = """
    Create a Bitcoin price table with 
    date, open price, high price, low price, close price, 
    volume, market cap
    """
    
    print("\nGenerating Bitcoin price data...")
    print(f"Prompt: {prompt.strip()}")
    
    result = system.process_prompt(prompt, row_count=100)
    
    # Display results
    print(f"\n{'='*80}")
    print("GENERATION RESULTS")
    print("="*80)
    print(f"✓ Table: {result['schema']['table_name']}")
    print(f"✓ Generated: {result['generation_stats']['rows_generated']} price records")
    print(f"✓ Speed: {result['generation_stats']['rows_per_second']:.0f} rows/second")
    print(f"✓ Duration: {result['generation_stats']['duration_seconds']:.3f} seconds")
    
    # Display schema
    print(f"\nSchema Fields:")
    for field in result['schema']['fields']:
        print(f"  - {field['name']} ({field['type']})")
    
    # Get all data and sort by date
    all_data = system.query(limit=100)
    
    # Sort by date (most recent first)
    sorted_data = sorted(all_data, key=lambda x: x.get('date', datetime.min) if isinstance(x.get('date'), datetime) else datetime.min, reverse=True)
    
    # Display sample data
    print(f"\n{'='*80}")
    print("SAMPLE BITCOIN PRICES (Most Recent 10)")
    print("="*80)
    print(f"{'Date':<20} {'Open':<12} {'High':<12} {'Low':<12} {'Close':<12} {'Volume':<15}")
    print("-"*80)
    
    for i, record in enumerate(sorted_data[:10]):
        date_str = record.get('date').strftime('%Y-%m-%d %H:%M') if isinstance(record.get('date'), datetime) else str(record.get('date', 'N/A'))[:16]
        open_price = f"${record.get('open_price', 0):,.2f}" if isinstance(record.get('open_price'), (int, float)) else str(record.get('open_price', 'N/A'))
        high_price = f"${record.get('high_price', 0):,.2f}" if isinstance(record.get('high_price'), (int, float)) else str(record.get('high_price', 'N/A'))
        low_price = f"${record.get('low_price', 0):,.2f}" if isinstance(record.get('low_price'), (int, float)) else str(record.get('low_price', 'N/A'))
        close_price = f"${record.get('close_price', 0):,.2f}" if isinstance(record.get('close_price'), (int, float)) else str(record.get('close_price', 'N/A'))
        volume = f"{record.get('volume', 0):,.0f}" if isinstance(record.get('volume'), (int, float)) else str(record.get('volume', 'N/A'))
        
        print(f"{date_str:<20} {open_price:<12} {high_price:<12} {low_price:<12} {close_price:<12} {volume:<15}")
    
    print("="*80)
    
    # Calculate some statistics
    print(f"\n{'='*80}")
    print("PRICE STATISTICS")
    print("="*80)
    
    prices = [r.get('close_price', 0) for r in all_data if isinstance(r.get('close_price'), (int, float))]
    volumes = [r.get('volume', 0) for r in all_data if isinstance(r.get('volume'), (int, float))]
    
    if prices:
        print(f"Close Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}")
        print(f"Average Close Price: ${sum(prices)/len(prices):,.2f}")
    
    if volumes:
        print(f"Average Volume: {sum(volumes)/len(volumes):,.0f}")
        print(f"Total Volume: {sum(volumes):,.0f}")
    
    # Export to CSV
    print(f"\n{'='*80}")
    filename = "bitcoin_prices.csv"
    system.export_to_csv(filename)
    print(f"✓ Data exported to: {filename}")
    print("="*80)
    
    return system


if __name__ == "__main__":
    system = generate_bitcoin_prices()
    
    print("\n" + "="*80)
    print("SUCCESS!")
    print("="*80)
    print("\nThe universal Antigravity system can generate cryptocurrency data too!")
    print("\nTry other prompts:")
    print("  - 'Create Ethereum price history with date, price, gas fees'")
    print("  - 'Generate crypto wallet transactions with address, amount, timestamp'")
    print("  - 'Make NFT marketplace data with name, price, owner, collection'")
    print("="*80)
