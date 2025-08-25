import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import re
from typing import List, Dict, Optional


class ExpenseCategorizer:
    def __init__(self):
        self.model = None
        # Essential Categories
        self.categories = [
            # Essential
            'Housing', 'Food & Groceries', 'Transportation', 'Healthcare', 
            'Insurance', 'Debt Payments',
            # Lifestyle
            'Dining Out & Restaurants', 'Entertainment', 'Shopping & Retail', 
            'Travel & Vacation', 'Hobbies & Recreation', 'Personal Care',
            # Financial
            'Savings', 'Investments', 'Emergency Fund', 'Retirement Contributions',
            # Miscellaneous
            'Gifts & Donations', 'Education', 'Pet Care', 'Home Improvement',
            'Professional Services', 'Subscriptions', 'ATM/Cash Withdrawals',
            'Personal Transfers', 'Fees & Charges', 'Uncategorized/Other'
        ]
        
        self.category_keywords = {
            # Essential Categories
            'Housing': ['rent', 'mortgage', 'property tax', 'hoa', 'utilities', 'electric', 'water', 
                       'gas bill', 'internet', 'cable', 'phone', 'home insurance', 'renters insurance'],
            'Food & Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway', 
                                'kroger', 'whole foods', 'trader joes', 'aldi', 'food lion', 'publix',
                                'market', 'food', 'fresh', 'organic', 'produce', 'deli', 'bakery'],
            'Transportation': ['gas', 'fuel', 'car payment', 'auto loan', 'car insurance', 'maintenance',
                              'repair', 'oil change', 'tire', 'uber', 'lyft', 'taxi', 'metro', 'transit',
                              'parking', 'toll', 'registration', 'dmv', 'qt', 'exxon', 'shell', 'chevron',
                              'bp', '7-eleven', 'circle k', 'wawa', 'speedway', 'tire store', 'jiffy lube',
                              'valvoline', 'plat parking', 'park', 'garage'],
            'Healthcare': ['doctor', 'hospital', 'pharmacy', 'prescription', 'cvs', 'walgreens', 
                          'medical', 'dental', 'vision', 'clinic', 'copay', 'health insurance',
                          'bicycle health', 'urgent care', 'telehealth'],
            'Insurance': ['life insurance', 'health insurance', 'auto insurance', 'home insurance',
                         'disability insurance', 'umbrella insurance'],
            'Debt Payments': ['credit card payment', 'loan payment', 'student loan', 'personal loan',
                             'minimum payment', 'debt'],
            
            # Lifestyle Categories
            'Dining Out & Restaurants': ['restaurant', 'cafe', 'starbucks', 'mcdonalds', 'pizza', 
                                        'dining', 'takeout', 'delivery', 'doordash', 'ubereats',
                                        'grubhub', 'fast food', 'bar', 'brewery', 'arbys', 'wendys',
                                        'panda express', 'taco bell', 'burger king', 'kfc', 'subway',
                                        'chipotle', 'dominos', 'papa johns', 'sonic', 'dairy queen',
                                        'rosa cafe', 'qdoba', 'five guys', 'in-n-out'],
            'Entertainment': ['netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie', 
                             'theater', 'cinema', 'concert', 'tickets', 'streaming', 'gaming'],
            'Shopping & Retail': ['amazon', 'ebay', 'store', 'mall', 'clothing', 'best buy', 
                                 'electronics', 'furniture', 'home depot', 'lowes', 'merchandise'],
            'Travel & Vacation': ['hotel', 'airline', 'flight', 'booking', 'airbnb', 'vacation',
                                 'travel', 'car rental', 'cruise', 'resort'],
            'Hobbies & Recreation': ['gym', 'fitness', 'sports', 'hobby', 'craft', 'music lessons',
                                    'recreation', 'club membership', 'equipment'],
            'Personal Care': ['haircut', 'salon', 'spa', 'cosmetics', 'skincare', 'barber',
                             'nail salon', 'massage', 'beauty'],
            
            # Financial Categories
            'Savings': ['savings account', 'savings transfer', 'emergency savings', 'apple gs savings', 
                       'apple savings', 'high yield', 'money market'],
            'Investments': ['investment', 'brokerage', 'stock', 'mutual fund', 'etf', 'trading'],
            'Emergency Fund': ['emergency fund', 'emergency savings'],
            'Retirement Contributions': ['401k', 'ira', 'retirement', 'pension'],
            
            # Miscellaneous Categories
            'Gifts & Donations': ['gift', 'donation', 'charity', 'church', 'nonprofit', 'birthday',
                                 'wedding', 'holiday'],
            'Education': ['tuition', 'school', 'books', 'course', 'training', 'certification',
                         'education', 'learning'],
            'Pet Care': ['pet', 'veterinarian', 'vet', 'dog', 'cat', 'petco', 'petsmart',
                        'pet food', 'grooming'],
            'Home Improvement': ['home depot', 'lowes', 'hardware', 'repair', 'renovation',
                               'contractor', 'plumber', 'electrician'],
            'Professional Services': ['lawyer', 'attorney', 'accountant', 'tax', 'legal',
                                     'consultant', 'professional'],
            'Subscriptions': ['subscription', 'monthly fee', 'annual fee', 'membership', 'recurring',
                             'primo brands', 'water delivery', 'paypro'],
            'ATM/Cash Withdrawals': ['atm', 'cash withdrawal', 'cash advance'],
            'Personal Transfers': ['zelle', 'venmo', 'cashapp', 'paypal', 'transfer', 'apple pay cash'],
            'Fees & Charges': ['fee', 'charge', 'overdraft', 'late fee', 'service charge',
                              'maintenance fee', 'penalty', 'atm fee', 'foreign transaction',
                              'wire transfer', 'stop payment', 'returned item', 'tarrant county',
                              'county fee', 'city fee', 'government'],
            'Uncategorized/Other': []
        }
        
        # Category groupings for analysis
        self.category_groups = {
            'Essential': ['Housing', 'Food & Groceries', 'Transportation', 'Healthcare', 
                         'Insurance', 'Debt Payments'],
            'Lifestyle': ['Dining Out & Restaurants', 'Entertainment', 'Shopping & Retail', 
                         'Travel & Vacation', 'Hobbies & Recreation', 'Personal Care'],
            'Financial': ['Savings', 'Investments', 'Emergency Fund', 'Retirement Contributions'],
            'Miscellaneous': ['Gifts & Donations', 'Education', 'Pet Care', 'Home Improvement',
                             'Professional Services', 'Subscriptions', 'ATM/Cash Withdrawals',
                             'Fees & Charges', 'Personal Transfers', 'Uncategorized/Other']
        }
    
    def clean_description(self, description: str) -> str:
        """Clean transaction description for better categorization"""
        if pd.isna(description):
            return ""
        
        # Convert to lowercase and remove special characters
        cleaned = re.sub(r'[^\w\s]', ' ', str(description).lower())
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def create_training_data(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create training data based on keyword matching"""
        training_data = []
        
        for _, row in transactions_df.iterrows():
            description = self.clean_description(row.get('Description', ''))
            if not description:
                continue
            
            # Find category based on keywords
            category = 'Uncategorized/Other'
            for cat, keywords in self.category_keywords.items():
                if any(keyword in description for keyword in keywords):
                    category = cat
                    break
            
            training_data.append({
                'description': description,
                'category': category
            })
        
        return pd.DataFrame(training_data)
    
    def train_model(self, training_df: pd.DataFrame):
        """Train the categorization model"""
        # Create pipeline with TF-IDF and Naive Bayes
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])
        
        # Train the model
        X = training_df['description']
        y = training_df['category']
        
        self.model.fit(X, y)
        
        # Evaluate on split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        print("Model Performance:")
        print(classification_report(y_test, y_pred))
    
    def predict_category(self, description: str) -> str:
        """Predict category for a single transaction"""
        if not self.model:
            raise ValueError("Model not trained yet!")
        
        cleaned_desc = self.clean_description(description)
        prediction = self.model.predict([cleaned_desc])[0]
        return prediction
    
    def categorize_transactions(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Categorize all transactions in a dataframe"""
        if not self.model:
            # Create and train model if not exists
            training_data = self.create_training_data(transactions_df)
            self.train_model(training_data)
        
        # Add categories to transactions
        transactions_df = transactions_df.copy()
        transactions_df['Category'] = transactions_df.get('Description', '').apply(self.predict_category)
        
        return transactions_df
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        if not self.model:
            raise ValueError("No model to save!")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
    
    def get_category_group(self, category: str) -> str:
        """Get the group (Essential, Lifestyle, Financial, Miscellaneous) for a category"""
        for group, categories in self.category_groups.items():
            if category in categories:
                return group
        return 'Miscellaneous'
    
    def categorize_by_group(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Add category group column to transactions"""
        df = transactions_df.copy()
        df['Category_Group'] = df['Category'].apply(self.get_category_group)
        return df


def load_bank_csv(filepath: str, amount_col: str = 'Amount', 
                  description_col: str = 'Description', date_col: str = 'Date') -> pd.DataFrame:
    """Load bank CSV with flexible column naming"""
    df = pd.read_csv(filepath)
    
    # Standardize column names
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'amount' in col_lower or 'debit' in col_lower:
            column_mapping[col] = 'Amount'
        elif 'description' in col_lower or 'memo' in col_lower or 'payee' in col_lower:
            column_mapping[col] = 'Description'
        elif 'date' in col_lower:
            column_mapping[col] = 'Date'
    
    df = df.rename(columns=column_mapping)
    
    # Convert amount to positive values for expenses
    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').abs()
    
    # Convert date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    return df


if __name__ == "__main__":
    # Example usage
    print("Expense Categorizer initialized!")
    print("Use load_bank_csv() to load your transaction data")
    print("Then use ExpenseCategorizer().categorize_transactions() to categorize them")