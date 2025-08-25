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
    
    def analyze_specific_spending_patterns(self) -> Dict:
        """Analyze specific spending patterns for detailed recommendations"""
        df = self.transactions_df.copy()
        
        patterns = {
            'subscriptions': [],
            'dining_frequency': 0,
            'fast_food_spending': 0,
            'grocery_vs_dining': {'groceries': 0, 'dining': 0},
            'specific_merchants': {},
            'fees_paid': [],
            'unusual_large': []
        }
        
        # Analyze subscription patterns with detailed service identification
        subscription_transactions = df[df['Category'] == 'Subscriptions']
        for _, txn in subscription_transactions.iterrows():
            desc = txn['Description']
            desc_lower = desc.lower()
            amount = txn['Amount']
            
            # Specific service identification
            if 'amazon prime' in desc_lower:
                patterns['subscriptions'].append(f"Amazon Prime (${amount:.2f})")
            elif 'paramount' in desc_lower:
                patterns['subscriptions'].append(f"Paramount+ (${amount:.2f})")
            elif 'netflix' in desc_lower:
                patterns['subscriptions'].append(f"Netflix (${amount:.2f})")
            elif 'spotify' in desc_lower:
                patterns['subscriptions'].append(f"Spotify (${amount:.2f})")
            elif 'hulu' in desc_lower:
                patterns['subscriptions'].append(f"Hulu (${amount:.2f})")
            elif 'disney' in desc_lower:
                patterns['subscriptions'].append(f"Disney+ (${amount:.2f})")
            elif 'apple' in desc_lower and 'music' in desc_lower:
                patterns['subscriptions'].append(f"Apple Music (${amount:.2f})")
            elif 'youtube' in desc_lower and 'premium' in desc_lower:
                patterns['subscriptions'].append(f"YouTube Premium (${amount:.2f})")
            elif 'primo brands' in desc_lower or 'water' in desc_lower:
                patterns['subscriptions'].append(f"Water delivery service (${amount:.2f})")
            elif 'paypro' in desc_lower:
                # Try to extract more info from PayPro transactions
                if 'gym' in desc_lower or 'fitness' in desc_lower:
                    patterns['subscriptions'].append(f"Gym membership via PayPro (${amount:.2f})")
                elif 'insurance' in desc_lower:
                    patterns['subscriptions'].append(f"Insurance payment via PayPro (${amount:.2f})")
                else:
                    patterns['subscriptions'].append(f"PayPro service (${amount:.2f}) - check what this is for")
            elif 'recurring' in desc_lower:
                # Try to extract company name from recurring payments
                if 'root insurance' in desc_lower:
                    patterns['subscriptions'].append(f"Root Insurance (${amount:.2f})")
                elif 'at&t' in desc_lower or 'verizon' in desc_lower or 'tmobile' in desc_lower:
                    patterns['subscriptions'].append(f"Phone service (${amount:.2f})")
                else:
                    # Extract potential company name from description
                    words = desc.split()
                    company_hint = ""
                    for word in words:
                        if len(word) > 4 and word.upper() != word and not word.isdigit():
                            company_hint = word
                            break
                    if company_hint:
                        patterns['subscriptions'].append(f"Unknown service: {company_hint} (${amount:.2f}) - review this")
                    else:
                        patterns['subscriptions'].append(f"Unknown recurring payment (${amount:.2f}) - description: {desc[:50]}")
            else:
                # Catch-all for unidentified subscriptions
                patterns['subscriptions'].append(f"Unidentified subscription (${amount:.2f}) - {desc[:50]}")
        
        # Analyze dining patterns
        dining_transactions = df[df['Category'] == 'Dining Out & Restaurants']
        patterns['dining_frequency'] = len(dining_transactions)
        patterns['fast_food_spending'] = dining_transactions['Amount'].sum()
        
        # Compare groceries vs dining
        groceries = df[df['Category'] == 'Food & Groceries']['Amount'].sum()
        dining = df[df['Category'] == 'Dining Out & Restaurants']['Amount'].sum()
        patterns['grocery_vs_dining'] = {'groceries': groceries, 'dining': dining}
        
        # Identify top merchants
        merchant_spending = df.groupby('Description')['Amount'].sum().sort_values(ascending=False)
        patterns['specific_merchants'] = merchant_spending.head(10).to_dict()
        
        # Identify fees
        fee_transactions = df[df['Category'] == 'Fees & Charges']
        for _, txn in fee_transactions.iterrows():
            patterns['fees_paid'].append(f"{txn['Description']} (${txn['Amount']:.2f})")
        
        # Large unusual transactions
        unusual = self.identify_unusual_spending()
        for _, txn in unusual.head(3).iterrows():
            patterns['unusual_large'].append(f"${txn['Amount']:.2f} at {txn['Description']}")
        
        return patterns
    
    def generate_spending_insights(self) -> Dict:
        """Generate actionable spending insights"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        category_analysis = self.category_spending_analysis()
        trends = self.spending_trends()
        unusual = self.identify_unusual_spending()
        patterns = self.analyze_specific_spending_patterns()
        
        insights = {
            'total_spending': self.transactions_df['Amount'].sum(),
            'average_transaction': self.transactions_df['Amount'].mean(),
            'top_spending_categories': category_analysis['top_categories'],
            'spending_trend': trends['trend_change_percent'],
            'unusual_transactions_count': len(unusual),
            'recommendations': []
        }
        
        # Generate honest, specific recommendations
        monthly_summary = self.monthly_spending_summary()
        months_of_data = len(monthly_summary)
        
        # Subscription recommendations with specific service analysis
        if patterns['subscriptions']:
            total_subscription_cost = self.transactions_df[self.transactions_df['Category'] == 'Subscriptions']['Amount'].sum()
            monthly_avg = total_subscription_cost / max(months_of_data, 1)
            
            # Count how many subscriptions
            sub_count = len(patterns['subscriptions'])
            
            # Create detailed recommendation
            if sub_count > 5:
                recommendation = f"You have {sub_count} subscriptions costing ${monthly_avg:.2f}/month total. That's a lot! "
            else:
                recommendation = f"You're spending ${monthly_avg:.2f}/month on {sub_count} subscriptions: "
            
            # List specific subscriptions
            recommendation += f"{', '.join(patterns['subscriptions'])}. "
            
            # Add specific advice based on what we found
            if any('Prime' in sub for sub in patterns['subscriptions']) and any('Paramount' in sub for sub in patterns['subscriptions']):
                recommendation += "Heads up: Paramount+ is often free with Amazon Prime - you might be double-paying! "
            
            if any('Unknown' in sub or 'Unidentified' in sub or 'check what this is for' in sub for sub in patterns['subscriptions']):
                recommendation += "You have mystery charges you should investigate immediately. "
            
            if sub_count >= 3:
                recommendation += f"Cancel 2-3 services you rarely use to save ${monthly_avg * 0.4:.2f}-${monthly_avg * 0.6:.2f}/month."
            else:
                recommendation += f"Review if you're actually using these services - could save ${monthly_avg * 0.3:.2f}/month."
            
            insights['recommendations'].append(recommendation)
        
        # Dining out recommendations
        if patterns['grocery_vs_dining']['dining'] > patterns['grocery_vs_dining']['groceries']:
            dining_monthly = patterns['grocery_vs_dining']['dining'] / max(months_of_data, 1)
            potential_savings = dining_monthly * 0.4  # 40% reduction
            insights['recommendations'].append(
                f"Honest truth: You spent ${patterns['grocery_vs_dining']['dining']:.2f} dining out vs ${patterns['grocery_vs_dining']['groceries']:.2f} on groceries. "
                f"You ate out {patterns['dining_frequency']} times. Cooking at home 3-4 more times per week could save you ${potential_savings:.2f}/month."
            )
        
        # Fast food frequency
        if patterns['dining_frequency'] > 20:  # More than 20 dining transactions
            avg_per_meal = patterns['fast_food_spending'] / patterns['dining_frequency']
            insights['recommendations'].append(
                f"You ate out {patterns['dining_frequency']} times (${avg_per_meal:.2f} average per meal). "
                f"That's a lot! Reducing by just 8 meals per month could save ${avg_per_meal * 8:.2f}."
            )
        
        # Fee recommendations
        if patterns['fees_paid']:
            total_fees = self.transactions_df[self.transactions_df['Category'] == 'Fees & Charges']['Amount'].sum()
            insights['recommendations'].append(
                f"You paid ${total_fees:.2f} in fees: {', '.join(patterns['fees_paid'][:2])}. "
                f"Switch to fee-free alternatives to save this money."
            )
        
        # Large transaction review
        if patterns['unusual_large']:
            insights['recommendations'].append(
                f"Large purchases worth reviewing: {', '.join(patterns['unusual_large'][:2])}. "
                f"Make sure these were necessary and planned."
            )
        
        # Spending trend warning
        if trends['trend_change_percent'] > 15:
            insights['recommendations'].append(
                f"Warning: Your spending increased {trends['trend_change_percent']:.1f}% recently. "
                f"This trend will cost you ${trends['average_monthly'] * 0.15 * 12:.2f} extra per year if it continues."
            )
        
        return insights
    
    def calculate_potential_savings(self) -> Dict:
        """Calculate detailed, specific potential savings"""
        if self.transactions_df is None:
            raise ValueError("No transactions loaded!")
        
        category_analysis = self.category_spending_analysis()
        category_totals = category_analysis['totals']['sum']
        patterns = self.analyze_specific_spending_patterns()
        
        # Calculate monthly averages from the data
        monthly_summary = self.monthly_spending_summary()
        months_of_data = max(len(monthly_summary), 1)
        
        potential_savings = {
            'scenarios': [],
            'total_monthly_savings': 0,
            'total_annual_savings': 0
        }
        
        total_potential = 0
        
        # Specific dining savings scenario
        if 'Dining Out & Restaurants' in category_totals:
            dining_monthly = category_totals['Dining Out & Restaurants'] / months_of_data
            if dining_monthly > 50:  # Only if significant spending
                reduction_savings = dining_monthly * 0.4  # 40% reduction
                potential_savings['scenarios'].append({
                    'category': 'Dining Out & Restaurants',
                    'current_monthly': dining_monthly,
                    'savings_monthly': reduction_savings,
                    'savings_annual': reduction_savings * 12,
                    'specific_advice': f"Cook at home 3-4 more times per week instead of eating out {patterns.get('dining_frequency', 0)} times. "
                                     f"At ${dining_monthly/max(patterns.get('dining_frequency', 1), 1):.2f} per meal, this saves ${reduction_savings:.2f}/month."
                })
                total_potential += reduction_savings
        
        # Subscription savings scenario
        if 'Subscriptions' in category_totals:
            sub_monthly = category_totals['Subscriptions'] / months_of_data
            if sub_monthly > 10:  # Only if spending more than $10/month
                cancel_savings = sub_monthly * 0.35  # Cancel 35% of subscriptions
                # Create specific subscription advice
                subscription_list = patterns.get('subscriptions', [])
                if len(subscription_list) > 3:
                    advice = f"You have {len(subscription_list)} subscriptions: {', '.join(subscription_list)}. "
                    advice += f"That's quite a lot! Cancel the 2-3 you use least to save ${cancel_savings:.2f}/month. "
                    if any('Unknown' in sub or 'mystery' in sub.lower() for sub in subscription_list):
                        advice += "Start by investigating those mystery charges!"
                else:
                    advice = f"Your subscriptions: {', '.join(subscription_list)}. "
                    advice += f"Review each one monthly and cancel any you don't actively use to save ${cancel_savings:.2f}/month."
                
                potential_savings['scenarios'].append({
                    'category': 'Subscriptions',
                    'current_monthly': sub_monthly,
                    'savings_monthly': cancel_savings,
                    'savings_annual': cancel_savings * 12,
                    'specific_advice': advice
                })
                total_potential += cancel_savings
        
        # Fee elimination scenario
        if 'Fees & Charges' in category_totals:
            fees_monthly = category_totals['Fees & Charges'] / months_of_data
            if fees_monthly > 5:  # Only if paying meaningful fees
                fee_elimination = fees_monthly * 0.8  # Eliminate 80% of fees
                potential_savings['scenarios'].append({
                    'category': 'Fees & Charges',
                    'current_monthly': fees_monthly,
                    'savings_monthly': fee_elimination,
                    'savings_annual': fee_elimination * 12,
                    'specific_advice': f"You're paying ${fees_monthly:.2f}/month in avoidable fees. "
                                     f"Switch to a fee-free bank account and avoid overdrafts to save ${fee_elimination:.2f}/month."
                })
                total_potential += fee_elimination
        
        # Shopping optimization scenario
        if 'Shopping & Retail' in category_totals:
            shopping_monthly = category_totals['Shopping & Retail'] / months_of_data
            if shopping_monthly > 100:  # Only for significant shopping
                shopping_savings = shopping_monthly * 0.25  # 25% reduction through mindful shopping
                potential_savings['scenarios'].append({
                    'category': 'Shopping & Retail',
                    'current_monthly': shopping_monthly,
                    'savings_monthly': shopping_savings,
                    'savings_annual': shopping_savings * 12,
                    'specific_advice': f"Wait 24 hours before non-essential purchases over $50. "
                                     f"Use shopping lists and compare prices to reduce impulse buying by 25%, saving ${shopping_savings:.2f}/month."
                })
                total_potential += shopping_savings
        
        # Transportation optimization
        if 'Transportation' in category_totals:
            transport_monthly = category_totals['Transportation'] / months_of_data
            if transport_monthly > 100:  # Only for significant transport costs
                transport_savings = transport_monthly * 0.15  # 15% reduction
                potential_savings['scenarios'].append({
                    'category': 'Transportation',
                    'current_monthly': transport_monthly,
                    'savings_monthly': transport_savings,
                    'savings_annual': transport_savings * 12,
                    'specific_advice': f"Combine errands into single trips, carpool when possible, and maintain your car properly. "
                                     f"This can reduce your ${transport_monthly:.2f}/month transport costs by ${transport_savings:.2f}."
                })
                total_potential += transport_savings
        
        potential_savings['total_monthly_savings'] = total_potential
        potential_savings['total_annual_savings'] = total_potential * 12
        
        # Add combined scenario
        if total_potential > 0:
            potential_savings['combined_scenario'] = {
                'advice': f"If you implement all these changes - cook more, cancel unused subscriptions, avoid fees, and shop mindfully - "
                         f"you could save ${total_potential:.2f} per month (${total_potential * 12:.2f} annually). "
                         f"That's enough for a nice vacation or to boost your emergency fund!"
            }
        
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