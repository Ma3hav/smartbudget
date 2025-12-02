"""
Forecasting Module - Predicts future expenses using ML models
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from typing import Dict, List, Tuple

class ExpenseForecaster:
    """
    Handles expense forecasting using machine learning
    """
    
    def __init__(self, model_path='ml/forecast_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.label_encoders = {}
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model if exists"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data['model']
                    self.label_encoders = saved_data['label_encoders']
                    self.feature_names = saved_data['feature_names']
                print(f"✅ Model loaded from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                self.model = None
        else:
            print("⚠️ No pre-trained model found. Training new model...")
            self.train_default_model()
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'label_encoders': self.label_encoders,
                    'feature_names': self.feature_names
                }, f)
            print(f"✅ Model saved to {self.model_path}")
        except Exception as e:
            print(f"❌ Error saving model: {e}")
    
    def prepare_features(self, expenses_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features from expense data
        
        Features:
        - day_of_week
        - day_of_month
        - month
        - category
        - payment_type
        - rolling averages
        """
        df = expenses_df.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Sort by date
        df = df.sort_values('date')
        
        # Rolling statistics (7-day and 30-day windows)
        df['rolling_mean_7d'] = df['amount'].rolling(window=7, min_periods=1).mean()
        df['rolling_std_7d'] = df['amount'].rolling(window=7, min_periods=1).std().fillna(0)
        df['rolling_mean_30d'] = df['amount'].rolling(window=30, min_periods=1).mean()
        
        # Lag features (previous expenses)
        df['lag_1'] = df['amount'].shift(1).fillna(df['amount'].mean())
        df['lag_7'] = df['amount'].shift(7).fillna(df['amount'].mean())
        
        # Encode categorical variables
        for col in ['category', 'payment_type']:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        return df
    
    def train_model(self, expenses_data: List[Dict]) -> Dict:
        """
        Train forecasting model on historical expense data
        
        Args:
            expenses_data: List of expense dictionaries
            
        Returns:
            Training metrics
        """
        if len(expenses_data) < 30:
            return {
                'success': False,
                'message': 'Need at least 30 expenses to train model'
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(expenses_data)
        
        # Prepare features
        df_features = self.prepare_features(df)
        
        # Define feature columns
        feature_cols = [
            'day_of_week', 'day_of_month', 'month', 'is_weekend', 'week_of_year',
            'rolling_mean_7d', 'rolling_std_7d', 'rolling_mean_30d',
            'lag_1', 'lag_7', 'category_encoded', 'payment_type_encoded'
        ]
        
        # Remove rows with NaN
        df_features = df_features.dropna(subset=feature_cols + ['amount'])
        
        X = df_features[feature_cols]
        y = df_features['amount']
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X, y)
        self.feature_names = feature_cols
        
        # Calculate training metrics
        train_score = self.model.score(X, y)
        
        # Save model
        self.save_model()
        
        return {
            'success': True,
            'r2_score': train_score,
            'n_samples': len(df_features),
            'feature_importance': dict(zip(feature_cols, self.model.feature_importances_))
        }
    
    def train_default_model(self):
        """Train model with synthetic data for initial setup"""
        # Generate synthetic expense data
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', end='2024-11-28', freq='D')
        
        categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare', 'Other']
        payment_types = ['Credit Card', 'Debit Card', 'Cash', 'UPI', 'Bank Transfer']
        
        synthetic_data = []
        for date in dates:
            n_expenses = np.random.randint(0, 4)
            for _ in range(n_expenses):
                amount = np.random.lognormal(mean=3.5, sigma=0.8)
                synthetic_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': np.random.choice(categories),
                    'payment_type': np.random.choice(payment_types)
                })
        
        self.train_model(synthetic_data)
    
    def predict_next_month(self, expenses_data: List[Dict]) -> Dict:
        """
        Predict expenses for the next 30 days
        
        Args:
            expenses_data: Historical expense data
            
        Returns:
            Dictionary with predictions and confidence intervals
        """
        if not self.model:
            return {
                'success': False,
                'message': 'Model not trained'
            }
        
        # Convert to DataFrame and prepare features
        df = pd.DataFrame(expenses_data)
        df_features = self.prepare_features(df)
        
        # Get the last date
        last_date = df_features['date'].max()
        
        # Generate future dates (next 30 days)
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=30,
            freq='D'
        )
        
        predictions = []
        
        for future_date in future_dates:
            # Create feature vector for future date
            features = {
                'day_of_week': future_date.dayofweek,
                'day_of_month': future_date.day,
                'month': future_date.month,
                'is_weekend': 1 if future_date.dayofweek in [5, 6] else 0,
                'week_of_year': future_date.isocalendar()[1],
                'rolling_mean_7d': df_features['amount'].tail(7).mean(),
                'rolling_std_7d': df_features['amount'].tail(7).std(),
                'rolling_mean_30d': df_features['amount'].tail(30).mean(),
                'lag_1': df_features['amount'].iloc[-1],
                'lag_7': df_features['amount'].iloc[-7] if len(df_features) >= 7 else df_features['amount'].mean(),
                'category_encoded': 0,  # Default category
                'payment_type_encoded': 0  # Default payment type
            }
            
            X_pred = pd.DataFrame([features])[self.feature_names]
            
            # Predict
            predicted_amount = self.model.predict(X_pred)[0]
            
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_amount': round(predicted_amount, 2),
                'confidence_lower': round(predicted_amount * 0.85, 2),
                'confidence_upper': round(predicted_amount * 1.15, 2)
            })
        
        # Calculate monthly summary
        total_predicted = sum(p['predicted_amount'] for p in predictions)
        
        return {
            'success': True,
            'predictions': predictions,
            'monthly_summary': {
                'total_predicted': round(total_predicted, 2),
                'average_daily': round(total_predicted / 30, 2),
                'confidence_range': {
                    'lower': round(total_predicted * 0.85, 2),
                    'upper': round(total_predicted * 1.15, 2)
                }
            }
        }
    
    def predict_category_spending(self, expenses_data: List[Dict], 
                                category: str, days: int = 30) -> Dict:
        """
        Predict spending for a specific category
        
        Args:
            expenses_data: Historical expense data
            category: Category to predict
            days: Number of days to predict
            
        Returns:
            Category-specific predictions
        """
        df = pd.DataFrame(expenses_data)
        category_df = df[df['category'] == category]
        
        if len(category_df) < 10:
            return {
                'success': False,
                'message': f'Not enough data for category: {category}'
            }
        
        # Calculate historical statistics
        avg_amount = category_df['amount'].mean()
        std_amount = category_df['amount'].std()
        frequency = len(category_df) / len(df)
        
        # Predict
        expected_transactions = int(frequency * days)
        predicted_total = avg_amount * expected_transactions
        
        return {
            'success': True,
            'category': category,
            'predicted_total': round(predicted_total, 2),
            'expected_transactions': expected_transactions,
            'average_per_transaction': round(avg_amount, 2),
            'confidence_range': {
                'lower': round(predicted_total - (std_amount * np.sqrt(expected_transactions)), 2),
                'upper': round(predicted_total + (std_amount * np.sqrt(expected_transactions)), 2)
            }
        }

# Singleton instance
forecaster = ExpenseForecaster()

# Helper functions
def get_expense_forecast(expenses_data: List[Dict]) -> Dict:
    """Get 30-day expense forecast"""
    return forecaster.predict_next_month(expenses_data)

def get_category_forecast(expenses_data: List[Dict], category: str) -> Dict:
    """Get category-specific forecast"""
    return forecaster.predict_category_spending(expenses_data, category)

def train_forecasting_model(expenses_data: List[Dict]) -> Dict:
    """Train the forecasting model"""
    return forecaster.train_model(expenses_data)