"""
Simple Web API Server for Universal Antigravity System
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime

from universal_antigravity import UniversalAntigravity

# Initialize FastAPI app
app = FastAPI(title="Universal Antigravity API", version="2.0.0")

# Global system instance
universal_system = UniversalAntigravity()


@app.get("/")
async def root():
    """Serve the web interface."""
    return FileResponse("web/index.html")


@app.post("/api/generate")
async def generate_data(request: dict):
    """Generate synthetic data from natural language prompt."""
    try:
        prompt = request.get('prompt', '')
        row_count = request.get('row_count', 100)
        
        result = universal_system.process_prompt(prompt, row_count=row_count)
        
        # Convert datetime objects to strings
        if 'generation_stats' in result:
            for key, value in result['generation_stats'].items():
                if isinstance(value, datetime):
                    result['generation_stats'][key] = value.isoformat()
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query_data(request: dict):
    """Query the generated data."""
    try:
        filters = request.get('filters')
        limit = request.get('limit', 100)
        
        rows = universal_system.query(filters=filters, limit=limit)
        
        # Convert datetime objects to strings
        for row in rows:
            for key, value in row.items():
                if isinstance(value, datetime):
                    row[key] = value.isoformat()
        
        return JSONResponse(content={"count": len(rows), "rows": rows})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/schema")
async def get_schema():
    """Get current schema information."""
    try:
        schema_info = universal_system.get_schema_info()
        
        if schema_info is None:
            return JSONResponse(content={"message": "No schema generated yet"})
        
        return JSONResponse(content=schema_info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_data():
    """Clear current data and reset system."""
    try:
        universal_system.clear()
        return JSONResponse(content={"success": True, "message": "System cleared successfully"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("Starting Universal Antigravity Web Server")
    print("="*60)
    print("Server: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
