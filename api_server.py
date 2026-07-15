"""
FastAPI server for Antigravity system.
Provides REST API and WebSocket endpoints for data generation.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import json

from antigravity_system import AntigravitySystem
from database_models import init_database


# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    export_to_db: bool = False


class QueryRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None
    limit: int = 100


# Initialize FastAPI app
app = FastAPI(
    title="Antigravity API",
    description="Synthetic data generation API with real-time streaming",
    version="1.0.0"
)

# Global system instance
antigravity_system: Optional[AntigravitySystem] = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    global antigravity_system
    init_database()
    antigravity_system = AntigravitySystem()
    print("Antigravity system initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if antigravity_system:
        antigravity_system.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Antigravity API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/api/generate",
            "query": "/api/query",
            "statistics": "/api/statistics",
            "clear": "/api/clear",
            "stream": "/ws/stream",
        }
    }


@app.post("/api/generate")
async def generate_data(request: GenerateRequest):
    """
    Generate synthetic data from a prompt.
    
    Args:
        request: GenerateRequest with prompt and options
        
    Returns:
        Generation results and statistics
    """
    if not antigravity_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Process prompt through all 5 stages
        result = antigravity_system.process_prompt(request.prompt)
        
        # Optionally export to database
        if request.export_to_db and result['success']:
            exported_count = antigravity_system.export_to_database()
            result['exported_to_db'] = exported_count
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query_data(request: QueryRequest):
    """
    Query the virtual table.
    
    Args:
        request: QueryRequest with filters and limit
        
    Returns:
        Query results
    """
    if not antigravity_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        rows = antigravity_system.query_virtual_table(
            filters=request.filters,
            limit=request.limit
        )
        
        # Convert datetime objects to strings for JSON serialization
        for row in rows:
            if 'timestamp' in row and isinstance(row['timestamp'], datetime):
                row['timestamp'] = row['timestamp'].isoformat()
        
        return JSONResponse(content={
            "count": len(rows),
            "rows": rows
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """Get virtual table statistics."""
    if not antigravity_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        stats = antigravity_system.get_table_statistics()
        
        # Convert datetime objects
        if 'metadata' in stats:
            for key, value in stats['metadata'].items():
                if isinstance(value, datetime):
                    stats['metadata'][key] = value.isoformat()
        
        return JSONResponse(content=stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_table():
    """Clear all data from the virtual table."""
    if not antigravity_system:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        antigravity_system.clear_virtual_table()
        return JSONResponse(content={"success": True, "message": "Virtual table cleared"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming.
    Client sends a prompt, server streams generated rows.
    """
    await websocket.accept()
    
    try:
        # Receive prompt from client
        data = await websocket.receive_text()
        request_data = json.loads(data)
        prompt = request_data.get('prompt', '')
        
        if not prompt:
            await websocket.send_json({"error": "No prompt provided"})
            await websocket.close()
            return
        
        # Send acknowledgment
        await websocket.send_json({
            "status": "starting",
            "message": "Generation started"
        })
        
        # Parse intent and get context
        intent = antigravity_system.intent_parser.parse(prompt)
        live_vector = antigravity_system.context_encoder.compute_live_style_vector()
        
        # Stream generated data
        row_count = 0
        for generated_row in antigravity_system.generator.generate_stream(
            intent=intent,
            live_vector=live_vector,
            start_time=datetime.utcnow(),
            rows_per_minute=100
        ):
            # Validate
            validation_result = antigravity_system.validator.validate(generated_row)
            
            if validation_result.is_valid:
                # Insert to virtual table
                antigravity_system.virtual_table.insert(validation_result.row)
                
                # Send to client
                row_data = {
                    'timestamp': validation_result.row.timestamp.isoformat(),
                    'ip_address': validation_result.row.ip_address,
                    'endpoint': validation_result.row.endpoint,
                    'method': validation_result.row.method,
                    'status_code': validation_result.row.status_code,
                    'latency_ms': validation_result.row.latency_ms,
                }
                
                await websocket.send_json({
                    "type": "data",
                    "row": row_data
                })
                
                row_count += 1
                
                # Small delay to avoid overwhelming client
                if row_count % 10 == 0:
                    await asyncio.sleep(0.1)
        
        # Send completion message
        await websocket.send_json({
            "type": "complete",
            "total_rows": row_count
        })
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
