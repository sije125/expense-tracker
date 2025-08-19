#!/usr/bin/env python3
"""
Command-line Plaid integration for bank connections
No web server required - uses Plaid API directly
"""

import json
import sys
from datetime import datetime, timedelta
from plaid_client import PlaidClient
from spending_analyzer import SpendingAnalyzer


class PlaidCLI:
    def __init__(self):
        try:
            self.plaid_client = PlaidClient()
            self.analyzer = SpendingAnalyzer()
            print("✅ Plaid CLI initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Plaid: {e}")
            sys.exit(1)
    
    def show_status(self):
        """Show current Plaid connection status"""
        print("\n🏦 PLAID CONNECTION STATUS")
        print("=" * 50)
        
        try:
            # Test API connection
            link_token = self.plaid_client.create_link_token()
            print("✅ Plaid API connection: Working")
            print("✅ Credentials: Valid")
            print(f"✅ Environment: {self.plaid_client.env}")
            
            # Check existing connections
            connected_accounts = self.plaid_client.list_connected_accounts()
            
            if connected_accounts:
                print(f"\n📊 Connected Institutions: {len(connected_accounts)}")
                for institution, data in connected_accounts.items():
                    print(f"   {institution}: {len(data['accounts'])} accounts")
                    print(f"      Connected: {data['connected_at'][:10]}")
            else:
                print("\n📋 No banks connected yet")
            
        except Exception as e:
            print(f"❌ Plaid API error: {e}")
    
    def connect_instructions(self):
        """Show instructions for connecting banks"""
        print("\n🔗 HOW TO CONNECT YOUR BANK")
        print("=" * 50)
        print("Since web browsers are having connectivity issues, here are alternatives:")
        print()
        print("📱 OPTION 1: Mobile Device")
        print("   1. Open your phone's browser")
        print("   2. Connect to the same WiFi network")
        print("   3. Go to: http://192.168.1.158:8085")
        print("   4. Click 'Connect Bank Account'")
        print()
        print("💻 OPTION 2: Different Computer")
        print("   1. Use another computer on same network")
        print("   2. Go to: http://192.168.1.158:8085")
        print("   3. Complete Plaid Link flow")
        print()
        print("🌐 OPTION 3: Public Plaid Demo")
        print("   1. Visit: https://plaid.com/docs/quickstart/")
        print("   2. Try their live demo first")
        print("   3. Get familiar with the flow")
        print()
        print("📋 OPTION 4: Manual Token Exchange")
        print("   If you can get a public_token from Plaid Link elsewhere:")
        print("   python3 plaid_cli.py exchange YOUR_PUBLIC_TOKEN")
    
    def manual_token_exchange(self, public_token, institution_name="Manual"):
        """Exchange a public token manually"""
        try:
            print(f"\n🔄 Exchanging token for {institution_name}...")
            result = self.plaid_client.exchange_public_token(public_token, institution_name)
            
            print("✅ Bank connected successfully!")
            print(f"   Institution: {result['institution']}")
            print(f"   Item ID: {result['item_id']}")
            
            # Test getting accounts
            accounts = self.plaid_client.get_accounts(result['access_token'])
            print(f"   Accounts found: {len(accounts)}")
            
            for account in accounts:
                print(f"      {account['name']} ({account['type']}): ${account['balance']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Token exchange failed: {e}")
            return False
    
    def analyze_connected_accounts(self, days_back=365):
        """Analyze transactions from connected accounts"""
        print(f"\n📊 ANALYZING CONNECTED ACCOUNTS ({days_back} days)")
        print("=" * 50)
        
        try:
            # Get transactions
            df = self.plaid_client.get_all_transactions(days_back=days_back)
            
            if df.empty:
                print("❌ No transactions found")
                print("💡 Make sure you have connected a bank account")
                return
            
            print(f"✅ Retrieved {len(df)} transactions")
            
            # Analyze with ML
            self.analyzer.transactions_df = self.analyzer.categorizer.categorize_transactions(df)
            insights = self.analyzer.generate_spending_insights()
            
            # Display results
            print(f"\n💰 Total Spending: ${insights['total_spending']:,.2f}")
            print(f"📊 Average Transaction: ${insights['average_transaction']:.2f}")
            print(f"📈 Spending Trend: {insights['spending_trend']:+.1f}%")
            
            print(f"\n📋 TOP SPENDING CATEGORIES:")
            for category, percentage in insights['top_spending_categories'].items():
                print(f"   {category}: {percentage:.1f}%")
            
            if insights['recommendations']:
                print(f"\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(insights['recommendations'], 1):
                    print(f"   {i}. {rec}")
            
            # Potential savings
            potential_savings = self.analyzer.calculate_potential_savings()
            total_monthly = potential_savings.get('total_monthly_savings', 0)
            total_annual = potential_savings.get('total_annual_savings', 0)
            
            print(f"\n🎯 POTENTIAL SAVINGS:")
            print(f"   Monthly: ${total_monthly:,.2f}")
            print(f"   Annual: ${total_annual:,.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False
    
    def export_data(self, days_back=365, filename=None):
        """Export transaction data to CSV"""
        try:
            df = self.plaid_client.get_all_transactions(days_back=days_back)
            
            if df.empty:
                print("❌ No transactions to export")
                return
            
            if not filename:
                filename = f"plaid_export_{datetime.now().strftime('%Y%m%d')}.csv"
            
            df.to_csv(filename, index=False)
            print(f"✅ Exported {len(df)} transactions to {filename}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")


def main():
    cli = PlaidCLI()
    
    if len(sys.argv) == 1:
        # No arguments - show status and help
        cli.show_status()
        cli.connect_instructions()
        
    elif sys.argv[1] == "status":
        cli.show_status()
        
    elif sys.argv[1] == "connect":
        cli.connect_instructions()
        
    elif sys.argv[1] == "analyze":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        cli.analyze_connected_accounts(days)
        
    elif sys.argv[1] == "export":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        cli.export_data(days, filename)
        
    elif sys.argv[1] == "exchange":
        if len(sys.argv) < 3:
            print("❌ Usage: python3 plaid_cli.py exchange PUBLIC_TOKEN [BANK_NAME]")
            sys.exit(1)
        
        public_token = sys.argv[2]
        bank_name = sys.argv[3] if len(sys.argv) > 3 else "Manual"
        cli.manual_token_exchange(public_token, bank_name)
        
    else:
        print("❌ Unknown command")
        print("Usage:")
        print("  python3 plaid_cli.py status")
        print("  python3 plaid_cli.py connect")
        print("  python3 plaid_cli.py analyze [days]")
        print("  python3 plaid_cli.py export [days] [filename]")
        print("  python3 plaid_cli.py exchange PUBLIC_TOKEN [BANK_NAME]")


if __name__ == "__main__":
    main()