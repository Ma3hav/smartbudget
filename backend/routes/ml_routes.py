"""
ML Routes - Machine learning powered insights and predictions
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
        
        if not result['success'] or len(result['expenses']) < 30:
            return jsonify({
                'error': 'Insufficient data for prediction',
                'message': 'At least 30 expenses required for forecasting'
            }), 400
        
        # Get forecast
        forecast = get_expense_forecast(result['expenses'])
        
        return jsonify(forecast), 200
    
    except Exception as e:
        return jsonify({'error': f'Forecast failed: {str(e)}'}), 500


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
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Get category forecast
        forecast = get_category_forecast(result['expenses'], category, days)
        
        if forecast['success']:
            return jsonify(forecast), 200
        else:
            return jsonify({'error': forecast['message']}), 400
    
    except Exception as e:
        return jsonify({'error': f'Category forecast failed: {str(e)}'}), 500


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
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Check anomalies
        anomalies = check_spending_anomalies(result['expenses'], monthly_budget)
        
        return jsonify(anomalies), 200
    
    except Exception as e:
        return jsonify({'error': f'Anomaly detection failed: {str(e)}'}), 500


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
            return jsonify({'error': 'Monthly budget parameter required'}), 400
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Check budget status
        status = check_budget_status(result['expenses'], monthly_budget)
        
        return jsonify(status), 200
    
    except Exception as e:
        return jsonify({'error': f'Budget check failed: {str(e)}'}), 500


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
        
        if not result['success'] or len(result['expenses']) < 10:
            return jsonify({
                'error': 'Insufficient data for insights',
                'message': 'At least 10 expenses required for analysis'
            }), 400
        
        # Get insights
        insights = get_spending_insights(result['expenses'])
        
        return jsonify(insights), 200
    
    except Exception as e:
        return jsonify({'error': f'Insights generation failed: {str(e)}'}), 500


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
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Get recommendations
        recommendations = get_budget_recommendations(result['expenses'], income)
        
        return jsonify(recommendations), 200
    
    except Exception as e:
        return jsonify({'error': f'Budget recommendations failed: {str(e)}'}), 500


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
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Calculate health score
        health_score = get_financial_health_score(result['expenses'], income, savings)
        
        return jsonify(health_score), 200
    
    except Exception as e:
        return jsonify({'error': f'Health score calculation failed: {str(e)}'}), 500


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
        
        # Get user's expenses
        result = expense_service.get_user_expenses(user_id, limit=1000)
        
        if not result['success']:
            return jsonify({'error': 'Failed to get expenses'}), 400
        
        # Compare with benchmarks
        comparison = compare_spending_with_benchmarks(result['expenses'], income)
        
        return jsonify(comparison), 200
    
    except Exception as e:
        return jsonify({'error': f'Benchmark comparison failed: {str(e)}'}), 500