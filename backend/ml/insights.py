"""
Insights Module - Generates personalized financial insights and recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

class InsightsGenerator:
    """
    Generates actionable financial insights and recommendations
    """
    
    def __init__(self):
        self.insights_cache = {}
    
    def analyze_spending_patterns(self, expenses_data: List[Dict]) -> Dict:
        """
        Analyze overall spending patterns
        """
        df = pd.DataFrame(expenses_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Day of week analysis
        df['day_of_week'] = df['date'].dt.day_name()
        day_spending = df.groupby('day_of_week')['amount'].sum().to_dict()
        
        # Time of month analysis
        df['day_of_month'] = df['date'].dt.day
        df['period'] = pd.cut(df['day_of_month'], 
                            bins=[0, 10, 20, 31], 
                            labels=['Early', 'Mid', 'Late'])
        period_spending = df.groupby('period')['amount'].sum().to_dict()
        
        # Payment method preferences
        payment_dist = df['payment_type'].value_counts().to_dict()
        
        # Category breakdown
        category_breakdown = df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).to_dict('index')
        
        return {
            'day_of_week_spending': day_spending,
            'period_spending': {k: float(v) for k, v in period_spending.items()},
            'payment_distribution': payment_dist,
            'category_breakdown': {
                cat: {
                    'total': round(vals['sum'], 2),
                    'count': int(vals['count']),
                    'average': round(vals['mean'], 2)
                }
                for cat, vals in category_breakdown.items()
            }
        }
    
    def generate_saving_opportunities(self, expenses_data: List[Dict]) -> List[Dict]:
        """
        Identify opportunities to save money
        """
        df = pd.DataFrame(expenses_data)
        opportunities = []
        
        # 1. High-frequency low-value purchases (coffee, snacks, etc.)
        frequent_small = df[df['amount'] < 20].groupby('category').size()
        for category, count in frequent_small.items():
            if count > 15:  # More than 15 small purchases
                total = df[(df['category'] == category) & (df['amount'] < 20)]['amount'].sum()
                monthly_savings = total * 0.3  # Assume 30% reduction possible
                
                opportunities.append({
                    'type': 'frequent_small_purchases',
                    'category': category,
                    'current_monthly': round(total, 2),
                    'potential_savings': round(monthly_savings, 2),
                    'suggestion': f"Reduce {category} expenses by bringing lunch/coffee from home",
                    'impact': 'medium' if monthly_savings > 50 else 'low'
                })
        
        # 2. Subscription optimization
        bills = df[df['category'] == 'Bills']
        if len(bills) > 0:
            avg_bill = bills['amount'].mean()
            if avg_bill > 100:
                opportunities.append({
                    'type': 'subscription_review',
                    'category': 'Bills',
                    'current_monthly': round(bills['amount'].sum(), 2),
                    'potential_savings': round(avg_bill * 0.15, 2),
                    'suggestion': "Review subscriptions and negotiate better rates for internet/phone",
                    'impact': 'high'
                })
        
        # 3. Weekend overspending
        df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6])
        weekend_spending = df[df['is_weekend']]['amount'].sum()
        weekday_spending = df[~df['is_weekend']]['amount'].sum()
        
        weekend_days = df[df['is_weekend']]['date'].nunique()
        weekday_days = df[~df['is_weekend']]['date'].nunique()
        
        if weekend_days > 0 and weekday_days > 0:
            weekend_avg = weekend_spending / weekend_days
            weekday_avg = weekday_spending / weekday_days
            
            if weekend_avg > weekday_avg * 1.5:
                monthly_savings = (weekend_avg - weekday_avg) * 8 * 0.4  # 40% reduction on 8 weekend days
                opportunities.append({
                    'type': 'weekend_spending',
                    'category': 'Entertainment',
                    'current_monthly': round(weekend_spending, 2),
                    'potential_savings': round(monthly_savings, 2),
                    'suggestion': "Plan weekend activities in advance to reduce impulse spending",
                    'impact': 'medium'
                })
        
        # 4. Expensive category recommendations
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        if len(category_totals) > 0:
            top_category = category_totals.index[0]
            top_amount = category_totals.iloc[0]
            
            if top_amount > df['amount'].sum() * 0.35:  # More than 35% of total
                opportunities.append({
                    'type': 'category_overweight',
                    'category': top_category,
                    'current_monthly': round(top_amount, 2),
                    'potential_savings': round(top_amount * 0.20, 2),
                    'suggestion': f"Focus on reducing {top_category} expenses - consider bulk buying or alternatives",
                    'impact': 'high'
                })
        
        return sorted(opportunities, key=lambda x: x['potential_savings'], reverse=True)
    
    def generate_budget_recommendations(self, expenses_data: List[Dict], 
                                    income: float = None) -> Dict:
        """
        Generate budget allocation recommendations based on 50/30/20 rule
        """
        df = pd.DataFrame(expenses_data)
        total_expenses = df['amount'].sum()
        
        # Categorize into needs, wants, savings
        needs_categories = ['Bills', 'Food', 'Healthcare', 'Transport']
        wants_categories = ['Entertainment', 'Shopping', 'Other']
        
        needs_total = df[df['category'].isin(needs_categories)]['amount'].sum()
        wants_total = df[df['category'].isin(wants_categories)]['amount'].sum()
        
        # Calculate percentages
        needs_percent = (needs_total / total_expenses * 100) if total_expenses > 0 else 0
        wants_percent = (wants_total / total_expenses * 100) if total_expenses > 0 else 0
        
        recommendations = {
            'current_allocation': {
                'needs': round(needs_percent, 1),
                'wants': round(wants_percent, 1),
                'actual_needs': round(needs_total, 2),
                'actual_wants': round(wants_total, 2)
            },
            'recommended_allocation': {
                'needs': 50,
                'wants': 30,
                'savings': 20
            },
            'adjustments_needed': []
        }
        
        if income:
            recommended_needs = income * 0.50
            recommended_wants = income * 0.30
            recommended_savings = income * 0.20
            
            if needs_total > recommended_needs:
                recommendations['adjustments_needed'].append({
                    'category': 'Needs',
                    'message': f"Reduce needs spending by ${needs_total - recommended_needs:.2f}",
                    'priority': 'high'
                })
            
            if wants_total > recommended_wants:
                recommendations['adjustments_needed'].append({
                    'category': 'Wants',
                    'message': f"Reduce discretionary spending by ${wants_total - recommended_wants:.2f}",
                    'priority': 'medium'
                })
            
            recommendations['recommended_amounts'] = {
                'needs_budget': round(recommended_needs, 2),
                'wants_budget': round(recommended_wants, 2),
                'savings_goal': round(recommended_savings, 2)
            }
        
        return recommendations
    
    def get_personalized_tips(self, expenses_data: List[Dict], 
                            user_profile: Dict = None) -> List[Dict]:
        """
        Generate personalized financial tips based on user behavior
        """
        df = pd.DataFrame(expenses_data)
        tips = []
        
        # Tip 1: Meal planning
        food_expenses = df[df['category'] == 'Food']
        if len(food_expenses) > 20:
            tips.append({
                'category': 'Food',
                'tip': "Meal prep on Sundays to reduce dining out during the week",
                'potential_impact': f"Save up to ${food_expenses['amount'].sum() * 0.25:.2f}/month",
                'difficulty': 'easy'
            })
        
        # Tip 2: Payment method optimization
        cash_usage = len(df[df['payment_type'] == 'Cash'])
        if cash_usage > len(df) * 0.3:
            tips.append({
                'category': 'Payment',
                'tip': "Use cashback credit cards for purchases to earn 1-3% back",
                'potential_impact': f"Earn ${df['amount'].sum() * 0.02:.2f}/month in rewards",
                'difficulty': 'easy'
            })
        
        # Tip 3: Bulk buying for frequent purchases
        frequent_categories = df['category'].value_counts()
        for cat, count in frequent_categories.items():
            if count > 15 and cat in ['Food', 'Healthcare']:
                tips.append({
                    'category': cat,
                    'tip': f"Buy {cat.lower()} items in bulk to save 10-15%",
                    'potential_impact': f"Save ${df[df['category'] == cat]['amount'].sum() * 0.12:.2f}/month",
                    'difficulty': 'medium'
                })
                break
        
        # Tip 4: Automated savings
        tips.append({
            'category': 'Savings',
            'tip': "Set up automatic transfers to savings account on payday",
            'potential_impact': "Build emergency fund and reach goals faster",
            'difficulty': 'easy'
        })
        
        # Tip 5: Price comparison
        shopping_expenses = df[df['category'] == 'Shopping']
        if len(shopping_expenses) > 5:
            tips.append({
                'category': 'Shopping',
                'tip': "Use price comparison apps before major purchases",
                'potential_impact': f"Save up to ${shopping_expenses['amount'].sum() * 0.15:.2f}/month",
                'difficulty': 'easy'
            })
        
        # Tip 6: Energy efficiency
        bills = df[df['category'] == 'Bills']
        if len(bills) > 0 and bills['amount'].sum() > 200:
            tips.append({
                'category': 'Bills',
                'tip': "Switch to LED bulbs and unplug devices to reduce electricity bills",
                'potential_impact': f"Save up to ${bills['amount'].sum() * 0.10:.2f}/month",
                'difficulty': 'easy'
            })
        
        # Tip 7: Transportation optimization
        transport = df[df['category'] == 'Transport']
        if len(transport) > 10:
            tips.append({
                'category': 'Transport',
                'tip': "Consider carpooling or public transport for daily commute",
                'potential_impact': f"Save up to ${transport['amount'].sum() * 0.30:.2f}/month",
                'difficulty': 'medium'
            })
        
        # Tip 8: Entertainment alternatives
        entertainment = df[df['category'] == 'Entertainment']
        if len(entertainment) > 8:
            tips.append({
                'category': 'Entertainment',
                'tip': "Use free entertainment options like libraries, parks, and community events",
                'potential_impact': f"Save up to ${entertainment['amount'].sum() * 0.40:.2f}/month",
                'difficulty': 'easy'
            })
        
        return tips[:5]  # Return top 5 tips
    
    def calculate_financial_health_score(self, expenses_data: List[Dict],
                                        income: float = None,
                                        savings: float = None) -> Dict:
        """
        Calculate an overall financial health score (0-100)
        """
        df = pd.DataFrame(expenses_data)
        score_components = {}
        
        # Component 1: Spending consistency (0-25 points)
        daily_spending = df.groupby(df['date'].dt.date)['amount'].sum()
        if len(daily_spending) > 0 and daily_spending.mean() > 0:
            cv = daily_spending.std() / daily_spending.mean()
            consistency_score = max(0, 25 - (cv * 10))
        else:
            consistency_score = 15
        score_components['spending_consistency'] = round(consistency_score, 2)
        
        # Component 2: Budget adherence (0-25 points)
        if income:
            expense_ratio = df['amount'].sum() / income
            adherence_score = max(0, 25 - (expense_ratio * 20))
        else:
            adherence_score = 15  # Default if no income data
        score_components['budget_adherence'] = round(adherence_score, 2)
        
        # Component 3: Savings rate (0-30 points)
        if income and savings:
            savings_rate = savings / income
            savings_score = min(30, savings_rate * 100)
        else:
            savings_score = 10  # Default
        score_components['savings_rate'] = round(savings_score, 2)
        
        # Component 4: Expense diversity (0-20 points)
        category_dist = df.groupby('category')['amount'].sum()
        if len(category_dist) > 0:
            # Penalize if one category dominates
            max_category_pct = category_dist.max() / category_dist.sum()
            diversity_score = max(0, 20 - (max_category_pct * 30))
        else:
            diversity_score = 10
        score_components['expense_diversity'] = round(diversity_score, 2)
        
        total_score = sum(score_components.values())
        
        # Determine health level
        if total_score >= 80:
            health_level = 'Excellent'
            color = '#22c55e'
        elif total_score >= 60:
            health_level = 'Good'
            color = '#3b82f6'
        elif total_score >= 40:
            health_level = 'Fair'
            color = '#FFA500'
        else:
            health_level = 'Needs Improvement'
            color = '#D2042D'
        
        return {
            'total_score': round(total_score, 1),
            'health_level': health_level,
            'color': color,
            'components': score_components,
            'recommendations': self._get_score_recommendations(score_components)
        }
    
    def _get_score_recommendations(self, components: Dict) -> List[str]:
        """Get recommendations based on low-scoring components"""
        recommendations = []
        
        if components['spending_consistency'] < 15:
            recommendations.append("Work on maintaining consistent daily spending")
        if components['budget_adherence'] < 15:
            recommendations.append("Reduce overall expenses to improve budget adherence")
        if components['savings_rate'] < 15:
            recommendations.append("Increase your monthly savings rate")
        if components['expense_diversity'] < 10:
            recommendations.append("Balance spending across different categories")
        
        return recommendations
    
    def identify_spending_trends(self, expenses_data: List[Dict]) -> Dict:
        """
        Identify spending trends over time
        """
        df = pd.DataFrame(expenses_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Monthly trends
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_spending = df.groupby('year_month')['amount'].sum()
        
        trends = {
            'monthly_spending': {
                str(k): round(v, 2) for k, v in monthly_spending.items()
            },
            'increasing_categories': [],
            'decreasing_categories': [],
            'stable_categories': []
        }
        
        # Category trends
        for category in df['category'].unique():
            cat_data = df[df['category'] == category].groupby('year_month')['amount'].sum()
            
            if len(cat_data) >= 2:
                # Simple trend detection: compare first half vs second half
                mid_point = len(cat_data) // 2
                first_half_avg = cat_data.iloc[:mid_point].mean()
                second_half_avg = cat_data.iloc[mid_point:].mean()
                
                if second_half_avg > first_half_avg * 1.15:
                    trends['increasing_categories'].append({
                        'category': category,
                        'change_percent': round(((second_half_avg - first_half_avg) / first_half_avg) * 100, 1)
                    })
                elif second_half_avg < first_half_avg * 0.85:
                    trends['decreasing_categories'].append({
                        'category': category,
                        'change_percent': round(((second_half_avg - first_half_avg) / first_half_avg) * 100, 1)
                    })
                else:
                    trends['stable_categories'].append(category)
        
        return trends
    
    def compare_with_averages(self, expenses_data: List[Dict], 
                            user_income: float = None) -> Dict:
        """
        Compare user spending with national/regional averages
        """
        df = pd.DataFrame(expenses_data)
        total_spending = df['amount'].sum()
        
        # Average spending benchmarks (monthly, in USD)
        national_averages = {
            'Food': 550,
            'Transport': 350,
            'Shopping': 200,
            'Bills': 400,
            'Entertainment': 150,
            'Healthcare': 300,
            'Other': 100
        }
        
        comparisons = {}
        
        for category in df['category'].unique():
            user_spending = df[df['category'] == category]['amount'].sum()
            benchmark = national_averages.get(category, 100)
            
            difference = user_spending - benchmark
            percent_diff = (difference / benchmark) * 100 if benchmark > 0 else 0
            
            comparisons[category] = {
                'user_spending': round(user_spending, 2),
                'average_spending': benchmark,
                'difference': round(difference, 2),
                'percent_difference': round(percent_diff, 1),
                'status': 'above' if difference > 0 else 'below'
            }
        
        return {
            'category_comparisons': comparisons,
            'total_user_spending': round(total_spending, 2),
            'total_average_spending': sum(national_averages.values()),
            'overall_status': 'above_average' if total_spending > sum(national_averages.values()) else 'below_average'
        }

# Singleton instance
insights_gen = InsightsGenerator()

# Helper functions
def get_spending_insights(expenses_data: List[Dict]) -> Dict:
    """Get comprehensive spending insights"""
    return {
        'patterns': insights_gen.analyze_spending_patterns(expenses_data),
        'opportunities': insights_gen.generate_saving_opportunities(expenses_data),
        'tips': insights_gen.get_personalized_tips(expenses_data),
        'trends': insights_gen.identify_spending_trends(expenses_data)
    }

def get_budget_recommendations(expenses_data: List[Dict], income: float = None) -> Dict:
    """Get budget allocation recommendations"""
    return insights_gen.generate_budget_recommendations(expenses_data, income)

def get_financial_health_score(expenses_data: List[Dict], 
                            income: float = None,
                            savings: float = None) -> Dict:
    """Calculate financial health score"""
    return insights_gen.calculate_financial_health_score(expenses_data, income, savings)

def compare_spending_with_benchmarks(expenses_data: List[Dict], 
                                    income: float = None) -> Dict:
    """Compare user spending with national averages"""
    return insights_gen.compare_with_averages(expenses_data, income)