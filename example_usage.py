#!/usr/bin/env python3
"""
Example usage of the Expense Tracker

This script demonstrates how to use the expense tracker with sample data.
"""

import pandas as pd
from datetime import datetime, timedelta
import random
from spending_analyzer import SpendingAnalyzer
from visualizer import ExpenseVisualizer


def create_sample_data(filename: str = "sample_transactions.csv", num_transactions: int = 200):
    """Create sample transaction data for demonstration"""
    
    # Sample merchants and their categories
    merchants = {
        'Groceries': ['Whole Foods', 'Safeway', 'Target', 'Walmart', 'Kroger'],
        'Dining': ['Starbucks', 'McDonalds', 'Pizza Hut', 'Local Restaurant', 'Subway'],
        'Transportation': ['Shell Gas', 'Uber', 'Metro Transit', 'Parking Meter', 'Lyft'],
        'Utilities': ['PG&E Electric', 'Water Company', 'Internet Provider', 'Phone Bill'],
        'Entertainment': ['Netflix', 'Spotify', 'Movie Theater', 'Gym Membership'],
        'Shopping': ['Amazon', 'Best Buy', 'Clothing Store', 'Online Shopping'],
        'Healthcare': ['CVS Pharmacy', 'Doctor Office', 'Dental Clinic'],
        'Bills': ['Insurance Payment', 'Credit Card Payment', 'Loan Payment']
    }
    
    # Generate random transactions
    transactions = []
    start_date = datetime.now() - timedelta(days=180)  # 6 months of data
    
    for i in range(num_transactions):
        # Pick random category and merchant
        category = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[category])
        
        # Generate realistic amounts based on category
        amount_ranges = {
            'Groceries': (20, 150),
            'Dining': (8, 60),
            'Transportation': (5, 80),
            'Utilities': (50, 200),
            'Entertainment': (10, 50),
            'Shopping': (15, 300),
            'Healthcare': (20, 150),
            'Bills': (100, 500)
        }
        
        min_amt, max_amt = amount_ranges[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        # Random date within the last 6 months
        random_days = random.randint(0, 180)
        transaction_date = start_date + timedelta(days=random_days)
        
        transactions.append({
            'Date': transaction_date.strftime('%Y-%m-%d'),
            'Description': merchant,
            'Amount': amount
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(transactions)
    df = df.sort_values('Date')
    df.to_csv(filename, index=False)
    
    print(f"✅ Created {filename} with {num_transactions} sample transactions")
    return filename


def demo_analysis():
    """Demonstrate the expense analysis capabilities"""
    
    print("🚀 EXPENSE TRACKER DEMO")
    print("=" * 50)
    
    # Create sample data
    csv_file = create_sample_data()
    
    # Initialize analyzer
    analyzer = SpendingAnalyzer()
    print(f"\n📂 Loading sample data from {csv_file}...")
    
    # Load and categorize transactions
    transactions = analyzer.load_transactions(csv_file)
    print(f"✅ Loaded and categorized {len(transactions)} transactions")
    
    # Generate insights
    print("\n🔍 Generating spending insights...")
    insights = analyzer.generate_spending_insights()
    
    print(f"\n💰 Total Spending: ${insights['total_spending']:,.2f}")
    print(f"📊 Average Transaction: ${insights['average_transaction']:.2f}")
    print(f"📈 Spending Trend: {insights['spending_trend']:+.1f}%")
    
    print("\n📋 Top Spending Categories:")
    for category, percentage in insights['top_spending_categories'].items():
        print(f"   {category}: {percentage:.1f}%")
    
    # Show recommendations
    if insights['recommendations']:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Calculate savings potential
    print("\n💰 Calculating savings potential...")
    potential_savings = analyzer.calculate_potential_savings()
    
    total_monthly = potential_savings.get('total_monthly_savings', 0)
    total_annual = potential_savings.get('total_annual_savings', 0)
    
    print(f"\n🎯 Potential Savings:")
    print(f"   Monthly: ${total_monthly:,.2f}")
    print(f"   Annual: ${total_annual:,.2f}")
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    try:
        visualizer = ExpenseVisualizer(analyzer)
        
        # Create dashboard
        print("   📈 Generating dashboard...")
        visualizer.create_dashboard()
        
        print("   🥧 Creating category breakdown...")
        visualizer.plot_category_breakdown()
        
    except ImportError as e:
        print(f"   ⚠️  Visualization libraries not available: {e}")
        print("   💡 Install matplotlib, seaborn, and plotly for visualizations")
    
    print("\n✅ Demo complete!")
    print(f"\n💡 To analyze your own data:")
    print(f"   1. Export transactions from your bank as CSV")
    print(f"   2. Run: python main.py analyze your_file.csv")
    print(f"   3. Or use interactive mode: python main.py interactive")


if __name__ == "__main__":
    demo_analysis()