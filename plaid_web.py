#!/usr/bin/env python3
"""
Simplified Plaid web interface for bank connections
"""

from flask import Flask, render_template_string, request, jsonify
import os
import sys
from plaid_client import PlaidClient

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key')

# Initialize Plaid client
try:
    plaid_client = PlaidClient()
    PLAID_READY = True
except Exception as e:
    print(f"⚠️  Plaid initialization failed: {e}")
    PLAID_READY = False

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>💰 Expense Tracker - Plaid Login</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/plaid-link@2/dist/link-initialize.js"></script>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand">💰 Expense Tracker</span>
        </div>
    </nav>
    
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body text-center">
                        <h1>🏦 Connect Your Bank Account</h1>
                        <p class="lead">Securely connect to 12,000+ banks via Plaid</p>
                        
                        {% if plaid_ready %}
                        <div class="alert alert-success">
                            <h5>✅ Plaid Ready!</h5>
                            <p>Your credentials are configured and working.</p>
                        </div>
                        
                        <div class="mt-4">
                            <button id="link-button" class="btn btn-primary btn-lg">
                                🔗 Connect Bank Account
                            </button>
                        </div>
                        
                        <div class="mt-4">
                            <h6>🔒 Security Features:</h6>
                            <ul class="list-unstyled">
                                <li>✅ Bank-approved connections</li>
                                <li>✅ OAuth authentication</li>
                                <li>✅ No passwords stored</li>
                                <li>✅ Encrypted data transfer</li>
                            </ul>
                        </div>
                        
                        {% else %}
                        <div class="alert alert-warning">
                            <h5>⚠️ Plaid Setup Required</h5>
                            <p>Plaid credentials need to be configured.</p>
                            <p>Run: <code>python3 setup_plaid.py</code></p>
                        </div>
                        {% endif %}
                        
                        <div class="mt-4">
                            <h6>Alternative: Command Line</h6>
                            <div class="alert alert-info">
                                <code>python3 main.py analyze your_file.csv</code><br>
                                <code>python3 example_usage.py</code>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="status" class="mt-3"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Plaid Link
        {% if plaid_ready %}
        
        // First get a link token
        fetch('/create_link_token')
            .then(response => response.json())
            .then(data => {
                if (data.link_token) {
                    initializePlaidLink(data.link_token);
                } else {
                    showError('Failed to create link token: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                showError('Network error: ' + error);
            });
        
        function initializePlaidLink(linkToken) {
            const handler = Plaid.create({
                token: linkToken,
                onSuccess: (public_token, metadata) => {
                    showStatus('🔄 Connecting to ' + metadata.institution.name + '...');
                    
                    // Exchange public token for access token
                    fetch('/exchange_token', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            public_token: public_token,
                            institution_name: metadata.institution.name
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showSuccess('✅ Successfully connected to ' + data.institution + '!');
                            setTimeout(() => {
                                window.location.href = '/dashboard';
                            }, 2000);
                        } else {
                            showError('❌ Connection failed: ' + data.error);
                        }
                    })
                    .catch(error => {
                        showError('❌ Exchange failed: ' + error);
                    });
                },
                onExit: (err, metadata) => {
                    if (err) {
                        showError('❌ Connection cancelled: ' + err.error_message);
                    } else {
                        showStatus('ℹ️ Connection cancelled by user');
                    }
                }
            });
            
            document.getElementById('link-button').onclick = function() {
                handler.open();
            };
        }
        
        {% endif %}
        
        function showStatus(message) {
            document.getElementById('status').innerHTML = 
                '<div class="alert alert-info">' + message + '</div>';
        }
        
        function showSuccess(message) {
            document.getElementById('status').innerHTML = 
                '<div class="alert alert-success">' + message + '</div>';
        }
        
        function showError(message) {
            document.getElementById('status').innerHTML = 
                '<div class="alert alert-danger">' + message + '</div>';
        }
    </script>
</body>
</html>
    """, plaid_ready=PLAID_READY)

@app.route('/create_link_token')
def create_link_token():
    if not PLAID_READY:
        return jsonify({'error': 'Plaid not configured'})
    
    try:
        link_token = plaid_client.create_link_token()
        return jsonify({'link_token': link_token})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/exchange_token', methods=['POST'])
def exchange_token():
    if not PLAID_READY:
        return jsonify({'error': 'Plaid not configured'})
    
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        institution_name = data.get('institution_name', 'Bank')
        
        result = plaid_client.exchange_public_token(public_token, institution_name)
        
        return jsonify({
            'success': True,
            'institution': result['institution'],
            'message': f'Connected to {institution_name}'
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/dashboard')
def dashboard():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Expense Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand">💰 Expense Tracker</span>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h1>🎉 Bank Connected Successfully!</h1>
        
        <div class="alert alert-success">
            <h5>✅ Ready to Analyze</h5>
            <p>Your bank account is now connected. Use these commands to analyze your data:</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>📊 Analyze Connected Accounts</h5>
                        <p>Get insights from your connected bank data:</p>
                        <code>python3 main.py plaid-analyze</code>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>💰 Get Savings Recommendations</h5>
                        <p>See where you can cut spending:</p>
                        <code>python3 main.py plaid-analyze --days 180</code>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <a href="/" class="btn btn-primary">Connect Another Account</a>
        </div>
    </div>
</body>
</html>
    """)

if __name__ == '__main__':
    print("🚀 Starting Plaid Connection Interface")
    print("🌐 Open in Chrome: http://localhost:8085")
    print("🏦 Connect your bank securely via Plaid")
    
    app.run(debug=True, host='0.0.0.0', port=8085)