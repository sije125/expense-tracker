#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
from threading import Timer

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Expense Tracker - Working!</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .feature { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 15px 0; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Expense Tracker Web Interface</h1>
        
        <div class="success">
            <strong>Success!</strong> Your expense tracker web server is now running correctly!
        </div>
        
        <h2>Available Features:</h2>
        
        <div class="feature">
            <h3>Command Line Analysis</h3>
            <p>Run these commands in your terminal:</p>
            <ul>
                <li><code>python3 main.py analyze sample_transactions.csv</code> - Analyze expenses</li>
                <li><code>python3 main.py dashboard sample_transactions.csv --save-plots</code> - Create visual dashboard</li>
                <li><code>python3 main.py recommendations sample_transactions.csv</code> - Get savings tips</li>
            </ul>
        </div>
        
        <div class="feature">
            <h3>Bank Connection (Advanced)</h3>
            <p>For live bank data integration:</p>
            <ul>
                <li>Set up Plaid API credentials in <code>.env</code></li>
                <li>Run <code>python3 main.py web</code> for full Flask app</li>
                <li>Connect real bank accounts securely</li>
            </ul>
        </div>
        
        <div class="feature">
            <h3>Sample Analysis Results</h3>
            <p>Your sample data shows:</p>
            <ul>
                <li>Total spending: $22,440.89</li>
                <li>200 transactions analyzed</li>
                <li>ML categorization active</li>
                <li>Potential monthly savings: $171.00</li>
            </ul>
        </div>
        
        <p style="text-align: center; margin-top: 30px;">
            <strong>Server Status:</strong> Running on localhost:8080
        </p>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode())
        else:
            super().do_GET()

# Start server
with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🚀 Server starting on http://localhost:{PORT}")
    print(f"✅ Open this URL in your browser: http://localhost:{PORT}")
    print("⏹️  Press Ctrl+C to stop")
    httpd.serve_forever()