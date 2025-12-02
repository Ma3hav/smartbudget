"""
Alert Routes - Budget alert and notification endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.alert_service import AlertService
from backend.models.alert_model import AlertSchema, AlertFilterSchema
from marshmallow import ValidationError

bp = Blueprint('alerts', __name__)
alert_service = AlertService()
alert_schema = AlertSchema()
filter_schema = AlertFilterSchema()


@bp.route('/', methods=['POST'])
@jwt_required()
def create_alert():
    """
    Create a new alert (admin/system use)
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - alert_type (str): Type of alert
        - title (str): Alert title
        - message (str): Alert message
        - priority (str, optional): Alert priority
        - metadata (dict, optional): Additional data
    
    Returns:
        - 201: Alert created successfully
        - 400: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user_id to data
        data['user_id'] = user_id
        
        # Validate input
        validated_data = alert_schema.load(data)
        
        # Create alert
        result = alert_service.create_alert(user_id, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'alert': result['alert']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create alert: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Get user's alerts with optional filters
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Query Parameters:
        - page (int, optional): Page number (default: 1)
        - limit (int, optional): Items per page (default: 20)
        - alert_type (str, optional): Filter by alert type
        - priority (str, optional): Filter by priority
        - is_read (bool, optional): Filter by read status
        - start_date (str, optional): Start date filter
        - end_date (str, optional): End date filter
    
    Returns:
        - 200: Alerts list with pagination
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # Build filters
        filters = {}
        if request.args.get('alert_type'):
            filters['alert_type'] = request.args.get('alert_type')
        if request.args.get('priority'):
            filters['priority'] = request.args.get('priority')
        if request.args.get('is_read'):
            filters['is_read'] = request.args.get('is_read').lower() == 'true'
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        # Get alerts
        result = alert_service.get_user_alerts(user_id, filters, page, limit)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get alerts: {str(e)}'}), 500


@bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """
    Get count of unread alerts
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Unread count
    """
    try:
        user_id = get_jwt_identity()
        
        result = alert_service.get_unread_count(user_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get unread count: {str(e)}'}), 500


@bp.route('/<alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """
    Get a specific alert by ID
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - alert_id (str): Alert ID
    
    Returns:
        - 200: Alert details
        - 404: Alert not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = alert_service.get_alert_by_id(alert_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to get alert: {str(e)}'}), 500


@bp.route('/<alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(alert_id):
    """
    Mark an alert as read
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - alert_id (str): Alert ID
    
    Returns:
        - 200: Alert marked as read
        - 404: Alert not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = alert_service.mark_alert_as_read(alert_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to mark alert as read: {str(e)}'}), 500


@bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """
    Mark all user's alerts as read
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: All alerts marked as read
    """
    try:
        user_id = get_jwt_identity()
        
        result = alert_service.mark_all_as_read(user_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to mark all as read: {str(e)}'}), 500


@bp.route('/<alert_id>', methods=['DELETE'])
@jwt_required()
def delete_alert(alert_id):
    """
    Delete an alert
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - alert_id (str): Alert ID
    
    Returns:
        - 200: Alert deleted successfully
        - 404: Alert not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = alert_service.delete_alert(alert_id, user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete alert: {str(e)}'}), 500


@bp.route('/check-budget', methods=['POST'])
@jwt_required()
def check_budget_alerts():
    """
    Check and create budget alerts based on category budgets
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - category_budgets (dict): Category name to budget limit mapping
        Example: {"Food": 500, "Transport": 300}
    
    Returns:
        - 200: Budget check completed
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        category_budgets = data.get('category_budgets', {})
        
        if not category_budgets:
            return jsonify({'error': 'Category budgets required'}), 400
        
        result = alert_service.check_budget_alerts(user_id, category_budgets)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to check budget alerts: {str(e)}'}), 500
