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
        self.categories = [
            'Groceries', 'Dining', 'Transportation', 'Utilities', 'Entertainment',
            'Healthcare', 'Shopping', 'Bills', 'Travel', 'Other'
        ]
        self.category_keywords = {
            'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'safeway', 'kroger', 'whole foods'],
            'Dining': ['restaurant', 'food', 'cafe', 'starbucks', 'mcdonalds', 'pizza', 'dining'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'transit'],
            'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'cable', 'utility'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'theater', 'gym', 'subscription'],
            'Healthcare': ['pharmacy', 'doctor', 'medical', 'cvs', 'walgreens', 'hospital'],
            'Shopping': ['amazon', 'ebay', 'store', 'mall', 'clothing', 'best buy'],
            'Bills': ['insurance', 'mortgage', 'rent', 'loan', 'credit card', 'bank fee'],
            'Travel': ['hotel', 'airline', 'flight', 'booking', 'airbnb'],
            'Other': []
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
            category = 'Other'
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