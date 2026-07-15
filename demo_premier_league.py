"""
Premier League Table Generator Demo
Demonstrates the universal schema-agnostic Antigravity system.
"""
from universal_antigravity import UniversalAntigravity


def demo_premier_league():
    """Generate a realistic Premier League standings table."""
    print("="*80)
    print("PREMIER LEAGUE TABLE GENERATOR")
    print("="*80)
    
    system = UniversalAntigravity()
    
    # Generate Premier League table
    prompt = """
    Create a Premier League table with 
    team name, position, played, won, drawn, lost, 
    goals for, goals against, goal difference, points
    """
    
    result = system.process_prompt(prompt, row_count=20)
    
    # Display results
    print(f"\n✓ Generated {result['generation_stats']['rows_generated']} Premier League team records")
    print(f"✓ Table: {result['schema']['table_name']}")
    print(f"✓ Speed: {result['generation_stats']['rows_per_second']:.0f} rows/second")
    
    # Get all data and sort by position
    all_data = system.query(limit=20)
    
    # Sort by position
    sorted_data = sorted(all_data, key=lambda x: x.get('position', 0))
    
    # Display as formatted table
    print(f"\n{'='*120}")
    print(f"{'Pos':<5} {'Team':<25} {'Played':<8} {'Won':<6} {'Drawn':<7} {'Lost':<6} {'GF':<6} {'GA':<6} {'GD':<6} {'Points':<8}")
    print("="*120)
    
    for team in sorted_data:
        print(f"{team.get('position', 0):<5} "
              f"{team.get('team_name', 'Unknown'):<25} "
              f"{team.get('played', 0):<8} "
              f"{team.get('won', 0):<6} "
              f"{team.get('drawn', 0):<7} "
              f"{team.get('lost', 0):<6} "
              f"{team.get('goals_for', 0):<6} "
              f"{team.get('goals_against', 0):<6} "
              f"{team.get('goal_difference', 0):<6} "
              f"{team.get('points', 0):<8}")
    
    print("="*120)
    
    # Export to CSV
    system.export_to_csv("premier_league_table.csv")
    print(f"\n✓ Exported to premier_league_table.csv")
    
    return system


def demo_custom_tables():
    """Demonstrate generating various custom tables."""
    system = UniversalAntigravity()
    
    examples = [
        {
            "name": "Student Records",
            "prompt": "Generate student records with student name, age, grade, GPA, major",
            "rows": 15
        },
        {
            "name": "Sales Transactions",
            "prompt": "Create sales data with product name, quantity, price, customer name, date",
            "rows": 10
        },
        {
            "name": "Employee Database",
            "prompt": "Make employee table with name, position, salary, department, hired date",
            "rows": 8
        }
    ]
    
    for example in examples:
        print(f"\n{'='*80}")
        print(f"{example['name'].upper()}")
        print("="*80)
        
        system.clear()
        result = system.process_prompt(example['prompt'], row_count=example['rows'])
        
        print(f"\n✓ Generated {result['generation_stats']['rows_generated']} records")
        print(f"✓ Fields: {', '.join([f['name'] for f in result['schema']['fields']])}")
        
        # Show sample
        sample = system.query(limit=3)
        print(f"\nSample data (first 3 rows):")
        for i, row in enumerate(sample, 1):
            print(f"  Row {i}: {dict(list(row.items())[:5])}...")  # Show first 5 fields
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    # Demo 1: Premier League table
    system = demo_premier_league()
    
    # Demo 2: Various custom tables
    demo_custom_tables()
    
    print(f"\n{'='*80}")
    print("ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nThe universal Antigravity system can generate synthetic data for ANY table!")
    print("Just describe your desired table structure in natural language.")
    print("\nExamples:")
    print("  - 'Create an e-commerce orders table with order ID, customer, product, quantity, total'")
    print("  - 'Generate hospital patient records with name, age, condition, admission date'")
    print("  - 'Make a movie database with title, director, year, rating, genre'")
    print("="*80)
