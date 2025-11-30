"""
JWT Utilities - Token generation and validation helpers
"""

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta
from functools import wraps
from flask import jsonify
from bson import ObjectId


def generate_tokens(user_id):
    """
    Generate access and refresh tokens for a user
    
    Args:
        user_id: User's MongoDB ObjectId or string
    
    Returns:
        dict: Contains access_token and refresh_token
    """
    user_id_str = str(user_id)
    
    access_token = create_access_token(
        identity=user_id_str,
        fresh=True
    )
    
    refresh_token = create_refresh_token(
        identity=user_id_str
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_current_user_id():
    """
    Get current authenticated user's ID from JWT token
    
    Returns:
        ObjectId: Current user's MongoDB ObjectId
    """
    user_id = get_jwt_identity()
    return ObjectId(user_id)


def token_required(f):
    """
    Decorator to require valid JWT token
    Use this on routes that need authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'message': str(e)}), 401
    
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from utils.db_connection import get_users_collection
        
        try:
            user_id = get_current_user_id()
            users = get_users_collection()
            user = users.find_one({'_id': user_id})
            
            if not user or not user.get('is_admin', False):
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authorization failed', 'message': str(e)}), 401
    
    return decorated_function


def refresh_access_token(refresh_token):
    """
    Generate new access token from refresh token
    
    Args:
        refresh_token: Valid refresh token
    
    Returns:
        str: New access token
    """
    user_id = get_jwt_identity()
    return create_access_token(identity=user_id, fresh=False)