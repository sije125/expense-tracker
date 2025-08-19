#!/usr/bin/env python3
"""
Expense Tracker - ML-powered expense categorization and analysis tool

Usage:
    python main.py analyze <csv_file>
    python main.py dashboard <csv_file>
    python main.py recommendations <csv_file>
    python main.py plaid-connect
    python main.py plaid-analyze
    python main.py web
"""

import sys
import argparse
from pathlib import Path
from spending_analyzer import SpendingAnalyzer
from visualizer import ExpenseVisualizer

try:
    from plaid_client import PlaidClient
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False


class ExpenseTracker:
    def __init__(self):
        self.analyzer = SpendingAnalyzer()
        self.visualizer = None
        if PLAID_AVAILABLE:
            self.plaid_client = PlaidClient()
        else:
            self.plaid_client = None
    
    def analyze_expenses(self, csv_file: str):
        """Analyze expenses and generate comprehensive report"""
        print(f"Loading transactions from {csv_file}...")
        
        try:
            transactions = self.analyzer.load_transactions(csv_file)
            print(f"✅ Loaded {len(transactions)} transactions")
            
            # Generate insights
            insights = self.analyzer.generate_spending_insights()
            
            print("\n" + "="*50)
            print("EXPENSE ANALYSIS REPORT")
            print("="*50)
            
            print(f"\n💰 Total Spending: ${insights['total_spending']:,.2f}")
            print(f"📊 Average Transaction: ${insights['average_transaction']:.2f}")
            
            print(f"\n📈 Spending Trend: {insights['spending_trend']:+.1f}%")
            if insights['spending_trend'] > 5:
                print("   ⚠️  Spending is increasing")
            elif insights['spending_trend'] < -5:
                print("   ✅ Spending is decreasing")
            else:
                print("   ➡️  Spending is stable")
            
            print(f"\n🔍 Unusual Transactions: {insights['unusual_transactions_count']}")
            
            print("\n📋 TOP SPENDING CATEGORIES:")
            for category, percentage in insights['top_spending_categories'].items():
                print(f"   {category}: {percentage:.1f}%")
            
            # Monthly summary
            monthly_summary = self.analyzer.monthly_spending_summary()
            print(f"\n📅 MONTHLY BREAKDOWN (Last {len(monthly_summary)} months):")
            for month, total in monthly_summary['Total'].tail(3).items():
                print(f"   {month}: ${total:,.2f}")
            
            # Recommendations
            if insights['recommendations']:
                print("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(insights['recommendations'], 1):
                    print(f"   {i}. {rec}")
            
            return insights
            
        except Exception as e:
            print(f"❌ Error analyzing expenses: {e}")
            return None
    
    def generate_savings_plan(self, csv_file: str):
        """Generate detailed savings recommendations"""
        try:
            self.analyzer.load_transactions(csv_file)
            potential_savings = self.analyzer.calculate_potential_savings()
            
            print("\n" + "="*50)
            print("SAVINGS OPPORTUNITIES")
            print("="*50)
            
            total_monthly = potential_savings.get('total_monthly_savings', 0)
            total_annual = potential_savings.get('total_annual_savings', 0)
            
            print(f"\n🎯 POTENTIAL SAVINGS:")
            print(f"   Monthly: ${total_monthly:,.2f}")
            print(f"   Annual: ${total_annual:,.2f}")
            
            print(f"\n📊 BY CATEGORY:")
            
            for category, data in potential_savings.items():
                if isinstance(data, dict) and 'monthly_spending' in data:
                    current = data['monthly_spending']
                    savings = data['potential_monthly_savings']
                    percentage = (savings / current) * 100 if current > 0 else 0
                    
                    print(f"\n   {category.upper()}:")
                    print(f"      Current: ${current:,.2f}/month")
                    print(f"      Potential savings: ${savings:,.2f}/month ({percentage:.0f}%)")
                    
                    # Specific recommendations by category
                    if category == 'Dining':
                        print("      💡 Cook at home more, meal prep, limit takeout")
                    elif category == 'Entertainment':
                        print("      💡 Free activities, library events, streaming bundles")
                    elif category == 'Shopping':
                        print("      💡 Wait 24hrs before purchases, use shopping lists")
                    elif category == 'Transportation':
                        print("      💡 Combine trips, public transport, carpool")
                    elif category == 'Utilities':
                        print("      💡 Energy-efficient appliances, programmable thermostat")
                    elif category == 'Groceries':
                        print("      💡 Meal planning, bulk buying, store brands")
            
            return potential_savings
            
        except Exception as e:
            print(f"❌ Error generating savings plan: {e}")
            return None
    
    def create_dashboard(self, csv_file: str, save_plots: bool = False):
        """Create visual dashboard"""
        try:
            self.analyzer.load_transactions(csv_file)
            self.visualizer = ExpenseVisualizer(self.analyzer)
            
            print("📊 Generating expense dashboard...")
            
            # Create comprehensive dashboard
            if save_plots:
                self.visualizer.create_dashboard('expense_dashboard.png')
                self.visualizer.plot_category_breakdown('category_breakdown.png')
                self.visualizer.plot_monthly_trends('monthly_trends.png')
                self.visualizer.plot_savings_potential('savings_potential.png')
                print("✅ Dashboard saved as PNG files")
            else:
                self.visualizer.create_dashboard()
            
        except Exception as e:
            print(f"❌ Error creating dashboard: {e}")
    
    def plaid_connect_flow(self):
        """Interactive flow to connect bank accounts via Plaid"""
        if not PLAID_AVAILABLE:
            print("❌ Plaid not available. Install with: pip install plaid-python")
            return
        
        print("\n🏦 CONNECT BANK ACCOUNT")
        print("=" * 50)
        
        try:
            # Check existing connections
            connected = self.plaid_client.list_connected_accounts()
            if connected:
                print("📊 Currently Connected Accounts:")
                for institution, data in connected.items():
                    print(f"   {institution}: {len(data['accounts'])} accounts")
                print()
            
            print("💡 To connect a new bank account:")
            print("   1. Start the web app: python main.py web")
            print("   2. Open http://localhost:5000 in your browser")
            print("   3. Click 'Connect Bank Account'")
            print("   4. Follow the secure Plaid Link flow")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def plaid_analyze(self, days_back: int = 365):
        """Analyze expenses from connected Plaid accounts"""
        if not PLAID_AVAILABLE:
            print("❌ Plaid not available. Install with: pip install plaid-python")
            return
        
        print(f"\n📊 ANALYZING PLAID DATA ({days_back} days)")
        print("=" * 50)
        
        try:
            # Get transactions from Plaid
            df = self.plaid_client.get_all_transactions(days_back=days_back)
            
            if df.empty:
                print("❌ No transactions found. Please connect a bank account first.")
                print("💡 Run: python main.py plaid-connect")
                return
            
            # Use existing analysis methods
            self.analyzer.transactions_df = self.analyzer.categorizer.categorize_transactions(df)
            insights = self.analyzer.generate_spending_insights()
            
            print(f"✅ Analyzed {len(df)} transactions from connected accounts")
            print(f"\n💰 Total Spending: ${insights['total_spending']:,.2f}")
            print(f"📊 Average Transaction: ${insights['average_transaction']:.2f}")
            print(f"📈 Spending Trend: {insights['spending_trend']:+.1f}%")
            
            print("\n📋 TOP SPENDING CATEGORIES:")
            for category, percentage in insights['top_spending_categories'].items():
                print(f"   {category}: {percentage:.1f}%")
            
            if insights['recommendations']:
                print("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(insights['recommendations'], 1):
                    print(f"   {i}. {rec}")
            
            # Show savings potential
            potential_savings = self.analyzer.calculate_potential_savings()
            total_monthly = potential_savings.get('total_monthly_savings', 0)
            total_annual = potential_savings.get('total_annual_savings', 0)
            
            print(f"\n🎯 POTENTIAL SAVINGS:")
            print(f"   Monthly: ${total_monthly:,.2f}")
            print(f"   Annual: ${total_annual:,.2f}")
            
        except Exception as e:
            print(f"❌ Error analyzing Plaid data: {e}")
    
    def start_web_app(self):
        """Start the Flask web application"""
        if not PLAID_AVAILABLE:
            print("❌ Plaid not available. Install with: pip install plaid-python flask")
            return
        
        try:
            from web_app import app
            print("🚀 Starting Expense Tracker Web App")
            print("💡 Make sure to set up your .env file with Plaid credentials")
            print("🌐 Open http://localhost:8081 in your browser")
            app.run(debug=True, host='0.0.0.0', port=8081)
        except ImportError as e:
            print(f"❌ Web app dependencies missing: {e}")
            print("💡 Install with: pip install flask")
    
    def run_interactive_mode(self):
        """Run interactive mode for exploring data"""
        print("\n🚀 EXPENSE TRACKER - Interactive Mode")
        
        if PLAID_AVAILABLE:
            print("Choose data source:")
            print("1. CSV file")
            print("2. Connected bank accounts (Plaid)")
            print("3. Web interface")
            print("4. Quit")
            
            choice = input("\nChoice (1-4): ").strip()
            
            if choice == '2':
                self.plaid_analyze()
                return
            elif choice == '3':
                self.start_web_app()
                return
            elif choice == '4':
                return
            elif choice != '1':
                print("Invalid choice!")
                return
        
        print("Enter CSV file path (or 'quit' to exit):")
        
        while True:
            csv_file = input("\n> ").strip()
            
            if csv_file.lower() in ['quit', 'exit', 'q']:
                break
            
            if not Path(csv_file).exists():
                print("❌ File not found!")
                continue
            
            print("\nChoose action:")
            print("1. Analyze expenses")
            print("2. Generate savings plan")
            print("3. Create dashboard")
            print("4. Enter new file")
            
            choice = input("\nChoice (1-4): ").strip()
            
            if choice == '1':
                self.analyze_expenses(csv_file)
            elif choice == '2':
                self.generate_savings_plan(csv_file)
            elif choice == '3':
                self.create_dashboard(csv_file)
            elif choice == '4':
                continue
            else:
                print("Invalid choice!")


def main():
    parser = argparse.ArgumentParser(description='Expense Tracker - ML-powered expense analysis')
    parser.add_argument('command', 
                       choices=['analyze', 'dashboard', 'recommendations', 'interactive', 
                               'plaid-connect', 'plaid-analyze', 'web'],
                       help='Command to run')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file with transactions')
    parser.add_argument('--save-plots', action='store_true', help='Save plots as PNG files')
    parser.add_argument('--days', type=int, default=365, help='Days of transaction history for Plaid')
    
    args = parser.parse_args()
    
    tracker = ExpenseTracker()
    
    # Handle Plaid commands
    if args.command == 'plaid-connect':
        tracker.plaid_connect_flow()
        return
    elif args.command == 'plaid-analyze':
        tracker.plaid_analyze(args.days)
        return
    elif args.command == 'web':
        tracker.start_web_app()
        return
    elif args.command == 'interactive':
        tracker.run_interactive_mode()
        return
    
    # CSV-based commands
    if not args.csv_file:
        print("❌ CSV file required for this command")
        sys.exit(1)
    
    if not Path(args.csv_file).exists():
        print(f"❌ File not found: {args.csv_file}")
        sys.exit(1)
    
    if args.command == 'analyze':
        tracker.analyze_expenses(args.csv_file)
    elif args.command == 'dashboard':
        tracker.create_dashboard(args.csv_file, args.save_plots)
    elif args.command == 'recommendations':
        tracker.generate_savings_plan(args.csv_file)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run interactive mode
        tracker = ExpenseTracker()
        tracker.run_interactive_mode()
    else:
        main()