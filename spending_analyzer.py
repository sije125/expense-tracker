import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from expense_categorizer import ExpenseCategorizer, load_bank_csv


class SpendingAnalyzer:
    def __init__(self):
        self.categorizer = ExpenseCategorizer()
        self.transactions_df = None
    
    def load_transactions(self, csv_path: str = None, plaid_df: pd.DataFrame = None) -> pd.DataFrame:
        """Load and categorize transactions from CSV or Plaid DataFrame"""
        if plaid_df is not None:
            # Use Plaid data directly
            self.transactions_df = plaid_df.copy()
        elif csv_path:
            # Load from CSV
            self.transactions_df = load_bank_csv(csv_path)
        else:
            raise ValueError("Either csv_path or plaid_df must be provided")
        
        self.transactions_df = self.categorizer.categorize_transactions(self.transactions_df)
        return self.transactions_df
    
    def monthly_spending_summary(self) -> pd.DataFrame:
        """Generate monthly spending summary by category"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        df = self.transactions_df.copy()
        df['Month'] = df['Date'].dt.to_period('M')
        
        summary = df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
        summary_pivot = summary.pivot(index='Month', columns='Category', values='Amount').fillna(0)
        summary_pivot['Total'] = summary_pivot.sum(axis=1)
        
        return summary_pivot
    
    def category_spending_analysis(self) -> Dict:
        """Analyze spending by category"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        category_totals = self.transactions_df.groupby('Category')['Amount'].agg(['sum', 'mean', 'count'])
        category_percentages = (category_totals['sum'] / category_totals['sum'].sum()) * 100
        
        return {
            'totals': category_totals,
            'percentages': category_percentages,
            'top_categories': category_percentages.sort_values(ascending=False).head(5)
        }
    
    def spending_trends(self) -> Dict:
        """Analyze spending trends over time"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        df = self.transactions_df.copy()
        df['Month'] = df['Date'].dt.to_period('M')
        
        monthly_totals = df.groupby('Month')['Amount'].sum()
        
        # Calculate trend (last 3 months vs previous 3 months if available)
        if len(monthly_totals) >= 6:
            recent_avg = monthly_totals.tail(3).mean()
            previous_avg = monthly_totals.iloc[-6:-3].mean()
            trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            trend_change = 0
        
        return {
            'monthly_totals': monthly_totals,
            'average_monthly': monthly_totals.mean(),
            'trend_change_percent': trend_change,
            'highest_month': monthly_totals.idxmax(),
            'lowest_month': monthly_totals.idxmin()
        }
    
    def identify_unusual_spending(self, threshold_multiplier: float = 2.0) -> pd.DataFrame:
        """Identify transactions that are unusually high for their category"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        df = self.transactions_df.copy()
        
        # Calculate category statistics
        category_stats = df.groupby('Category')['Amount'].agg(['mean', 'std'])
        
        unusual_transactions = []
        
        for category in category_stats.index:
            cat_data = df[df['Category'] == category]
            threshold = category_stats.loc[category, 'mean'] + (
                threshold_multiplier * category_stats.loc[category, 'std']
            )
            
            unusual = cat_data[cat_data['Amount'] > threshold]
            unusual_transactions.append(unusual)
        
        if unusual_transactions:
            return pd.concat(unusual_transactions).sort_values('Amount', ascending=False)
        else:
            return pd.DataFrame()
    
    def generate_spending_insights(self) -> Dict:
        """Generate actionable spending insights"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        category_analysis = self.category_spending_analysis()
        trends = self.spending_trends()
        unusual = self.identify_unusual_spending()
        
        insights = {
            'total_spending': self.transactions_df['Amount'].sum(),
            'average_transaction': self.transactions_df['Amount'].mean(),
            'top_spending_categories': category_analysis['top_categories'],
            'spending_trend': trends['trend_change_percent'],
            'unusual_transactions_count': len(unusual),
            'recommendations': []
        }
        
        # Generate recommendations
        top_category = category_analysis['top_categories'].index[0]
        top_category_pct = category_analysis['top_categories'].iloc[0]
        
        if top_category_pct > 30:
            insights['recommendations'].append(
                f"Consider reducing {top_category} spending - it's {top_category_pct:.1f}% of your total expenses"
            )
        
        if trends['trend_change_percent'] > 10:
            insights['recommendations'].append(
                f"Your spending has increased by {trends['trend_change_percent']:.1f}% recently"
            )
        
        if len(unusual) > 0:
            insights['recommendations'].append(
                f"You have {len(unusual)} unusually large transactions worth reviewing"
            )
        
        # Specific category recommendations
        category_totals = category_analysis['totals']['sum']
        
        if 'Dining' in category_totals and category_totals['Dining'] > category_totals.get('Groceries', 0):
            insights['recommendations'].append(
                "You spend more on dining out than groceries - cooking at home could save money"
            )
        
        if 'Entertainment' in category_totals and category_analysis['percentages']['Entertainment'] > 15:
            insights['recommendations'].append(
                "Entertainment spending is high - consider free or low-cost alternatives"
            )
        
        return insights
    
    def calculate_potential_savings(self) -> Dict:
        """Calculate potential savings by category"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        category_analysis = self.category_spending_analysis()
        category_totals = category_analysis['totals']['sum']
        
        # Conservative savings estimates
        savings_potential = {
            'Dining': 0.30,  # 30% savings by cooking more
            'Entertainment': 0.25,  # 25% savings with free alternatives
            'Shopping': 0.20,  # 20% savings with mindful shopping
            'Transportation': 0.15,  # 15% savings with optimization
            'Utilities': 0.10,  # 10% savings with efficiency
            'Groceries': 0.15,  # 15% savings with planning
        }
        
        potential_savings = {}
        total_potential = 0
        
        for category, percentage in savings_potential.items():
            if category in category_totals:
                monthly_spending = category_totals[category]
                potential_monthly_savings = monthly_spending * percentage
                potential_savings[category] = {
                    'monthly_spending': monthly_spending,
                    'potential_monthly_savings': potential_monthly_savings,
                    'potential_annual_savings': potential_monthly_savings * 12
                }
                total_potential += potential_monthly_savings
        
        potential_savings['total_monthly_savings'] = total_potential
        potential_savings['total_annual_savings'] = total_potential * 12
        
        return potential_savings


def main():
    """Example usage of the spending analyzer"""
    analyzer = SpendingAnalyzer()
    
    print("Spending Analyzer Ready!")
    print("\nUsage:")
    print("1. analyzer.load_transactions('your_bank_export.csv')")
    print("2. insights = analyzer.generate_spending_insights()")
    print("3. savings = analyzer.calculate_potential_savings()")
    print("4. summary = analyzer.monthly_spending_summary()")


if __name__ == "__main__":
    main()