"""
Expense Routes - Expense management endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.expense_service import ExpenseService
from backend.models.expense_model import ExpenseSchema, ExpenseUpdateSchema, ExpenseFilterSchema
from marshmallow import ValidationError
from datetime import datetime

bp = Blueprint('expenses', __name__)
expense_service = ExpenseService()
expense_schema = ExpenseSchema()
update_schema = ExpenseUpdateSchema()
filter_schema = ExpenseFilterSchema()


@bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    """
    Create a new expense
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - amount (float): Expense amount
        - category (str): Expense category
        - payment_type (str): Payment method
        - date (str, optional): Expense date (ISO format)
        - notes (str, optional): Additional notes
        - tags (list, optional): Tags for categorization
    
    Returns:
        - 201: Expense created successfully
        - 400: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user_id to data
        data['user_id'] = user_id
        
        # Validate input
        validated_data = expense_schema.load(data)
        
        # Create expense
        result = expense_service.create_expense(user_id, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'expense': result['expense']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create expense: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    """
    Get user's expenses with optional filters
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - page (int, optional): Page number (default: 1)
        - limit (int, optional): Items per page (default: 50)
        - category (str, optional): Filter by category
        - payment_type (str, optional): Filter by payment type
        - start_date (str, optional): Start date filter (ISO format)
        - end_date (str, optional): End date filter (ISO format)
        - min_amount (float, optional): Minimum amount filter
        - max_amount (float, optional): Maximum amount filter
    
    Returns:
        - 200: Expenses list with pagination
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Build filters
        filters = {}
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        if request.args.get('payment_type'):
            filters['payment_type'] = request.args.get('payment_type')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('min_amount'):
            filters['min_amount'] = request.args.get('min_amount', type=float)
        if request.args.get('max_amount'):
            filters['max_amount'] = request.args.get('max_amount', type=float)
        
        # Get expenses
        result = expense_service.get_user_expenses(user_id, filters, page, limit)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get expenses: {str(e)}'}), 500


@bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_expenses():
    """
    Get user's most recent expenses
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - limit (int, optional): Number of expenses (default: 10)
    
    Returns:
        - 200: Recent expenses list
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        
        result = expense_service.get_recent_expenses(user_id, limit)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get recent expenses: {str(e)}'}), 500


@bp.route('/<expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """
    Get a specific expense by ID
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - expense_id (str): Expense ID
    
    Returns:
        - 200: Expense details
        - 404: Expense not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = expense_service.get_expense_by_id(expense_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to get expense: {str(e)}'}), 500


@bp.route('/<expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """
    Update an expense
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - expense_id (str): Expense ID
    
    Request Body:
        - amount (float, optional): Updated amount
        - category (str, optional): Updated category
        - payment_type (str, optional): Updated payment type
        - date (str, optional): Updated date
        - notes (str, optional): Updated notes
        - tags (list, optional): Updated tags
    
    Returns:
        - 200: Expense updated successfully
        - 400: Validation error
        - 404: Expense not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        validated_data = update_schema.load(data)
        
        # Update expense
        result = expense_service.update_expense(expense_id, user_id, validated_data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'expense': result['expense']
            }), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update expense: {str(e)}'}), 500


@bp.route('/<expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """
    Delete an expense
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - expense_id (str): Expense ID
    
    Returns:
        - 200: Expense deleted successfully
        - 404: Expense not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = expense_service.delete_expense(expense_id, user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete expense: {str(e)}'}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    Get expense statistics
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - start_date (str, optional): Start date (ISO format)
        - end_date (str, optional): End date (ISO format)
    
    Returns:
        - 200: Statistics data
    """
    try:
        user_id = get_jwt_identity()
        
        # Get date range
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        
        result = expense_service.get_expense_statistics(user_id, start_date, end_date)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500
