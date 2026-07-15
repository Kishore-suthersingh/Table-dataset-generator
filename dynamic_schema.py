"""
Dynamic schema definition and parsing system.
Allows users to define any table schema through natural language or structured format.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class FieldType(Enum):
    """Supported field types."""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    ENUM = "enum"


@dataclass
class FieldConstraint:
    """Constraints for a field."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    enum_values: Optional[List[str]] = None
    required: bool = True
    unique: bool = False
    pattern: Optional[str] = None  # Regex pattern


@dataclass
class FieldDefinition:
    """Definition of a single field in the schema."""
    name: str
    field_type: FieldType
    description: str = ""
    constraints: Optional[FieldConstraint] = None
    sample_values: Optional[List[Any]] = None  # Sample values for generation
    
    def __repr__(self):
        return f"Field({self.name}: {self.field_type.value})"


@dataclass
class SchemaDefinition:
    """Complete schema definition for a table."""
    table_name: str
    description: str
    fields: List[FieldDefinition]
    relationships: Optional[Dict[str, str]] = None  # Field -> Related table
    
    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Get field definition by name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None
    
    def __repr__(self):
        return f"Schema({self.table_name}, {len(self.fields)} fields)"


class SchemaParser:
    """
    Parse schema definitions from natural language or structured format.
    
    Supports:
    - Natural language: "Create a Premier League table with team name, position, points, wins, losses"
    - JSON format: {...}
    - Python dict format
    """
    
    def __init__(self):
        self.type_keywords = {
            'integer': ['number', 'int', 'integer', 'count', 'position', 'rank'],
            'float': ['float', 'decimal', 'percentage', 'rate', 'ratio'],
            'string': ['name', 'text', 'string', 'description', 'city', 'country'],
            'datetime': ['date', 'time', 'datetime', 'timestamp', 'when'],
            'boolean': ['bool', 'boolean', 'flag', 'yes/no', 'true/false'],
        }
    
    def parse_natural_language(self, prompt: str) -> SchemaDefinition:
        """
        Parse schema from natural language description.
        
        Example: "Create a Premier League table with team name (string), position (integer), 
                  points (integer), wins (integer), losses (integer), goals scored (integer)"
        """
        # Extract table name
        table_name = self._extract_table_name(prompt)
        
        # Extract field definitions
        fields = self._extract_fields_from_nl(prompt)
        
        return SchemaDefinition(
            table_name=table_name,
            description=prompt,
            fields=fields
        )
    
    def parse_structured(self, schema_dict: Dict[str, Any]) -> SchemaDefinition:
        """
        Parse schema from structured dictionary.
        
        Example:
        {
            "table_name": "premier_league",
            "description": "Premier League standings",
            "fields": [
                {"name": "team_name", "type": "string", "max_length": 50},
                {"name": "position", "type": "integer", "min": 1, "max": 20},
                {"name": "points", "type": "integer", "min": 0}
            ]
        }
        """
        fields = []
        for field_spec in schema_dict.get('fields', []):
            field_type = FieldType(field_spec['type'])
            
            # Build constraints
            constraints = FieldConstraint(
                min_value=field_spec.get('min'),
                max_value=field_spec.get('max'),
                min_length=field_spec.get('min_length'),
                max_length=field_spec.get('max_length'),
                enum_values=field_spec.get('enum_values'),
                required=field_spec.get('required', True),
                unique=field_spec.get('unique', False),
                pattern=field_spec.get('pattern')
            )
            
            fields.append(FieldDefinition(
                name=field_spec['name'],
                field_type=field_type,
                description=field_spec.get('description', ''),
                constraints=constraints,
                sample_values=field_spec.get('sample_values')
            ))
        
        return SchemaDefinition(
            table_name=schema_dict['table_name'],
            description=schema_dict.get('description', ''),
            fields=fields,
            relationships=schema_dict.get('relationships')
        )
    
    def _extract_table_name(self, prompt: str) -> str:
        """Extract table name from natural language."""
        # Look for patterns like "Create a X table", "Generate X data"
        patterns = [
            r'create (?:a |an )?([a-z_ ]+) table',
            r'generate ([a-z_ ]+) (?:data|table)',
            r'(?:for|about) ([a-z_ ]+) (?:table|data)',
        ]
        
        prompt_lower = prompt.lower()
        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                table_name = match.group(1).strip().replace(' ', '_')
                return table_name
        
        return 'synthetic_table'
    
    def _extract_fields_from_nl(self, prompt: str) -> List[FieldDefinition]:
        """Extract field definitions from natural language."""
        fields = []
        
        # Look for "with field1, field2, field3" or "columns: field1, field2"
        field_section = None
        
        patterns = [
            r'with\s+(.+?)(?:\.|$)',
            r'columns?:\s*(.+?)(?:\.|$)',
            r'fields?:\s*(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                field_section = match.group(1)
                break
        
        if not field_section:
            # Default minimal schema
            return [
                FieldDefinition("id", FieldType.INTEGER, "Unique identifier"),
                FieldDefinition("name", FieldType.STRING, "Name or description"),
                FieldDefinition("value", FieldType.FLOAT, "Numeric value"),
            ]
        
        # Parse individual fields
        # Support formats: "team name (string)", "position (integer)", "points"
        field_pattern = r'([a-z_ ]+)(?:\s*\(([a-z]+)\))?'
        
        for match in re.finditer(field_pattern, field_section):
            field_name = match.group(1).strip().replace(' ', '_')
            explicit_type = match.group(2)
            
            # Determine field type
            if explicit_type:
                field_type = self._map_type_keyword(explicit_type)
            else:
                field_type = self._infer_type_from_name(field_name)
            
            # Create constraints based on type and name
            constraints = self._create_default_constraints(field_name, field_type)
            
            fields.append(FieldDefinition(
                name=field_name,
                field_type=field_type,
                description=f"Field: {field_name}",
                constraints=constraints
            ))
        
        return fields
    
    def _map_type_keyword(self, keyword: str) -> FieldType:
        """Map a keyword to field type."""
        keyword = keyword.lower()
        for field_type, keywords in self.type_keywords.items():
            if keyword in keywords or keyword in field_type:
                return FieldType(field_type)
        return FieldType.STRING  # Default
    
    def _infer_type_from_name(self, field_name: str) -> FieldType:
        """Infer field type from field name."""
        name_lower = field_name.lower()
        
        # Check for type keywords in field name
        for field_type, keywords in self.type_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return FieldType(field_type)
        
        # **FIX: Better detection for numeric fields**
        # Price-related fields should be float
        if any(word in name_lower for word in ['price', 'cost', 'amount', 'salary', 'fee', 'rate', 'gpa']):
            return FieldType.FLOAT
        
        # Volume and cap fields should be integer
        if any(word in name_lower for word in ['volume', 'cap', 'circulation', 'supply']):
            return FieldType.INTEGER
        
        # Specific field name mappings
        if any(word in name_lower for word in ['id', 'position', 'rank', 'count']):
            return FieldType.INTEGER
        elif any(word in name_lower for word in ['score', 'point', 'goal', 'win', 'loss', 'draw', 'played', 'age']):
            return FieldType.INTEGER
        elif any(word in name_lower for word in ['name', 'city', 'team', 'player', 'stadium', 'product', 'customer', 'student']):
            return FieldType.STRING
        elif any(word in name_lower for word in ['date', 'time', 'created', 'updated', 'hired', 'admission']):
            return FieldType.DATETIME
        
        return FieldType.STRING  # Default
    
    def _create_default_constraints(self, field_name: str, field_type: FieldType) -> FieldConstraint:
        """Create sensible default constraints based on field name and type."""
        constraints = FieldConstraint()
        
        name_lower = field_name.lower()
        
        if field_type == FieldType.INTEGER:
            if 'position' in name_lower or 'rank' in name_lower:
                constraints.min_value = 1
                constraints.max_value = 100
            elif any(word in name_lower for word in ['point', 'score', 'goal']):
                constraints.min_value = 0
                constraints.max_value = 200
            elif any(word in name_lower for word in ['win', 'loss', 'draw', 'played']):
                constraints.min_value = 0
                constraints.max_value = 50
        
        elif field_type == FieldType.STRING:
            if 'name' in name_lower:
                constraints.min_length = 2
                constraints.max_length = 50
            else:
                constraints.max_length = 255
        
        elif field_type == FieldType.FLOAT:
            constraints.min_value = 0.0
            constraints.max_value = 100.0
        
        return constraints


# Example usage
if __name__ == "__main__":
    parser = SchemaParser()
    
    # Test natural language parsing
    prompt = "Create a Premier League table with team name, position, played, won, drawn, lost, goals for, goals against, goal difference, points"
    schema = parser.parse_natural_language(prompt)
    
    print(f"Schema: {schema}")
    print(f"Fields ({len(schema.fields)}):")
    for field in schema.fields:
        print(f"  - {field}")
    
    # Test structured parsing
    structured = {
        "table_name": "sales_data",
        "description": "Sales transactions",
        "fields": [
            {"name": "transaction_id", "type": "integer", "unique": True},
            {"name": "product_name", "type": "string", "max_length": 100},
            {"name": "quantity", "type": "integer", "min": 1, "max": 1000},
            {"name": "price", "type": "float", "min": 0.0},
            {"name": "date", "type": "datetime"},
        ]
    }
    
    schema2 = parser.parse_structured(structured)
    print(f"\nStructured Schema: {schema2}")
    print(f"Fields ({len(schema2.fields)}):")
    for field in schema2.fields:
        print(f"  - {field}")
