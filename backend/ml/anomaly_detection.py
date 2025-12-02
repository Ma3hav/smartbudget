"""
Anomaly Detection Module - Detects unusual spending patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from scipy import stats

class AnomalyDetector:
    """
    Detects spending anomalies and unusual patterns
    """
    
    def __init__(self, threshold_sigma=2.5):
        """
        Args:
            threshold_sigma: Number of standard deviations for anomaly threshold
        """
        self.threshold_sigma = threshold_sigma
    
    def detect_amount_anomalies(self, expenses_data: List[Dict]) -> List[Dict]:
        """
        Detect unusually high expense amounts
        
        Uses Z-score method to identify outliers
        """
        if len(expenses_data) < 10:
            return []
        
        df = pd.DataFrame(expenses_data)
        
        # Calculate z-scores for amounts
        df['z_score'] = stats.zscore(df['amount'])
        
        # Identify anomalies
        anomalies = df[df['z_score'].abs() > self.threshold_sigma]
        
        results = []
        for _, row in anomalies.iterrows():
            expected_amount = df['amount'].mean()
            deviation = row['amount'] - expected_amount
            
            results.append({
                'id': row.get('_id', row.get('id')),
                'date': row['date'],
                'amount': float(row['amount']),
                'category': row.get('category', 'Unknown'),
                'expected_amount': round(expected_amount, 2),
                'deviation': round(deviation, 2),
                'severity': 'high' if row['z_score'] > 3 else 'medium',
                'message': f"Unusual {row.get('category', 'expense')}: ${row['amount']:.2f} (expected ~${expected_amount:.2f})"
            })
        
        return results
    
    def detect_category_anomalies(self, expenses_data: List[Dict], 
                                time_window_days=30) -> List[Dict]:
        """
        Detect unusual spending in specific categories
        """
        df = pd.DataFrame(expenses_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get recent expenses
        cutoff_date = df['date'].max() - timedelta(days=time_window_days)
        recent_df = df[df['date'] > cutoff_date]
        
        # Historical baseline (older data)
        historical_df = df[df['date'] <= cutoff_date]
        
        if len(historical_df) < 10:
            return []
        
        anomalies = []
        
        for category in df['category'].unique():
            recent_cat = recent_df[recent_df['category'] == category]['amount'].sum()
            historical_cat = historical_df[historical_df['category'] == category]
            
            if len(historical_cat) == 0:
                continue
            
            historical_mean = historical_cat['amount'].sum() / (len(historical_df['date'].unique()) / 30)
            historical_std = historical_cat['amount'].std()
            
            # Check if recent spending is anomalous
            if historical_std > 0:
                z_score = (recent_cat - historical_mean) / (historical_std + 1)
                
                if abs(z_score) > self.threshold_sigma:
                    percent_change = ((recent_cat - historical_mean) / historical_mean) * 100
                    
                    anomalies.append({
                        'category': category,
                        'current_spending': round(recent_cat, 2),
                        'historical_average': round(historical_mean, 2),
                        'percent_change': round(percent_change, 2),
                        'severity': 'high' if abs(percent_change) > 50 else 'medium',
                        'message': f"{category} spending {'increased' if percent_change > 0 else 'decreased'} by {abs(percent_change):.1f}%"
                    })
        
        return sorted(anomalies, key=lambda x: abs(x['percent_change']), reverse=True)
    
    def detect_frequency_anomalies(self, expenses_data: List[Dict]) -> List[Dict]:
        """
        Detect unusual spending frequency (too many transactions)
        """
        df = pd.DataFrame(expenses_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Count transactions per day
        daily_counts = df.groupby(df['date'].dt.date).size()
        
        mean_count = daily_counts.mean()
        std_count = daily_counts.std()
        
        anomalies = []
        
        for date, count in daily_counts.items():
            if std_count > 0:
                z_score = (count - mean_count) / std_count
                
                if z_score > self.threshold_sigma:
                    anomalies.append({
                        'date': str(date),
                        'transaction_count': int(count),
                        'expected_count': round(mean_count, 1),
                        'severity': 'high' if z_score > 3 else 'medium',
                        'message': f"Unusual number of transactions on {date}: {count} (expected ~{mean_count:.0f})"
                    })
        
        return anomalies
    
    def detect_budget_overrun(self, expenses_data: List[Dict], 
                            monthly_budget: float) -> Dict:
        """
        Check if spending is on track to exceed budget
        """
        df = pd.DataFrame(expenses_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Get current month expenses
        current_month = df['date'].max().month
        current_year = df['date'].max().year
        
        month_expenses = df[
            (df['date'].dt.month == current_month) &
            (df['date'].dt.year == current_year)
        ]
        
        total_spent = month_expenses['amount'].sum()
        days_passed = df['date'].max().day
        days_in_month = 30  # Simplified
        
        # Project month-end spending
        daily_average = total_spent / days_passed if days_passed > 0 else 0
        projected_total = daily_average * days_in_month
        
        is_overrun = projected_total > monthly_budget
        percent_over = ((projected_total - monthly_budget) / monthly_budget) * 100 if is_overrun else 0
        
        return {
            'is_overrun_risk': is_overrun,
            'total_spent': round(total_spent, 2),
            'monthly_budget': monthly_budget,
            'remaining_budget': round(monthly_budget - total_spent, 2),
            'projected_total': round(projected_total, 2),
            'projected_overage': round(projected_total - monthly_budget, 2) if is_overrun else 0,
            'percent_over_budget': round(percent_over, 2) if is_overrun else 0,
            'days_remaining': days_in_month - days_passed,
            'recommended_daily_limit': round((monthly_budget - total_spent) / (days_in_month - days_passed), 2) if days_passed < days_in_month else 0,
            'severity': 'high' if percent_over > 20 else 'medium' if percent_over > 10 else 'low',
            'message': f"On track to exceed budget by ${projected_total - monthly_budget:.2f}" if is_overrun else "Spending is within budget"
        }
    
    def get_all_anomalies(self, expenses_data: List[Dict], 
                        monthly_budget: float = None) -> Dict:
        """
        Get all detected anomalies in one call
        """
        return {
            'amount_anomalies': self.detect_amount_anomalies(expenses_data),
            'category_anomalies': self.detect_category_anomalies(expenses_data),
            'frequency_anomalies': self.detect_frequency_anomalies(expenses_data),
            'budget_status': self.detect_budget_overrun(expenses_data, monthly_budget) if monthly_budget else None
        }

# Singleton instance
detector = AnomalyDetector()

# Helper functions
def check_spending_anomalies(expenses_data: List[Dict], 
                            monthly_budget: float = None) -> Dict:
    """Check for all types of spending anomalies"""
    return detector.get_all_anomalies(expenses_data, monthly_budget)

def check_budget_status(expenses_data: List[Dict], 
                    monthly_budget: float) -> Dict:
    """Check if user is on track with budget"""
    return detector.detect_budget_overrun(expenses_data, monthly_budget)