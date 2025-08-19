import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from dotenv import load_dotenv

try:
    from plaid.api import plaid_api
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.country_code import CountryCode
    from plaid.model.products import Products
    from plaid.configuration import Configuration
    from plaid.api_client import ApiClient
except ImportError:
    print("⚠️  Plaid not installed. Run: pip install plaid-python")
    raise

load_dotenv()


class PlaidClient:
    def __init__(self):
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')
        self.env = os.getenv('PLAID_ENV', 'sandbox')
        
        if not self.client_id or not self.secret:
            raise ValueError("Missing Plaid credentials. Check your .env file.")
        
        # Configure Plaid client based on environment
        if self.env == 'sandbox':
            host = 'https://sandbox.plaid.com'
        elif self.env == 'development':
            host = 'https://development.plaid.com'
        else:
            host = 'https://production.plaid.com'
        
        configuration = Configuration(
            host=host,
            api_key={
                'clientId': self.client_id,
                'secret': self.secret
            }
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        
        self.access_tokens = {}  # Store access tokens for connected accounts
    
    def create_link_token(self, user_id: str = "user_1") -> str:
        """Create a Link token for Plaid Link initialization"""
        try:
            request = LinkTokenCreateRequest(
                products=[Products('transactions')],
                client_name="Expense Tracker",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )
            
            response = self.client.link_token_create(request)
            return response['link_token']
            
        except Exception as e:
            print(f"Error creating link token: {e}")
            raise
    
    def exchange_public_token(self, public_token: str, institution_name: str = None) -> Dict:
        """Exchange public token for access token"""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            
            access_token = response['access_token']
            item_id = response['item_id']
            
            # Store access token
            key = institution_name or item_id
            self.access_tokens[key] = {
                'access_token': access_token,
                'item_id': item_id,
                'connected_at': datetime.now().isoformat()
            }
            
            # Save to file for persistence
            self._save_access_tokens()
            
            return {
                'access_token': access_token,
                'item_id': item_id,
                'institution': key
            }
            
        except Exception as e:
            print(f"Error exchanging public token: {e}")
            raise
    
    def get_accounts(self, access_token: str) -> List[Dict]:
        """Get account information"""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            
            accounts = []
            for account in response['accounts']:
                accounts.append({
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': account['type'],
                    'subtype': account['subtype'],
                    'balance': account['balances']['current']
                })
            
            return accounts
            
        except Exception as e:
            print(f"Error getting accounts: {e}")
            raise
    
    def get_transactions(self, access_token: str, start_date: datetime = None, 
                        end_date: datetime = None, account_ids: List[str] = None) -> pd.DataFrame:
        """Get transactions from Plaid"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=365)  # 1 year default
            if not end_date:
                end_date = datetime.now()
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                account_ids=account_ids
            )
            
            response = self.client.transactions_get(request)
            transactions = response['transactions']
            
            # Convert to DataFrame
            transaction_data = []
            for transaction in transactions:
                transaction_data.append({
                    'Date': transaction['date'],
                    'Description': transaction['name'],
                    'Amount': abs(transaction['amount']),  # Make positive for expenses
                    'Account': transaction['account_id'],
                    'Category': ' > '.join(transaction.get('category', ['Other'])),
                    'transaction_id': transaction['transaction_id'],
                    'merchant_name': transaction.get('merchant_name', ''),
                    'account_owner': transaction.get('account_owner', '')
                })
            
            df = pd.DataFrame(transaction_data)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter out transfers and credits (focus on expenses)
            df = df[df['Amount'] > 0]
            
            return df.sort_values('Date', ascending=False)
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            raise
    
    def get_all_transactions(self, days_back: int = 365) -> pd.DataFrame:
        """Get transactions from all connected accounts"""
        all_transactions = []
        
        self._load_access_tokens()
        
        if not self.access_tokens:
            print("No connected accounts found. Please connect an account first.")
            return pd.DataFrame()
        
        start_date = datetime.now() - timedelta(days=days_back)
        end_date = datetime.now()
        
        for institution, token_data in self.access_tokens.items():
            try:
                print(f"Fetching transactions from {institution}...")
                
                access_token = token_data['access_token']
                transactions = self.get_transactions(access_token, start_date, end_date)
                
                if not transactions.empty:
                    transactions['Institution'] = institution
                    all_transactions.append(transactions)
                    print(f"✅ Got {len(transactions)} transactions from {institution}")
                else:
                    print(f"⚠️  No transactions found for {institution}")
                    
            except Exception as e:
                print(f"❌ Error fetching from {institution}: {e}")
                continue
        
        if all_transactions:
            combined_df = pd.concat(all_transactions, ignore_index=True)
            return combined_df.sort_values('Date', ascending=False)
        else:
            return pd.DataFrame()
    
    def _save_access_tokens(self):
        """Save access tokens to file"""
        with open('.plaid_tokens.json', 'w') as f:
            json.dump(self.access_tokens, f, indent=2)
    
    def _load_access_tokens(self):
        """Load access tokens from file"""
        try:
            with open('.plaid_tokens.json', 'r') as f:
                self.access_tokens = json.load(f)
        except FileNotFoundError:
            self.access_tokens = {}
    
    def list_connected_accounts(self) -> Dict:
        """List all connected accounts"""
        self._load_access_tokens()
        
        connected_accounts = {}
        for institution, token_data in self.access_tokens.items():
            try:
                access_token = token_data['access_token']
                accounts = self.get_accounts(access_token)
                connected_accounts[institution] = {
                    'connected_at': token_data['connected_at'],
                    'accounts': accounts
                }
            except Exception as e:
                print(f"Error checking {institution}: {e}")
                
        return connected_accounts
    
    def remove_connection(self, institution: str) -> bool:
        """Remove a connected institution"""
        self._load_access_tokens()
        
        if institution in self.access_tokens:
            del self.access_tokens[institution]
            self._save_access_tokens()
            print(f"✅ Removed connection to {institution}")
            return True
        else:
            print(f"❌ No connection found for {institution}")
            return False


def main():
    """Example usage"""
    try:
        client = PlaidClient()
        print("✅ Plaid client initialized successfully")
        
        # Check for existing connections
        accounts = client.list_connected_accounts()
        if accounts:
            print(f"\n📊 Connected Accounts: {len(accounts)}")
            for institution, data in accounts.items():
                print(f"   {institution}: {len(data['accounts'])} accounts")
        else:
            print("\n💡 No accounts connected yet")
            print("Use the web interface to connect your bank accounts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to set up your .env file with Plaid credentials")


if __name__ == "__main__":
    main()