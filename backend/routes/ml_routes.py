"""
ML Routes - Machine learning powered insights and predictions
FIXED VERSION with proper error handling
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.expense_service import ExpenseService
from ml.forecasting import get_expense_forecast, get_category_forecast
from ml.anomaly_detection import check_spending_anomalies, check_budget_status
from ml.insights import (
    get_spending_insights,
    get_budget_recommendations,
    get_financial_health_score,
    compare_spending_with_benchmarks
)

bp = Blueprint('ml', __name__)
expense_service = ExpenseService()


@bp.route('/forecast', methods=['GET'])
@jwt_required()
def get_forecast():
    """
    Get 30-day expense forecast using ML
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Forecast predictions
        - 400: Insufficient data for prediction
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        # ✅ FIXED: Separate error handling
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses',
                'message': result.get('message', 'Unable to fetch expense data')
            }), 400
        
        # ✅ FIXED: Check data sufficiency separately
        if len(result['expenses']) < 30:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for prediction',
                'message': 'At least 30 expenses required for forecasting',
                'current_count': len(result['expenses']),
                'required_count': 30
            }), 400
        
        # Get forecast
        forecast = get_expense_forecast(result['expenses'])
        
        return jsonify(forecast), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Forecast failed: {str(e)}'
        }), 500


@bp.route('/forecast/category/<category>', methods=['GET'])
@jwt_required()
def get_category_forecast_route(category):
    """
    Get category-specific expense forecast
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - category (str): Category name
    
    Query Parameters:
        - days (int, optional): Number of days to forecast (default: 30)
    
    Returns:
        - 200: Category forecast
        - 400: Insufficient data
    """
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': 'Invalid days parameter',
                'message': 'Days must be between 1 and 365'
            }), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # Get category forecast
        forecast = get_category_forecast(result['expenses'], category, days)
        
        if forecast['success']:
            return jsonify(forecast), 200
        else:
            return jsonify({
                'success': False,
                'error': forecast['message']
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Category forecast failed: {str(e)}'
        }), 500


@bp.route('/anomalies', methods=['GET'])
@jwt_required()
def detect_anomalies():
    """
    Detect spending anomalies and unusual patterns
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - monthly_budget (float, optional): Monthly budget for comparison
    
    Returns:
        - 200: Detected anomalies
    """
    try:
        user_id = get_jwt_identity()
        monthly_budget = request.args.get('monthly_budget', type=float)
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Handle case with no expenses
        if len(result['expenses']) == 0:
            return jsonify({
                'success': True,
                'amount_anomalies': [],
                'category_anomalies': [],
                'frequency_anomalies': [],
                'budget_status': None,
                'message': 'No expenses to analyze'
            }), 200
        
        # Check anomalies
        anomalies = check_spending_anomalies(result['expenses'], monthly_budget)
        
        return jsonify(anomalies), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Anomaly detection failed: {str(e)}'
        }), 500


@bp.route('/budget-status', methods=['GET'])
@jwt_required()
def get_budget_status():
    """
    Check if user is on track with budget
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - monthly_budget (float): Monthly budget amount
    
    Returns:
        - 200: Budget status and projections
        - 400: Monthly budget required
    """
    try:
        user_id = get_jwt_identity()
        monthly_budget = request.args.get('monthly_budget', type=float)
        
        if not monthly_budget:
            return jsonify({
                'success': False,
                'error': 'Monthly budget parameter required'
            }), 400
        
        if monthly_budget <= 0:
            return jsonify({
                'success': False,
                'error': 'Monthly budget must be greater than 0'
            }), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Handle empty expenses
        if len(result['expenses']) == 0:
            return jsonify({
                'is_overrun_risk': False,
                'total_spent': 0,
                'monthly_budget': monthly_budget,
                'remaining_budget': monthly_budget,
                'projected_total': 0,
                'projected_overage': 0,
                'percent_over_budget': 0,
                'days_remaining': 30,
                'recommended_daily_limit': monthly_budget / 30,
                'severity': 'low',
                'message': 'No expenses recorded yet'
            }), 200
        
        # Check budget status
        status = check_budget_status(result['expenses'], monthly_budget)
        
        return jsonify(status), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Budget check failed: {str(e)}'
        }), 500


@bp.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """
    Get comprehensive spending insights and recommendations
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Spending insights, patterns, and tips
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Better validation for insights
        if len(result['expenses']) < 10:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for insights',
                'message': 'At least 10 expenses required for meaningful analysis',
                'current_count': len(result['expenses']),
                'required_count': 10
            }), 400
        
        # Get insights
        insights = get_spending_insights(result['expenses'])
        
        return jsonify(insights), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Insights generation failed: {str(e)}'
        }), 500


@bp.route('/budget-recommendations', methods=['GET'])
@jwt_required()
def get_budget_recommendations_route():
    """
    Get budget allocation recommendations (50/30/20 rule)
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - income (float, optional): Monthly income
    
    Returns:
        - 200: Budget recommendations
    """
    try:
        user_id = get_jwt_identity()
        income = request.args.get('income', type=float)
        
        # Validate income if provided
        if income is not None and income <= 0:
            return jsonify({
                'success': False,
                'error': 'Income must be greater than 0'
            }), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Handle empty expenses
        if len(result['expenses']) == 0:
            if income:
                return jsonify({
                    'current_allocation': {
                        'needs': 0,
                        'wants': 0,
                        'actual_needs': 0,
                        'actual_wants': 0
                    },
                    'recommended_allocation': {
                        'needs': 50,
                        'wants': 30,
                        'savings': 20
                    },
                    'recommended_amounts': {
                        'needs_budget': income * 0.50,
                        'wants_budget': income * 0.30,
                        'savings_goal': income * 0.20
                    },
                    'adjustments_needed': [],
                    'message': 'No expenses to analyze. Start tracking to get personalized recommendations.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'No expenses found',
                    'message': 'Please add expenses to get budget recommendations'
                }), 400
        
        # Get recommendations
        recommendations = get_budget_recommendations(result['expenses'], income)
        
        return jsonify(recommendations), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Budget recommendations failed: {str(e)}'
        }), 500


@bp.route('/financial-health', methods=['GET'])
@jwt_required()
def get_financial_health():
    """
    Calculate financial health score (0-100)
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - income (float, optional): Monthly income
        - savings (float, optional): Current savings
    
    Returns:
        - 200: Financial health score and breakdown
    """
    try:
        user_id = get_jwt_identity()
        income = request.args.get('income', type=float)
        savings = request.args.get('savings', type=float)
        
        # Validate parameters
        if income is not None and income < 0:
            return jsonify({
                'success': False,
                'error': 'Income cannot be negative'
            }), 400
        
        if savings is not None and savings < 0:
            return jsonify({
                'success': False,
                'error': 'Savings cannot be negative'
            }), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Handle empty expenses
        if len(result['expenses']) == 0:
            return jsonify({
                'success': False,
                'error': 'Insufficient data',
                'message': 'Please add at least 10 expenses to calculate financial health score',
                'current_count': 0,
                'required_count': 10
            }), 400
        
        # Calculate health score
        health_score = get_financial_health_score(result['expenses'], income, savings)
        
        return jsonify(health_score), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Health score calculation failed: {str(e)}'
        }), 500


@bp.route('/compare-benchmarks', methods=['GET'])
@jwt_required()
def compare_with_benchmarks():
    """
    Compare user's spending with national averages
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - income (float, optional): Monthly income
    
    Returns:
        - 200: Comparison with benchmarks
    """
    try:
        user_id = get_jwt_identity()
        income = request.args.get('income', type=float)
        
        # Validate income if provided
        if income is not None and income < 0:
            return jsonify({
                'success': False,
                'error': 'Income cannot be negative'
            }), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to get expenses'
            }), 400
        
        # ✅ FIXED: Handle empty expenses
        if len(result['expenses']) == 0:
            return jsonify({
                'success': False,
                'error': 'No expenses found',
                'message': 'Please add expenses to compare with benchmarks'
            }), 400
        
        # Compare with benchmarks
        comparison = compare_spending_with_benchmarks(result['expenses'], income)
        
        return jsonify(comparison), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Benchmark comparison failed: {str(e)}'
        }), 500