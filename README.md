# Expense Tracker 💰

ML-powered expense categorization and analysis tool that helps you understand your spending patterns and identify savings opportunities.

## Features

🏦 **Secure Bank Integration**: Connect directly to your bank via Plaid API
🤖 **AI-Powered Categorization**: Automatically categorizes transactions using machine learning
📊 **Spending Analysis**: Detailed insights into spending patterns and trends  
💡 **Smart Recommendations**: AI-generated suggestions for reducing expenses
📈 **Visual Dashboard**: Interactive charts and graphs
🎯 **Savings Calculator**: Estimates potential monthly and annual savings
🌐 **Web Interface**: User-friendly browser-based dashboard

## Quick Start

### Option 1: Secure Bank Connection (Recommended)

1. **Setup Plaid integration:**
   ```bash
   pip install -r requirements.txt
   python setup_plaid.py
   ```

2. **Start web interface:**
   ```bash
   python main.py web
   ```

3. **Open http://localhost:5000** and connect your bank securely

### Option 2: CSV Upload

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Export your bank transactions** as CSV (most banks support this)

3. **Run the analyzer:**
   ```bash
   # Interactive mode
   python main.py interactive

   # Direct analysis
   python main.py analyze your_transactions.csv

   # Generate dashboard
   python main.py dashboard your_transactions.csv

   # Get savings recommendations
   python main.py recommendations your_transactions.csv
   ```

## CSV Format

Your bank CSV should contain columns for:
- **Amount/Debit** - Transaction amount
- **Description/Memo/Payee** - Transaction description  
- **Date** - Transaction date

The tool automatically detects common column names and formats.

## Categories

Transactions are automatically categorized into:
- 🛒 Groceries
- 🍽️ Dining
- 🚗 Transportation  
- ⚡ Utilities
- 🎬 Entertainment
- 🏥 Healthcare
- 🛍️ Shopping
- 📄 Bills
- ✈️ Travel
- 📦 Other

## Example Output

```
💰 Total Spending: $3,247.89
📊 Average Transaction: $47.23
📈 Spending Trend: +12.3%

📋 TOP SPENDING CATEGORIES:
   Dining: 28.5%
   Groceries: 22.1% 
   Transportation: 15.8%

💡 RECOMMENDATIONS:
   1. Consider reducing Dining spending - it's 28.5% of total expenses
   2. You spend more on dining out than groceries - cooking at home could save money
   3. Your spending has increased by 12.3% recently

🎯 POTENTIAL SAVINGS:
   Monthly: $487.18
   Annual: $5,846.16
```

## Security

✅ **No bank login required** - you export data manually  
✅ **Local processing** - all analysis happens on your machine  
✅ **No data uploaded** - your financial data stays private  
✅ **Open source** - you can audit the code

## Commands

### Plaid Integration (Bank Connection)
```bash
# Setup Plaid credentials
python setup_plaid.py

# Start web interface
python main.py web

# Connect bank accounts (CLI)
python main.py plaid-connect

# Analyze connected accounts
python main.py plaid-analyze --days 365
```

### CSV Analysis
```bash
# Interactive mode (recommended for first-time users)
python main.py interactive

# Analyze expenses and get insights
python main.py analyze transactions.csv

# Create visual dashboard
python main.py dashboard transactions.csv --save-plots

# Get detailed savings recommendations  
python main.py recommendations transactions.csv
```

## File Structure

```
expense-tracker/
├── main.py              # Main application entry point
├── expense_categorizer.py # ML categorization engine
├── spending_analyzer.py   # Analysis and insights
├── visualizer.py         # Charts and graphs
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Tips for Better Results

1. **Include transaction descriptions** - more detail = better categorization
2. **Use recent data** - at least 3-6 months for trend analysis  
3. **Regular analysis** - run monthly to track progress
4. **Export all transactions** - including small amounts for complete picture

## Supported Bank Formats

The tool works with CSV exports from most major banks including:
- Chase, Bank of America, Wells Fargo
- Capital One, Discover, American Express  
- Credit unions and regional banks
- Most fintech apps (Venmo, PayPal, etc.)

Just ensure your CSV has amount, description, and date columns.