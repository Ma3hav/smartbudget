"""
Authentication Routes - User registration and login endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.auth_service import AuthService
from backend.models.user_model import UserSchema, UserLoginSchema, UserUpdateSchema
from marshmallow import ValidationError

bp = Blueprint('auth', __name__)
auth_service = AuthService()
user_schema = UserSchema()
login_schema = UserLoginSchema()
update_schema = UserUpdateSchema()


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request Body:
        - email (str): User's email
        - name (str): User's full name
        - password (str): User's password
    
    Returns:
        - 201: User registered successfully
        - 400: Validation error or registration failed
    """
    try:
        data = request.get_json()
        
        # Validate input
        validated_data = user_schema.load(data)
        
        # Register user
        result = auth_service.register_user(
            email=data.get('email'),
            name=data.get('name'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['user'],
                'access_token': result['tokens']['access_token'],
                'refresh_token': result['tokens']['refresh_token']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and get tokens
    
    Request Body:
        - email (str): User's email
        - password (str): User's password
    
    Returns:
        - 200: Login successful
        - 401: Invalid credentials
    """
    try:
        data = request.get_json()
        
        # Validate input
        validated_data = login_schema.load(data)
        
        # Login user
        result = auth_service.login_user(
            email=data.get('email'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['user'],
                'access_token': result['tokens']['access_token'],
                'refresh_token': result['tokens']['refresh_token']
            }), 200
        else:
            return jsonify({'error': result['message']}), 401
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's profile
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: User profile
        - 404: User not found
    """
    try:
        user_id = get_jwt_identity()
        
        user = auth_service.get_user_by_id(user_id)
        
        if user:
            return jsonify({'user': user}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500


@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update current user's profile
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - name (str, optional): User's name
        - profile (dict, optional): Profile settings
        - settings (dict, optional): App settings
    
    Returns:
        - 200: Profile updated successfully
        - 400: Validation error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        validated_data = update_schema.load(data)
        
        # Update profile
        result = auth_service.update_user_profile(user_id, **validated_data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'user': result['user']
            }), 200
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Profile update failed: {str(e)}'}), 500


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user's password
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - old_password (str): Current password
        - new_password (str): New password
    
    Returns:
        - 200: Password changed successfully
        - 400: Invalid password
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Both old and new passwords are required'}), 400
        
        # Change password
        result = auth_service.change_password(user_id, old_password, new_password)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 400
    
    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500


@bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """
    Delete user account
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Account deleted successfully
        - 400: Deletion failed
    """
    try:
        user_id = get_jwt_identity()
        
        # Delete account
        result = auth_service.delete_user(user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 400
    
    except Exception as e:
        return jsonify({'error': f'Account deletion failed: {str(e)}'}), 500
