"""
Savings Routes - Savings goal management endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.savings_service import SavingsService
from models.savings_model import SavingsGoalSchema, SavingsGoalUpdateSchema, SavingsTransactionSchema
from marshmallow import ValidationError

bp = Blueprint('savings', __name__)
savings_service = SavingsService()
goal_schema = SavingsGoalSchema()
update_schema = SavingsGoalUpdateSchema()
transaction_schema = SavingsTransactionSchema()


@bp.route('/', methods=['POST'])
@jwt_required()
def create_goal():
    """
    Create a new savings goal
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - title (str): Goal title
        - target_amount (float): Target amount
        - saved_amount (float, optional): Initial saved amount
        - deadline (str, optional): Deadline date (ISO format)
        - description (str, optional): Goal description
        - priority (str, optional): Priority level
    
    Returns:
        - 201: Goal created successfully
        - 400: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user_id to data
        data['user_id'] = user_id
        
        # Validate input
        validated_data = goal_schema.load(data)
        
        # Create goal
        result = savings_service.create_goal(user_id, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'goal': result['goal']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create goal: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_goals():
    """
    Get user's savings goals
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - status (str, optional): Filter by status (active, completed, paused, cancelled)
    
    Returns:
        - 200: Goals list with summary
    """
    try:
        user_id = get_jwt_identity()
        status = request.args.get('status')
        
        result = savings_service.get_user_goals(user_id, status)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get goals: {str(e)}'}), 500


@bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_goals():
    """
    Get overdue goals (past deadline and not completed)
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Overdue goals list
    """
    try:
        user_id = get_jwt_identity()
        
        result = savings_service.get_overdue_goals(user_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get overdue goals: {str(e)}'}), 500


@bp.route('/<goal_id>', methods=['GET'])
@jwt_required()
def get_goal(goal_id):
    """
    Get a specific goal by ID
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - goal_id (str): Goal ID
    
    Returns:
        - 200: Goal details
        - 404: Goal not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = savings_service.get_goal_by_id(goal_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to get goal: {str(e)}'}), 500


@bp.route('/<goal_id>', methods=['PUT'])
@jwt_required()
def update_goal(goal_id):
    """
    Update a savings goal
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - goal_id (str): Goal ID
    
    Request Body:
        - title (str, optional): Updated title
        - target_amount (float, optional): Updated target amount
        - saved_amount (float, optional): Updated saved amount
        - deadline (str, optional): Updated deadline
        - description (str, optional): Updated description
        - priority (str, optional): Updated priority
        - status (str, optional): Updated status
    
    Returns:
        - 200: Goal updated successfully
        - 400: Validation error
        - 404: Goal not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        validated_data = update_schema.load(data)
        
        # Update goal
        result = savings_service.update_goal(goal_id, user_id, validated_data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'goal': result['goal']
            }), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update goal: {str(e)}'}), 500


@bp.route('/<goal_id>/transaction', methods=['POST'])
@jwt_required()
def handle_transaction(goal_id):
    """
    Add or withdraw savings from a goal
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - goal_id (str): Goal ID
    
    Request Body:
        - action (str): Transaction type ("add" or "withdraw")
        - amount (float): Transaction amount
        - notes (str, optional): Transaction notes
    
    Returns:
        - 200: Transaction completed successfully
        - 400: Validation error or insufficient funds
        - 404: Goal not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        validated_data = transaction_schema.load(data)
        
        action = validated_data.get('action')
        amount = validated_data.get('amount')
        notes = validated_data.get('notes', '')
        
        # Handle transaction
        if action == 'add':
            result = savings_service.add_savings(goal_id, user_id, amount, notes)
        elif action == 'withdraw':
            result = savings_service.withdraw_savings(goal_id, user_id, amount, notes)
        else:
            return jsonify({'error': 'Invalid action. Use "add" or "withdraw"'}), 400
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 400 if 'not found' not in result['message'].lower() else 404
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Transaction failed: {str(e)}'}), 500


@bp.route('/<goal_id>', methods=['DELETE'])
@jwt_required()
def delete_goal(goal_id):
    """
    Delete a savings goal
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - goal_id (str): Goal ID
    
    Returns:
        - 200: Goal deleted successfully
        - 404: Goal not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = savings_service.delete_goal(goal_id, user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete goal: {str(e)}'}), 500