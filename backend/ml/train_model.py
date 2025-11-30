"""
Model Training Script - Train and evaluate forecasting models
"""

import pandas as pd
import numpy as np
from forecasting import ExpenseForecaster
from datetime import datetime, timedelta
import json
import os

def generate_training_data(n_months=12):
    """
    Generate realistic synthetic training data
    """
    np.random.seed(42)
    
    start_date = datetime.now() - timedelta(days=n_months * 30)
    dates = pd.date_range(start=start_date, periods=n_months * 30, freq='D')
    
    categories = {
        'Food': (30, 80, 0.8),  # (min, max, probability)
        'Transport': (10, 50, 0.6),
        'Shopping': (20, 200, 0.3),
        'Bills': (50, 300, 0.15),
        'Entertainment': (15, 100, 0.4),
        'Healthcare': (20, 150, 0.2),
        'Other': (10, 50, 0.3)
    }
    
    payment_types = ['Credit Card', 'Debit Card', 'Cash', 'UPI', 'Bank Transfer']
    
    training_data = []
    
    for date in dates:
        # Weekend multiplier
        weekend_mult = 1.3 if date.dayofweek in [5, 6] else 1.0
        
        # Month-end multiplier
        day_mult = 1.2 if date.day > 25 else 1.0
        
        for category, (min_amt, max_amt, prob) in categories.items():
            if np.random.random() < prob * weekend_mult:
                base_amount = np.random.uniform(min_amt, max_amt)
                amount = base_amount * weekend_mult * day_mult
                
                training_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': category,
                    'payment_type': np.random.choice(payment_types),
                    'notes': f'Sample {category} expense'
                })
    
    return training_data

def train_and_evaluate():
    """
    Train the forecasting model and evaluate performance
    """
    print("🚀 Starting model training...")
    print("=" * 60)
    
    # Generate training data
    print("\n📊 Generating training data...")
    training_data = generate_training_data(n_months=12)
    print(f"✅ Generated {len(training_data)} expense records")
    
    # Initialize forecaster
    forecaster = ExpenseForecaster()
    
    # Train model
    print("\n🎯 Training forecasting model...")
    results = forecaster.train_model(training_data)
    
    if results['success']:
        print(f"\n✅ Model trained successfully!")
        print(f"   📈 R² Score: {results['r2_score']:.4f}")
        print(f"   📊 Training samples: {results['n_samples']}")
        print(f"\n🔍 Top 5 Feature Importances:")
        for feature, importance in sorted(
            results['feature_importance'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]:
            print(f"   - {feature:25s}: {importance:.4f}")
    else:
        print(f"❌ Training failed: {results['message']}")
        return
    
    # Test predictions
    print("\n" + "=" * 60)
    print("🔮 Testing predictions...")
    predictions = forecaster.predict_next_month(training_data)
    
    if predictions['success']:
        print(f"\n✅ Prediction successful!")
        summary = predictions['monthly_summary']
        print(f"   💰 Predicted monthly total: ${summary['total_predicted']:.2f}")
        print(f"   📅 Average daily: ${summary['average_daily']:.2f}")
        print(f"   📊 Confidence range: ${summary['confidence_range']['lower']:.2f} - ${summary['confidence_range']['upper']:.2f}")
        
        print(f"\n📅 Sample predictions (first 7 days):")
        for pred in predictions['predictions'][:7]:
            print(f"   - {pred['date']}: ${pred['predicted_amount']:.2f}")
    
    print("\n" + "=" * 60)
    print("✨ Training complete! Model saved to ml/forecast_model.pkl")
    print("=" * 60)

if __name__ == '__main__':
    train_and_evaluate()