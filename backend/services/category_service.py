"""
Category Service - Handles category CRUD operations
"""

from backend.models.category_model import Category
from backend.utils.db_connection import get_categories_collection
from backend.utils.validation import sanitize_string
from bson import ObjectId
from datetime import datetime


class CategoryService:
    """Service class for category operations"""
    
    def __init__(self):
        self.categories = get_categories_collection()
    
    def create_category(self, user_id, category_data):
        """
        Create a new category
        
        Args:
            user_id: User's MongoDB ObjectId or string
            category_data (dict): Category details
        
        Returns:
            dict: Success status and created category or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Sanitize name
            name = sanitize_string(category_data.get('name', ''), max_length=50)
            
            if not name:
                return {
                    'success': False,
                    'message': 'Category name is required'
                }
            
            # Check if category already exists for this user
            existing = self.categories.find_one({
                'user_id': user_id,
                'name': name
            })
            
            if existing:
                return {
                    'success': False,
                    'message': 'Category with this name already exists'
                }
            
            # Create category
            category = Category(
                user_id=user_id,
                name=name,
                icon=category_data.get('icon', 'tag'),
                color=category_data.get('color', '#D2042D'),
                budget_limit=category_data.get('budget_limit')
            )
            
            # Insert into database
            result = self.categories.insert_one(category.to_mongo())
            
            # Get created category
            created_category = self.categories.find_one({'_id': result.inserted_id})
            category_obj = Category.from_mongo(created_category)
            
            return {
                'success': True,
                'message': 'Category created successfully',
                'category': category_obj.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to create category: {str(e)}'
            }
    
    def get_user_categories(self, user_id):
        """
        Get all categories for a user (including default ones)
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Categories list
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Get user's custom categories
            cursor = self.categories.find({'user_id': user_id}).sort('created_at', -1)
            categories_list = [Category.from_mongo(doc).to_dict() for doc in cursor]
            
            # Add default categories if user has no custom ones
            if len(categories_list) == 0:
                default_categories = self._create_default_categories(user_id)
                categories_list = default_categories
            
            return {
                'success': True,
                'categories': categories_list,
                'total': len(categories_list)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get categories: {str(e)}',
                'categories': []
            }
    
    def _create_default_categories(self, user_id):
        """
        Create default categories for a new user
        
        Args:
            user_id: User's MongoDB ObjectId
        
        Returns:
            list: Default categories
        """
        default_categories_data = [
            {'name': 'Food', 'icon': 'utensils', 'color': '#D2042D'},
            {'name': 'Transport', 'icon': 'car', 'color': '#8B0000'},
            {'name': 'Shopping', 'icon': 'shopping-bag', 'color': '#A52A2A'},
            {'name': 'Bills', 'icon': 'file-text', 'color': '#C41E3A'},
            {'name': 'Entertainment', 'icon': 'film', 'color': '#DC143C'},
            {'name': 'Healthcare', 'icon': 'heart', 'color': '#B22222'},
            {'name': 'Other', 'icon': 'more-horizontal', 'color': '#8B0000'}
        ]
        
        categories_list = []
        
        for cat_data in default_categories_data:
            category = Category(
                user_id=user_id,
                name=cat_data['name'],
                icon=cat_data['icon'],
                color=cat_data['color'],
                is_default=True
            )
            
            result = self.categories.insert_one(category.to_mongo())
            created_category = self.categories.find_one({'_id': result.inserted_id})
            categories_list.append(Category.from_mongo(created_category).to_dict())
        
        return categories_list
    
    def get_category_by_id(self, category_id, user_id):
        """
        Get single category by ID
        
        Args:
            category_id: Category's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Category data or error message
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            category_doc = self.categories.find_one({
                '_id': category_id,
                'user_id': user_id
            })
            
            if not category_doc:
                return {
                    'success': False,
                    'message': 'Category not found'
                }
            
            category = Category.from_mongo(category_doc)
            
            return {
                'success': True,
                'category': category.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get category: {str(e)}'
            }
    
    def update_category(self, category_id, user_id, update_data):
        """
        Update a category
        
        Args:
            category_id: Category's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
            update_data (dict): Fields to update
        
        Returns:
            dict: Success status and updated category or error message
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            category_doc = self.categories.find_one({
                '_id': category_id,
                'user_id': user_id
            })
            
            if not category_doc:
                return {
                    'success': False,
                    'message': 'Category not found'
                }
            
            category = Category.from_mongo(category_doc)
            
            # Cannot modify default categories
            if category.is_default and 'name' in update_data:
                return {
                    'success': False,
                    'message': 'Cannot modify default category name'
                }
            
            # Sanitize name if provided
            if 'name' in update_data:
                update_data['name'] = sanitize_string(update_data['name'], max_length=50)
                
                # Check for duplicate name
                existing = self.categories.find_one({
                    'user_id': user_id,
                    'name': update_data['name'],
                    '_id': {'$ne': category_id}
                })
                
                if existing:
                    return {
                        'success': False,
                        'message': 'Category with this name already exists'
                    }
            
            # Update category
            category.update(**update_data)
            
            # Save to database
            self.categories.update_one(
                {'_id': category_id},
                {'$set': category.to_mongo()}
            )
            
            return {
                'success': True,
                'message': 'Category updated successfully',
                'category': category.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update category: {str(e)}'
            }
    
    def delete_category(self, category_id, user_id):
        """
        Delete a category
        
        Args:
            category_id: Category's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            category_doc = self.categories.find_one({
                '_id': category_id,
                'user_id': user_id
            })
            
            if not category_doc:
                return {
                    'success': False,
                    'message': 'Category not found'
                }
            
            category = Category.from_mongo(category_doc)
            
            # Cannot delete default categories
            if category.is_default:
                return {
                    'success': False,
                    'message': 'Cannot delete default category'
                }
            
            # Delete category
            result = self.categories.delete_one({
                '_id': category_id,
                'user_id': user_id
            })
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': 'Category deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Category not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete category: {str(e)}'
            }
    
    def get_category_spending(self, user_id, category_name, start_date=None, end_date=None):
        """
        Get total spending for a category
        
        Args:
            user_id: User's MongoDB ObjectId or string
            category_name: Category name
            start_date: Start date for filtering
            end_date: End date for filtering
        
        Returns:
            dict: Category spending data
        """
        try:
            from backend.utils.db_connection import get_expenses_collection
            
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            expenses = get_expenses_collection()
            
            # Build query
            query = {
                'user_id': user_id,
                'category': category_name
            }
            
            if start_date:
                query['date'] = {'$gte': start_date}
            
            if end_date:
                if 'date' in query:
                    query['date']['$lte'] = end_date
                else:
                    query['date'] = {'$lte': end_date}
            
            # Aggregate total spending
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': None,
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1},
                    'average': {'$avg': '$amount'}
                }}
            ]
            
            result = list(expenses.aggregate(pipeline))
            
            if result:
                return {
                    'success': True,
                    'category': category_name,
                    'total_spent': round(result[0]['total'], 2),
                    'transaction_count': result[0]['count'],
                    'average_amount': round(result[0]['average'], 2)
                }
            else:
                return {
                    'success': True,
                    'category': category_name,
                    'total_spent': 0,
                    'transaction_count': 0,
                    'average_amount': 0
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get category spending: {str(e)}'
            }
