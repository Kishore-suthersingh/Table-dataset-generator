"""
Simple HTTP Server with Pattern-Based Generation Support
Enhanced to handle file uploads for pattern-based generation
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from urllib.parse import parse_qs
import os
from datetime import datetime
import cgi
import tempfile

from universal_antigravity import UniversalAntigravity

# Global system instance
universal_system = UniversalAntigravity()

# Store uploaded files temporarily
uploaded_files = {}


class AntigravityHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for Antigravity API."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            # Serve the web interface
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('web/index.html', 'rb') as f:
                self.wfile.write(f.read())
        
        elif self.path == '/api/health':
            # Health check
            self.send_json_response({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "modes": ["prompt", "pattern"]
            })
        
        elif self.path == '/api/schema':
            # Get schema info
            schema_info = universal_system.get_schema_info()
            if schema_info is None:
                self.send_json_response({"message": "No schema generated yet"})
            else:
                self.send_json_response(schema_info)
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        
        if self.path == '/api/upload':
            # Handle file upload
            try:
                # Parse multipart form data
                content_type = self.headers.get('Content-Type')
                if 'multipart/form-data' in content_type:
                    # Get boundary
                    boundary = content_type.split('boundary=')[1].encode()
                    
                    # Read the full request body
                    body = self.rfile.read(content_length)
                    
                    # Parse to find file data
                    parts = body.split(b'--' + boundary)
                    for part in parts:
                        if b'Content-Disposition' in part and b'filename=' in part:
                            # Extract filename
                            filename_start = part.find(b'filename="') + 10
                            filename_end = part.find(b'"', filename_start)
                            filename = part[filename_start:filename_end].decode()
                            
                            # Extract file content
                            file_data_start = part.find(b'\r\n\r\n') + 4
                            file_data = part[file_data_start:-2]  # Remove trailing \r\n
                            
                            # Save to temp file
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                            temp_file.write(file_data)
                            temp_file.close()
                            
                            file_id = f"upload_{len(uploaded_files) + 1}"
                            uploaded_files[file_id] = {
                                'path': temp_file.name,
                                'original_name': filename,
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            
                            self.send_json_response({
                                'success': True,
                                'file_id': file_id,
                                'filename': filename
                            })
                            return
                
                self.send_json_response({'error': 'No file found in request'}, status=400)
            
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        
        elif self.path == '/api/generate_from_sample':
            # Generate from uploaded sample
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                file_id = data.get('file_id')
                n_rows = data.get('n_rows', 100)
                use_web = data.get('use_web_enrichment', False)  # NEW: Web enrichment toggle
                
                if file_id not in uploaded_files:
                    self.send_json_response({'error': 'File not found'}, status=404)
                    return
                
                file_path = uploaded_files[file_id]['path']
                
                # Generate using pattern-based method with optional web enrichment
                result = universal_system.process_from_sample(file_path, n_rows, use_web_enrichment=use_web)
                
                # Convert datetime objects
                for key, value in result.get('generation_stats', {}).items():
                    if isinstance(value, datetime):
                        result['generation_stats'][key] = value.isoformat()
                
                self.send_json_response(result)
            
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        
        elif self.path == '/api/generate':
            # Generate from prompt (existing method)
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                prompt = data.get('prompt', '')
                row_count = data.get('row_count', 100)
                
                result = universal_system.process_prompt(prompt, row_count=row_count)
                
                # Convert datetime objects
                if 'generation_stats' in result:
                    for key, value in result['generation_stats'].items():
                        if isinstance(value, datetime):
                            result['generation_stats'][key] = value.isoformat()
                
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        
        elif self.path == '/api/query':
            # Query data
            try:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                filters = data.get('filters')
                limit = data.get('limit', 100)
                
                rows = universal_system.query(filters=filters, limit=limit)
                
                # Convert datetime objects
                for row in rows:
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            row[key] = value.isoformat()
                
                self.send_json_response({"count": len(rows), "rows": rows})
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        
        elif self.path == '/api/clear':
            # Clear data
            try:
                universal_system.clear()
                self.send_json_response({"success": True, "message": "System cleared"})
            except Exception as e:
                self.send_json_response({'error': str(e)}, status=500)
        
        else:
            self.send_error(404)
    
    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log message."""
        return  # Suppress default logging


if __name__ == "__main__":
    PORT = 8000
    
    print("="*60)
    print("Universal Antigravity Web Server v2.0")
    print("="*60)
    print(f"Server running at: http://localhost:{PORT}")
    print("\nSupported Modes:")
    print("  1. Natural Language Prompts")
    print("  2. Pattern-Based (Upload Sample CSV)")
    print("\nPress Ctrl+C to stop")
    print("="*60)
    
    server = HTTPServer(('0.0.0.0', PORT), AntigravityHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()
        
        # Cleanup temp files
        for file_info in uploaded_files.values():
            try:
                os.remove(file_info['path'])
            except:
                pass
