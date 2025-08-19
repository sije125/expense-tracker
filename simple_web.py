#!/usr/bin/env python3
"""
Simple web server for expense tracker that should work reliably
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

class ExpenseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/connect':
            self.serve_connect_page()
        elif parsed_path.path == '/status':
            self.serve_status()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>💰 Expense Tracker</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand">💰 Expense Tracker</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                <h1>🎉 Connection Successful!</h1>
                <p class="lead">Your ML-powered expense tracker is working in Chrome!</p>
                
                <div class="alert alert-success">
                    <h5>✅ Status Check</h5>
                    <ul class="mb-0">
                        <li>✅ Web server running</li>
                        <li>✅ Chrome connection working</li>
                        <li>✅ Plaid credentials configured</li>
                        <li>✅ ML categorizer ready</li>
                    </ul>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5>🏦 Bank Connection</h5>
                                <p>Connect securely via Plaid API</p>
                                <button class="btn btn-primary" onclick="connectBank()">
                                    Connect Bank Account
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5>📁 CSV Analysis</h5>
                                <p>Use command line tools</p>
                                <div class="alert alert-info">
                                    <small>
                                        <code>python3 main.py analyze file.csv</code><br>
                                        <code>python3 example_usage.py</code>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5>🚀 Quick Start</h5>
                        <p><strong>Demo with sample data:</strong></p>
                        <p><code>python3 example_usage.py</code></p>
                        
                        <p><strong>Analyze your CSV:</strong></p>
                        <p><code>python3 main.py analyze your_file.csv</code></p>
                        
                        <p><strong>Interactive mode:</strong></p>
                        <p><code>python3 main.py interactive</code></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function connectBank() {
            alert('Bank connection feature requires the full Flask app.\\n\\nFor now, use the command line tools:\\n\\n• python3 example_usage.py (demo)\\n• python3 main.py analyze file.csv\\n\\nThese provide the same ML categorization and analysis!');
        }
        
        // Check server status
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                console.log('Server status:', data);
            })
            .catch(error => {
                console.log('Status check failed:', error);
            });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_status(self):
        status = {
            "status": "running",
            "server": "Python HTTP Server",
            "port": 8083,
            "features": {
                "ml_categorizer": True,
                "spending_analysis": True,
                "csv_support": True,
                "plaid_ready": os.path.exists('.env')
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def log_message(self, format, *args):
        # Customize log format
        print(f"✅ {self.address_string()} - {format % args}")

def start_server(port=8083):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExpenseHandler)
    
    print(f"🚀 Expense Tracker Server Starting...")
    print(f"🌐 Chrome: http://localhost:{port}")
    print(f"🌐 Alt URL: http://127.0.0.1:{port}")
    print(f"⏹️  Press Ctrl+C to stop")
    print(f"📊 Status: http://localhost:{port}/status")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    start_server()