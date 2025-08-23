#!/usr/bin/env python3
"""
Flask web app for Plaid Link integration and expense analysis
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from plaid_client import PlaidClient
from spending_analyzer import SpendingAnalyzer
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize clients
plaid_client = PlaidClient()
analyzer = SpendingAnalyzer()


@app.route('/')
def index():
    """Main dashboard"""
    try:
        # Get connected accounts
        connected_accounts = plaid_client.list_connected_accounts()
        
        # Get recent transactions if accounts are connected
        recent_transactions = None
        insights = None
        
        if connected_accounts:
            df = plaid_client.get_all_transactions(days_back=30)
            if not df.empty:
                # Convert to format expected by analyzer
                analyzer.transactions_df = df
                insights = analyzer.generate_spending_insights()
                recent_transactions = df.head(10).to_dict('records')
        
        return render_template('dashboard.html', 
                             connected_accounts=connected_accounts,
                             recent_transactions=recent_transactions,
                             insights=insights)
                             
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/connect')
def connect_account():
    """Page to connect new bank account"""
    try:
        link_token = plaid_client.create_link_token()
        return render_template('connect.html', link_token=link_token)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/api/exchange_token', methods=['POST'])
def exchange_token():
    """Exchange public token for access token"""
    try:
        data = request.get_json()
        public_token = data.get('public_token')
        institution_name = data.get('institution_name', 'Unknown Bank')
        
        if not public_token:
            return jsonify({'error': 'Missing public token'}), 400
        
        result = plaid_client.exchange_public_token(public_token, institution_name)
        
        return jsonify({
            'success': True,
            'message': f'Successfully connected to {institution_name}',
            'institution': result['institution']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analysis')
def analysis():
    """Full expense analysis page"""
    try:
        # Get transactions from all connected accounts
        days_back = int(request.args.get('days', 365))
        df = plaid_client.get_all_transactions(days_back=days_back)
        
        if df.empty:
            return render_template('error.html', 
                                 error="No transactions found. Please connect a bank account first.")
        
        # Run analysis
        analyzer.transactions_df = analyzer.categorizer.categorize_transactions(df)
        insights = analyzer.generate_spending_insights()
        potential_savings = analyzer.calculate_potential_savings()
        monthly_summary = analyzer.monthly_spending_summary()
        
        # Ensure all numeric values are JSON serializable
        def make_serializable(obj):
            if hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif hasattr(obj, 'to_dict'):  # pandas objects
                return obj.to_dict()
            elif isinstance(obj, dict):
                return {str(k): make_serializable(v) for k, v in obj.items()}
            else:
                return obj
        
        potential_savings = make_serializable(potential_savings)
        
        # Prepare data for charts
        category_data = insights['top_spending_categories'].to_dict()
        
        # Convert Period objects to strings for JSON serialization
        monthly_data = {}
        for period, value in monthly_summary['Total'].items():
            monthly_data[str(period)] = float(value)
        
        return render_template('analysis.html',
                             insights=insights,
                             potential_savings=potential_savings,
                             category_data=category_data,
                             monthly_data=monthly_data,
                             total_transactions=len(df),
                             date_range=days_back)
                             
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/api/transactions')
def api_transactions():
    """API endpoint for transaction data"""
    try:
        days_back = int(request.args.get('days', 30))
        format_type = request.args.get('format', 'json')
        
        df = plaid_client.get_all_transactions(days_back=days_back)
        
        if df.empty:
            return jsonify({'error': 'No transactions found'}), 404
        
        if format_type == 'csv':
            return df.to_csv(index=False), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=transactions_{days_back}days.csv'
            }
        else:
            return jsonify({
                'transactions': df.to_dict('records'),
                'total_count': len(df),
                'date_range': days_back
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/insights')
def api_insights():
    """API endpoint for spending insights"""
    try:
        days_back = int(request.args.get('days', 365))
        df = plaid_client.get_all_transactions(days_back=days_back)
        
        if df.empty:
            return jsonify({'error': 'No transactions found'}), 404
        
        analyzer.transactions_df = analyzer.categorizer.categorize_transactions(df)
        insights = analyzer.generate_spending_insights()
        
        # Convert pandas Series to dict for JSON serialization
        if 'top_spending_categories' in insights:
            insights['top_spending_categories'] = insights['top_spending_categories'].to_dict()
        
        # Convert any other pandas objects to JSON-serializable format
        for key, value in insights.items():
            if hasattr(value, 'to_dict'):
                insights[key] = value.to_dict()
            elif hasattr(value, 'item'):  # numpy types
                insights[key] = value.item()
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/settings')
def settings():
    """Settings page"""
    connected_accounts = plaid_client.list_connected_accounts()
    return render_template('settings.html', connected_accounts=connected_accounts)


@app.route('/api/remove_connection', methods=['POST'])
def remove_connection():
    """Remove a bank connection"""
    try:
        data = request.get_json()
        institution = data.get('institution')
        
        if not institution:
            return jsonify({'error': 'Missing institution name'}), 400
        
        success = plaid_client.remove_connection(institution)
        
        if success:
            return jsonify({'success': True, 'message': f'Removed {institution}'})
        else:
            return jsonify({'error': f'Failed to remove {institution}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export')
def export_data():
    """Export transaction data"""
    try:
        days_back = int(request.args.get('days', 365))
        format_type = request.args.get('format', 'csv')
        
        df = plaid_client.get_all_transactions(days_back=days_back)
        
        if df.empty:
            return render_template('error.html', error="No transactions to export")
        
        filename = f"expense_export_{datetime.now().strftime('%Y%m%d')}_{days_back}days.csv"
        
        return df.to_csv(index=False), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename={filename}'
        }
        
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/api/create_link_token')
def create_link_token_api():
    """API endpoint to create a link token"""
    try:
        link_token = plaid_client.create_link_token()
        return jsonify({'link_token': link_token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test')
def test_plaid():
    """Test page for Plaid integration"""
    with open('test_plaid_link.html', 'r') as f:
        return f.read()


# Create templates directory and basic HTML templates
def create_templates():
    """Create basic HTML templates"""
    import os
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Base template
    base_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Expense Tracker{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/plaid-link@2/dist/link-initialize.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">💰 Expense Tracker</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/analysis">Analysis</a>
                <a class="nav-link" href="/connect">Connect Bank</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(f'{templates_dir}/base.html', 'w') as f:
        f.write(base_html)
    
    # Dashboard template
    dashboard_html = '''{% extends "base.html" %}

{% block title %}Dashboard - Expense Tracker{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h2>💰 Expense Dashboard</h2>
        
        {% if insights %}
        <div class="row mt-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <h5>Total Spending</h5>
                        <h3>${{ "%.2f"|format(insights.total_spending) }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <h5>Avg Transaction</h5>
                        <h3>${{ "%.2f"|format(insights.average_transaction) }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white {% if insights.spending_trend > 0 %}bg-warning{% else %}bg-success{% endif %}">
                    <div class="card-body">
                        <h5>Trend</h5>
                        <h3>{{ "%+.1f"|format(insights.spending_trend) }}%</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info">
                    <div class="card-body">
                        <h5>Categories</h5>
                        <h3>{{ insights.top_spending_categories|length }}</h3>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if recent_transactions %}
        <div class="mt-4">
            <h4>Recent Transactions</h4>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Amount</th>
                            <th>Category</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for txn in recent_transactions %}
                        <tr>
                            <td>{{ txn.Date }}</td>
                            <td>{{ txn.Description }}</td>
                            <td>${{ "%.2f"|format(txn.Amount) }}</td>
                            <td>{{ txn.Category }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
    
    <div class="col-md-4">
        <h4>Connected Accounts</h4>
        {% if connected_accounts %}
            {% for institution, data in connected_accounts.items() %}
            <div class="card mb-3">
                <div class="card-body">
                    <h6>{{ institution }}</h6>
                    <small class="text-muted">{{ data.accounts|length }} accounts</small>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="alert alert-info">
                <h6>No accounts connected</h6>
                <p>Connect your bank account to start tracking expenses automatically.</p>
                <a href="/connect" class="btn btn-primary">Connect Bank Account</a>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    # Connect page template
    connect_html = '''{% extends "base.html" %}

{% block title %}Connect Bank - Expense Tracker{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body text-center">
                <h4>🏦 Connect Your Bank Account</h4>
                <p class="text-muted">Securely connect your bank account using Plaid to automatically import transactions.</p>
                
                <div class="mt-4">
                    <button id="link-account" class="btn btn-primary btn-lg">
                        Connect Bank Account
                    </button>
                </div>
                
                <div class="mt-4">
                    <small class="text-muted">
                        🔒 Your login credentials are never stored. Plaid uses bank-level security to protect your data.
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
const linkToken = '{{ link_token }}';

const handler = Plaid.create({
    token: linkToken,
    onSuccess: (public_token, metadata) => {
        fetch('/api/exchange_token', {
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
                alert('Successfully connected to ' + data.institution);
                window.location.href = '/';
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Connection failed: ' + error);
        });
    },
    onExit: (err, metadata) => {
        console.log('User exited Link');
    }
});

document.getElementById('link-account').onclick = function() {
    handler.open();
};
</script>
{% endblock %}'''
    
    with open(f'{templates_dir}/connect.html', 'w') as f:
        f.write(connect_html)
    
    # Error template
    error_html = '''{% extends "base.html" %}

{% block title %}Error - Expense Tracker{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="alert alert-danger">
            <h4>❌ Error</h4>
            <p>{{ error }}</p>
            <a href="/" class="btn btn-primary">Return to Dashboard</a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/error.html', 'w') as f:
        f.write(error_html)


if __name__ == '__main__':
    # Create templates if they don't exist
    create_templates()
    
    print("🚀 Starting Expense Tracker Web App")
    print("💡 Make sure to set up your .env file with Plaid credentials")
    print("🌐 Open http://localhost:8080 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=8080)