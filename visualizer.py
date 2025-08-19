import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from spending_analyzer import SpendingAnalyzer


class ExpenseVisualizer:
    def __init__(self, analyzer: SpendingAnalyzer):
        self.analyzer = analyzer
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_category_breakdown(self, save_path: str = None, interactive: bool = False):
        """Create pie chart of spending by category"""
        category_analysis = self.analyzer.category_spending_analysis()
        
        if interactive:
            fig = px.pie(
                values=category_analysis['percentages'].values,
                names=category_analysis['percentages'].index,
                title="Spending Breakdown by Category"
            )
            fig.show()
            if save_path:
                fig.write_html(save_path.replace('.png', '.html'))
        else:
            plt.figure(figsize=(10, 8))
            plt.pie(category_analysis['percentages'].values, 
                   labels=category_analysis['percentages'].index,
                   autopct='%1.1f%%')
            plt.title("Spending Breakdown by Category")
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.show()
    
    def plot_monthly_trends(self, save_path: str = None, interactive: bool = False):
        """Create line chart of monthly spending trends"""
        trends = self.analyzer.spending_trends()
        monthly_data = trends['monthly_totals']
        
        if interactive:
            fig = px.line(
                x=monthly_data.index.astype(str),
                y=monthly_data.values,
                title="Monthly Spending Trends",
                labels={'x': 'Month', 'y': 'Amount ($)'}
            )
            fig.show()
            if save_path:
                fig.write_html(save_path.replace('.png', '.html'))
        else:
            plt.figure(figsize=(12, 6))
            plt.plot(monthly_data.index.astype(str), monthly_data.values, marker='o')
            plt.title("Monthly Spending Trends")
            plt.xlabel("Month")
            plt.ylabel("Amount ($)")
            plt.xticks(rotation=45)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.show()
    
    def plot_category_trends(self, save_path: str = None, interactive: bool = False):
        """Create stacked area chart of category spending over time"""
        monthly_summary = self.analyzer.monthly_spending_summary()
        
        if interactive:
            fig = px.area(
                monthly_summary.reset_index(),
                x='Month',
                y=monthly_summary.columns[:-1],  # Exclude 'Total' column
                title="Category Spending Trends Over Time"
            )
            fig.show()
            if save_path:
                fig.write_html(save_path.replace('.png', '.html'))
        else:
            plt.figure(figsize=(14, 8))
            plt.stackplot(monthly_summary.index.astype(str), 
                         *[monthly_summary[col] for col in monthly_summary.columns[:-1]],
                         labels=monthly_summary.columns[:-1])
            plt.title("Category Spending Trends Over Time")
            plt.xlabel("Month")
            plt.ylabel("Amount ($)")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.show()
    
    def plot_spending_heatmap(self, save_path: str = None):
        """Create heatmap of spending by category and month"""
        monthly_summary = self.analyzer.monthly_spending_summary()
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(monthly_summary.iloc[:, :-1].T,  # Exclude 'Total' column
                   annot=True, fmt='.0f', cmap='YlOrRd')
        plt.title("Spending Heatmap by Category and Month")
        plt.xlabel("Month")
        plt.ylabel("Category")
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.show()
    
    def plot_unusual_transactions(self, save_path: str = None):
        """Create scatter plot of unusual transactions"""
        unusual = self.analyzer.identify_unusual_spending()
        
        if len(unusual) == 0:
            print("No unusual transactions found!")
            return
        
        plt.figure(figsize=(12, 6))
        for category in unusual['Category'].unique():
            cat_data = unusual[unusual['Category'] == category]
            plt.scatter(cat_data['Date'], cat_data['Amount'], 
                       label=category, alpha=0.7, s=60)
        
        plt.title("Unusual Transactions by Category")
        plt.xlabel("Date")
        plt.ylabel("Amount ($)")
        plt.legend()
        plt.xticks(rotation=45)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.show()
    
    def plot_savings_potential(self, save_path: str = None, interactive: bool = False):
        """Create bar chart of potential savings by category"""
        potential_savings = self.analyzer.calculate_potential_savings()
        
        # Extract data for plotting
        categories = []
        current_spending = []
        potential_monthly_savings = []
        
        for category, data in potential_savings.items():
            if isinstance(data, dict) and 'monthly_spending' in data:
                categories.append(category)
                current_spending.append(data['monthly_spending'])
                potential_monthly_savings.append(data['potential_monthly_savings'])
        
        if interactive:
            fig = go.Figure(data=[
                go.Bar(name='Current Spending', x=categories, y=current_spending),
                go.Bar(name='Potential Savings', x=categories, y=potential_monthly_savings)
            ])
            fig.update_layout(
                title="Current Spending vs Potential Monthly Savings",
                barmode='group'
            )
            fig.show()
            if save_path:
                fig.write_html(save_path.replace('.png', '.html'))
        else:
            x = range(len(categories))
            width = 0.35
            
            plt.figure(figsize=(12, 6))
            plt.bar([i - width/2 for i in x], current_spending, width, 
                   label='Current Spending', alpha=0.8)
            plt.bar([i + width/2 for i in x], potential_monthly_savings, width, 
                   label='Potential Savings', alpha=0.8)
            
            plt.title("Current Spending vs Potential Monthly Savings")
            plt.xlabel("Category")
            plt.ylabel("Amount ($)")
            plt.xticks(x, categories, rotation=45)
            plt.legend()
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.show()
    
    def create_dashboard(self, save_path: str = None):
        """Create a comprehensive dashboard with multiple visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Category breakdown (pie chart)
        category_analysis = self.analyzer.category_spending_analysis()
        axes[0, 0].pie(category_analysis['percentages'].values, 
                      labels=category_analysis['percentages'].index,
                      autopct='%1.1f%%')
        axes[0, 0].set_title("Spending by Category")
        
        # Monthly trends (line chart)
        trends = self.analyzer.spending_trends()
        monthly_data = trends['monthly_totals']
        axes[0, 1].plot(monthly_data.index.astype(str), monthly_data.values, marker='o')
        axes[0, 1].set_title("Monthly Spending Trends")
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Category comparison (bar chart)
        category_totals = category_analysis['totals']['sum'].sort_values(ascending=False)
        axes[1, 0].bar(category_totals.index, category_totals.values)
        axes[1, 0].set_title("Total Spending by Category")
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Savings potential
        potential_savings = self.analyzer.calculate_potential_savings()
        categories = []
        savings = []
        for category, data in potential_savings.items():
            if isinstance(data, dict) and 'potential_monthly_savings' in data:
                categories.append(category)
                savings.append(data['potential_monthly_savings'])
        
        axes[1, 1].bar(categories, savings)
        axes[1, 1].set_title("Potential Monthly Savings")
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        plt.show()


def main():
    """Example usage"""
    print("Expense Visualizer Ready!")
    print("\nUsage:")
    print("1. analyzer = SpendingAnalyzer()")
    print("2. analyzer.load_transactions('your_data.csv')")
    print("3. visualizer = ExpenseVisualizer(analyzer)")
    print("4. visualizer.create_dashboard()")


if __name__ == "__main__":
    main()