"""
Category Routes - Custom category management endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.category_service import CategoryService
from models.category_model import CategorySchema, CategoryUpdateSchema
from marshmallow import ValidationError

bp = Blueprint('categories', __name__)
category_service = CategoryService()
category_schema = CategorySchema()
update_schema = CategoryUpdateSchema()


@bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    """
    Create a new custom category
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Request Body:
        - name (str): Category name
        - icon (str, optional): Icon name
        - color (str, optional): Hex color code
        - budget_limit (float, optional): Monthly budget limit
    
    Returns:
        - 201: Category created successfully
        - 400: Validation error or duplicate name
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Add user_id to data
        data['user_id'] = user_id
        
        # Validate input
        validated_data = category_schema.load(data)
        
        # Create category
        result = category_service.create_category(user_id, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'category': result['category']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create category: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    """
    Get all user's categories
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Returns:
        - 200: Categories list
    """
    try:
        user_id = get_jwt_identity()
        
        result = category_service.get_user_categories(user_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to get categories: {str(e)}'}), 500


@bp.route('/<category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """
    Get a specific category by ID
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - category_id (str): Category ID
    
    Returns:
        - 200: Category details
        - 404: Category not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = category_service.get_category_by_id(category_id, user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({'error': result['message']}), 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to get category: {str(e)}'}), 500


@bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """
    Update a category
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - category_id (str): Category ID
    
    Request Body:
        - name (str, optional): Updated name
        - icon (str, optional): Updated icon
        - color (str, optional): Updated color
        - budget_limit (float, optional): Updated budget limit
    
    Returns:
        - 200: Category updated successfully
        - 400: Validation error or cannot modify default
        - 404: Category not found
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        validated_data = update_schema.load(data)
        
        # Update category
        result = category_service.update_category(category_id, user_id, validated_data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'category': result['category']
            }), 200
        else:
            return jsonify({'error': result['message']}), 400 if 'cannot' in result['message'].lower() else 404
    
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update category: {str(e)}'}), 500


@bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """
    Delete a category
    
    Headers:
        - Authorization: Bearer <access_token>
    
    Parameters:
        - category_id (str): Category ID
    
    Returns:
        - 200: Category deleted successfully
        - 400: Cannot delete default category
        - 404: Category not found
    """
    try:
        user_id = get_jwt_identity()
        
        result = category_service.delete_category(category_id, user_id)
        
        if result['success']:
            return jsonify({'message': result['message']}), 200
        else:
            return jsonify({'error': result['message']}), 400 if 'cannot' in result['message'].lower() else 404
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete category: {str(e)}'}), 500