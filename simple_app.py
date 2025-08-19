#!/usr/bin/env python3
"""
Simple Flask app without Plaid dependency for testing
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Expense Tracker</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">💰 Expense Tracker</a>
        </div>
    </nav>
    
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body text-center">
                        <h1 class="card-title">🎉 Expense Tracker is Working!</h1>
                        <p class="card-text">Your ML-powered expense categorization tool is ready.</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h5>🏦 Bank Integration</h5>
                                        <p>Connect securely via Plaid API</p>
                                        <button class="btn btn-primary" disabled>Connect Bank (Setup Required)</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h5>📊 CSV Analysis</h5>
                                        <p>Upload bank transaction files</p>
                                        <a href="/upload" class="btn btn-success">Upload CSV</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <h6>Available Commands:</h6>
                            <div class="text-start">
                                <code>python3 main.py interactive</code> - Interactive mode<br>
                                <code>python3 main.py analyze file.csv</code> - Analyze CSV<br>
                                <code>python3 example_usage.py</code> - Demo with sample data
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

@app.route('/upload')
def upload():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Upload CSV - Expense Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">💰 Expense Tracker</a>
        </div>
    </nav>
    
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h3>📁 Upload Bank CSV</h3>
                        <p>Upload your bank transaction CSV file for analysis.</p>
                        
                        <div class="alert alert-info">
                            <h6>CSV Format Requirements:</h6>
                            <ul class="mb-0">
                                <li>Amount/Debit column</li>
                                <li>Description/Memo column</li>
                                <li>Date column</li>
                            </ul>
                        </div>
                        
                        <div class="alert alert-warning">
                            <strong>Note:</strong> For now, use the command line tools:<br>
                            <code>python3 main.py analyze your_file.csv</code>
                        </div>
                        
                        <a href="/" class="btn btn-secondary">← Back to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    ''')

if __name__ == '__main__':
    print("🚀 Starting Simple Expense Tracker Web App")
    print("🌐 Open http://localhost:8080 in your browser")
    app.run(debug=True, host='0.0.0.0', port=8080)