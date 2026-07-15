# Antigravity Synthetic Data Generation System

A sophisticated multi-stage workflow system that generates realistic synthetic tabular data by combining live database context with user-specified anomaly patterns.

## Overview

Antigravity implements a 5-stage workflow:

1. **Intent Parsing** - Extract entities and anomaly patterns from natural language prompts
2. **Context Acquisition** - Analyze live database to understand current patterns
3. **Generation Loop (DNS-CD)** - Generate synthetic data using consistency distillation
4. **Real-Time Governance** - Validate and auto-correct generated data
5. **Deployment** - Store in queryable virtual table with streaming access

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Sample Data

```bash
python sample_data_generator.py
```

This creates:
- SQLite database (`antigravity.db`)
- 50 sample users
- 1000 traffic log entries

### 3. Run Standalone Demo

```bash
python antigravity_system.py
```

Example output:
```
[Stage 1] Parsing intent from prompt...
  Parsed: IntentContext(anomaly=ddos, duration=30m, mix_ratio=0.50)

[Stage 2] Acquiring live context...
  Live Vector: LiveStyleVector(rpm=41.7, latency=102.3ms, ip_diversity=0.98)

[Stage 3 & 4] Starting generation and validation...
  Generated 1000 rows...
  Generated 2000 rows...
  ...

[Stage 5] Generation complete!

GENERATION RESULTS
Generated: 3000 rows
Validated: 2985 rows
Corrected: 15 rows
```

### 4. Start API Server

```bash
uvicorn api_server:app --reload
```

Server runs at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Usage

### Generate Data (REST)

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Simulate a DDOS attack pattern mixed with normal traffic for 30 minutes",
    "export_to_db": false
  }'
```

### Query Virtual Table

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"status_code": 404},
    "limit": 10
  }'
```

### Get Statistics

```bash
curl http://localhost:8000/api/statistics
```

### Real-Time Streaming (WebSocket)

```python
import asyncio
import websockets
import json

async def stream_data():
    uri = "ws://localhost:8000/ws/stream"
    async with websockets.connect(uri) as websocket:
        # Send prompt
        await websocket.send(json.dumps({
            "prompt": "Generate SQL injection attempts for 15 minutes"
        }))
        
        # Receive streaming data
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'data':
                print(f"Row: {data['row']}")
            elif data.get('type') == 'complete':
                print(f"Complete! Total: {data['total_rows']}")
                break

asyncio.run(stream_data())
```

## Example Prompts

- `"Simulate a DDOS attack pattern on our traffic logs mixed with normal user behavior for the next 30 minutes."`
- `"Generate normal traffic for 1 hour"`
- `"Create SQL injection attempts on the /login endpoint for 15 minutes with 20% attack rate"`
- `"Generate traffic with 80% anomaly rate for 45 minutes"`

## Architecture

### Core Components

- **`config.py`** - Anomaly patterns, configurations
- **`database_models.py`** - SQLAlchemy ORM models
- **`utils.py`** - Helper functions for data generation
- **`intent_parser.py`** - NLP entity extraction
- **`context_encoder.py`** - Live data analysis
- **`dns_cd_engine.py`** - Core generation algorithm
- **`validator.py`** - Real-time governance
- **`virtual_table.py`** - In-memory queryable table
- **`antigravity_system.py`** - Main orchestrator
- **`api_server.py`** - FastAPI REST/WebSocket server

### Anomaly Patterns

The system includes built-in patterns:

- **DDOS** - High frequency, low IP diversity, concentrated endpoints
- **SQL Injection** - Malicious payloads targeting specific endpoints
- **Normal** - Baseline user behavior

Each pattern has configurable characteristics (frequency multipliers, error rates, etc.)

## Configuration

Edit `config.py` to customize:

- Database URL
- Generation rates (rows per minute)
- Anomaly pattern characteristics
- Sample data pools (endpoints, geo locations, etc.)

## Development

### Project Structure

```
d:/open lab 2/
├── antigravity_system.py      # Main orchestrator
├── api_server.py              # FastAPI server
├── config.py                  # Configuration
├── context_encoder.py         # Context acquisition
├── database_models.py         # ORM models
├── dns_cd_engine.py          # Generation engine
├── intent_parser.py          # Intent parsing
├── sample_data_generator.py  # Bootstrap script
├── utils.py                  # Utilities
├── validator.py              # Validation system
├── virtual_table.py          # Virtual table
├── requirements.txt          # Dependencies
├── antigravity.db            # SQLite database
└── README.md                 # This file
```

### Testing

Run the standalone demo to test all 5 stages:

```bash
python antigravity_system.py
```

Test intent parsing:

```bash
python intent_parser.py
```

## Performance

- **Generation Speed**: ~1000 rows/second
- **Validation Overhead**: <1ms per row
- **Memory**: Auto-expires after 100k rows in virtual table

## License

MIT License
