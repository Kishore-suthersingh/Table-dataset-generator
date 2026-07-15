"""
Universal data generator that works with dynamic schemas.
Generates synthetic data for any user-defined table structure.
"""
from typing import Any, List, Dict, Generator
from datetime import datetime, timedelta
import random
import string
from dynamic_schema import SchemaDefinition, FieldDefinition, FieldType, FieldConstraint


class UniversalDataGenerator:
    """
    Generic data generator that works with any schema definition.
    Replaces domain-specific generators with a universal approach.
    """
    
    def __init__(self, schema: SchemaDefinition):
        self.schema = schema
        self.generated_unique_values: Dict[str, set] = {}  # Track unique values per field
    
    def generate_row(self) -> Dict[str, Any]:
        """Generate a single row conforming to the schema."""
        row = {}
        
        for field in self.schema.fields:
            value = self._generate_field_value(field)
            row[field.name] = value
        
        return row
    
    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generate multiple rows."""
        return [self.generate_row() for _ in range(count)]
    
    def generate_stream(self, count: int) -> Generator[Dict[str, Any], None, None]:
        """Generate rows as a stream."""
        for _ in range(count):
            yield self.generate_row()
    
    def _generate_field_value(self, field: FieldDefinition) -> Any:
        """Generate a value for a specific field."""
        # Use sample values if provided
        if field.sample_values:
            return random.choice(field.sample_values)
        
        # Generate based on field type
        if field.field_type == FieldType.INTEGER:
            return self._generate_integer(field)
        elif field.field_type == FieldType.FLOAT:
            return self._generate_float(field)
        elif field.field_type == FieldType.STRING:
            return self._generate_string(field)
        elif field.field_type == FieldType.DATETIME:
            return self._generate_datetime(field)
        elif field.field_type == FieldType.BOOLEAN:
            return self._generate_boolean(field)
        elif field.field_type == FieldType.ENUM:
            return self._generate_enum(field)
        else:
            return None
    
    def _generate_integer(self, field: FieldDefinition) -> int:
        """Generate integer value."""
        constraints = field.constraints or FieldConstraint()
        
        min_val = int(constraints.min_value) if constraints.min_value is not None else 0
        max_val = int(constraints.max_value) if constraints.max_value is not None else 1000000
        
        value = random.randint(min_val, max_val)
        
        # Handle uniqueness
        if constraints.unique:
            value = self._ensure_unique(field.name, value, lambda: random.randint(min_val, max_val))
        
        return value
    
    def _generate_float(self, field: FieldDefinition) -> float:
        """Generate float value."""
        constraints = field.constraints or FieldConstraint()
        
        min_val = constraints.min_value if constraints.min_value is not None else 0.0
        max_val = constraints.max_value if constraints.max_value is not None else 1000000.0
        
        value = random.uniform(min_val, max_val)
        return round(value, 2)
    
    def _generate_string(self, field: FieldDefinition) -> str:
        """Generate string value based on field name patterns."""
        constraints = field.constraints or FieldConstraint()
        name_lower = field.name.lower()
        
        # **FIX: Detect numeric fields that were incorrectly typed as string**
        # Price fields should be float, not string
        if any(word in name_lower for word in ['price', 'cost', 'amount', 'salary', 'fee', 'rate']):
            # Generate numeric price instead of string
            if 'bitcoin' in name_lower or 'btc' in name_lower or 'crypto' in name_lower:
                # Bitcoin prices: $20,000 - $100,000
                return str(round(random.uniform(20000, 100000), 2))
            elif 'stock' in name_lower:
                # Stock prices: $10 - $500
                return str(round(random.uniform(10, 500), 2))
            else:
                # Generic prices: $10 - $10,000
                return str(round(random.uniform(10, 10000), 2))
        
        # Volume and market cap should be large integers
        if any(word in name_lower for word in ['volume', 'market_cap', 'marketcap', 'circulation']):
            if 'bitcoin' in name_lower or 'btc' in name_lower or 'crypto' in name_lower:
                # Crypto volume/market cap: millions to billions
                return str(random.randint(1000000000, 100000000000))
            else:
                # Generic volume
                return str(random.randint(100000, 10000000))
        
        # Special handling for common field names
        if 'team' in name_lower and 'name' in name_lower:
            teams = [
                "Manchester United", "Liverpool", "Chelsea", "Arsenal", "Manchester City",
                "Tottenham", "Newcastle", "Brighton", "Aston Villa", "West Ham",
                "Crystal Palace", "Wolves", "Everton", "Fulham", "Brentford",
                "Nottingham Forest", "Bournemouth", "Leicester City", "Leeds United", "Southampton"
            ]
            return random.choice(teams)
        
        elif 'player' in name_lower and 'name' in name_lower:
            first_names = ["James", "John", "David", "Michael", "Robert", "Mohamed", "Kevin", "Harry", "Bruno", "Erling"]
            last_names = ["Smith", "Johnson", "Williams", "Salah", "Kane", "Fernandes", "Haaland", "De Bruyne", "Son", "Saka"]
            return f"{random.choice(first_names)} {random.choice(last_names)}"
        
        elif any(word in name_lower for word in ['city', 'location', 'place']):
            cities = ["London", "Manchester", "Liverpool", "Birmingham", "Leeds", "Newcastle", "Southampton"]
            return random.choice(cities)
        
        elif 'stadium' in name_lower:
            stadiums = ["Old Trafford", "Anfield", "Emirates Stadium", "Etihad Stadium", "Stamford Bridge", "Tottenham Hotspur Stadium"]
            return random.choice(stadiums)
        
        elif 'email' in name_lower:
            domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            return f"{username}@{random.choice(domains)}"
        
        elif 'phone' in name_lower:
            return f"+44 {random.randint(1000000000, 9999999999)}"
        
        elif 'url' in name_lower or 'website' in name_lower:
            return f"https://www.{random.choice(['example', 'site', 'web'])}.com"
        
        elif 'product' in name_lower and 'name' in name_lower:
            products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam", "Desk", "Chair"]
            return random.choice(products)
        
        elif 'customer' in name_lower and 'name' in name_lower:
            first = random.choice(["John", "Jane", "Bob", "Alice", "Mike", "Sarah"])
            last = random.choice(["Smith", "Jones", "Brown", "Davis", "Wilson"])
            return f"{first} {last}"
        
        elif 'student' in name_lower and 'name' in name_lower:
            first = random.choice(["Emily", "James", "Sophia", "Oliver", "Emma", "Noah"])
            last = random.choice(["Johnson", "Williams", "Brown", "Davis", "Miller"])
            return f"{first} {last}"
        
        elif 'major' in name_lower or 'department' in name_lower:
            majors = ["Computer Science", "Engineering", "Business", "Mathematics", "Physics", "Biology", "English"]
            return random.choice(majors)
        
        elif 'category' in name_lower or 'type' in name_lower:
            categories = ["Electronics", "Clothing", "Food", "Books", "Sports", "Home"]
            return random.choice(categories)
        
        else:
            # Generic string generation
            max_len = constraints.max_length or 50
            min_len = constraints.min_length or 5
            
            length = random.randint(min_len, min(max_len, 50))
            return ''.join(random.choices(string.ascii_letters + ' ', k=length)).strip()
    
    def _generate_datetime(self, field: FieldDefinition) -> datetime:
        """Generate datetime value."""
        # Default to last 365 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        delta = (end_date - start_date).total_seconds()
        random_seconds = random.uniform(0, delta)
        
        return start_date + timedelta(seconds=random_seconds)
    
    def _generate_boolean(self, field: FieldDefinition) -> bool:
        """Generate boolean value."""
        return random.choice([True, False])
    
    def _generate_enum(self, field: FieldDefinition) -> str:
        """Generate enum value."""
        if field.constraints and field.constraints.enum_values:
            return random.choice(field.constraints.enum_values)
        return "default"
    
    def _ensure_unique(self, field_name: str, value: Any, generator) -> Any:
        """Ensure value is unique for this field."""
        if field_name not in self.generated_unique_values:
            self.generated_unique_values[field_name] = set()
        
        # Try to generate unique value (max 100 attempts)
        for _ in range(100):
            if value not in self.generated_unique_values[field_name]:
                self.generated_unique_values[field_name].add(value)
                return value
            value = generator()
        
        # Fallback: append random suffix
        while value in self.generated_unique_values[field_name]:
            value = f"{value}_{random.randint(1000, 9999)}"
        
        self.generated_unique_values[field_name].add(value)
        return value


# Example usage
if __name__ == "__main__":
    from dynamic_schema import SchemaParser
    
    # Parse schema from natural language
    parser = SchemaParser()
    schema = parser.parse_natural_language(
        "Create a Premier League table with team name, position, played, won, drawn, lost, goals for, goals against, goal difference, points"
    )
    
    # Generate data
    generator = UniversalDataGenerator(schema)
    
    print("Generated Premier League Data:")
    print("="*80)
    for i, row in enumerate(generator.generate_stream(5), 1):
        print(f"\nRow {i}:")
        for key, value in row.items():
            print(f"  {key}: {value}")
