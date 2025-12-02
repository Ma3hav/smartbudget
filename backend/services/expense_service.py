"""
Expense Service - Handles expense CRUD operations
"""

from backend.models.expense_model import Expense
from backend.utils.db_connection import get_expenses_collection
from backend.utils.validation import validate_amount, is_valid_object_id
from bson import ObjectId
from datetime import datetime, timedelta


class ExpenseService:
    """Service class for expense operations"""
    
    def __init__(self):
        self.expenses = get_expenses_collection()
    
    def create_expense(self, user_id, expense_data):
        """
        Create a new expense
        
        Args:
            user_id: User's MongoDB ObjectId or string
            expense_data (dict): Expense details
        
        Returns:
            dict: Success status and created expense or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Validate amount
            is_valid, amount, message = validate_amount(expense_data.get('amount'))
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            # Create expense object
            expense = Expense(
                user_id=user_id,
                amount=amount,
                category=expense_data.get('category'),
                payment_type=expense_data.get('payment_type'),
                date=expense_data.get('date'),
                notes=expense_data.get('notes', ''),
                tags=expense_data.get('tags', []),
                receipt_url=expense_data.get('receipt_url')
            )
            
            # Insert into database
            result = self.expenses.insert_one(expense.to_mongo())
            
            # Get created expense
            created_expense = self.expenses.find_one({'_id': result.inserted_id})
            expense_obj = Expense.from_mongo(created_expense)
            
            return {
                'success': True,
                'message': 'Expense created successfully',
                'expense': expense_obj.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to create expense: {str(e)}'
            }
    
    def get_user_expenses(self, user_id, filters=None, page=1, limit=50):
        """
        Get user's expenses with optional filters
        
        Args:
            user_id: User's MongoDB ObjectId or string
            filters (dict, optional): Filter parameters
            page (int): Page number
            limit (int): Items per page
        
        Returns:
            dict: Expenses list and metadata
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Build query
            query = {'user_id': user_id}
            
            if filters:
                # Date range filter
                if 'start_date' in filters:
                    start_date = datetime.fromisoformat(filters['start_date'])
                    query['date'] = {'$gte': start_date}
                
                if 'end_date' in filters:
                    end_date = datetime.fromisoformat(filters['end_date'])
                    if 'date' in query:
                        query['date']['$lte'] = end_date
                    else:
                        query['date'] = {'$lte': end_date}
                
                # Category filter
                if 'category' in filters:
                    query['category'] = filters['category']
                
                # Payment type filter
                if 'payment_type' in filters:
                    query['payment_type'] = filters['payment_type']
                
                # Amount range filter
                if 'min_amount' in filters:
                    query['amount'] = {'$gte': float(filters['min_amount'])}
                
                if 'max_amount' in filters:
                    if 'amount' in query:
                        query['amount']['$lte'] = float(filters['max_amount'])
                    else:
                        query['amount'] = {'$lte': float(filters['max_amount'])}
                
                # Tags filter
                if 'tags' in filters:
                    query['tags'] = {'$in': filters['tags']}
            
            # Calculate pagination
            skip = (page - 1) * limit
            
            # Get expenses
            cursor = self.expenses.find(query).sort('date', -1).skip(skip).limit(limit)
            expenses_list = [Expense.from_mongo(doc).to_dict() for doc in cursor]
            
            # Get total count
            total_count = self.expenses.count_documents(query)
            
            return {
                'success': True,
                'expenses': expenses_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get expenses: {str(e)}',
                'expenses': []
            }
    
    def get_expense_by_id(self, expense_id, user_id):
        """
        Get single expense by ID
        
        Args:
            expense_id: Expense's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Expense data or error message
        """
        try:
            if isinstance(expense_id, str):
                expense_id = ObjectId(expense_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            expense_doc = self.expenses.find_one({
                '_id': expense_id,
                'user_id': user_id
            })
            
            if not expense_doc:
                return {
                    'success': False,
                    'message': 'Expense not found'
                }
            
            expense = Expense.from_mongo(expense_doc)
            
            return {
                'success': True,
                'expense': expense.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get expense: {str(e)}'
            }
    
    def update_expense(self, expense_id, user_id, update_data):
        """
        Update an expense
        
        Args:
            expense_id: Expense's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
            update_data (dict): Fields to update
        
        Returns:
            dict: Success status and updated expense or error message
        """
        try:
            if isinstance(expense_id, str):
                expense_id = ObjectId(expense_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            expense_doc = self.expenses.find_one({
                '_id': expense_id,
                'user_id': user_id
            })
            
            if not expense_doc:
                return {
                    'success': False,
                    'message': 'Expense not found'
                }
            
            expense = Expense.from_mongo(expense_doc)
            
            # Validate amount if provided
            if 'amount' in update_data:
                is_valid, amount, message = validate_amount(update_data['amount'])
                if not is_valid:
                    return {
                        'success': False,
                        'message': message
                    }
                update_data['amount'] = amount
            
            # Update expense
            expense.update(**update_data)
            
            # Save to database
            self.expenses.update_one(
                {'_id': expense_id},
                {'$set': expense.to_mongo()}
            )
            
            return {
                'success': True,
                'message': 'Expense updated successfully',
                'expense': expense.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update expense: {str(e)}'
            }
    
    def delete_expense(self, expense_id, user_id):
        """
        Delete an expense
        
        Args:
            expense_id: Expense's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(expense_id, str):
                expense_id = ObjectId(expense_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.expenses.delete_one({
                '_id': expense_id,
                'user_id': user_id
            })
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': 'Expense deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Expense not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete expense: {str(e)}'
            }
    
    def get_expense_statistics(self, user_id, start_date=None, end_date=None):
        """
        Get expense statistics for a user
        
        Args:
            user_id: User's MongoDB ObjectId or string
            start_date (datetime, optional): Start date for statistics
            end_date (datetime, optional): End date for statistics
        
        Returns:
            dict: Statistics data
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Default to current month
            if not start_date:
                start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Build query
            query = {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date}
            }
            
            # Aggregation pipeline
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': '$category',
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1},
                    'average': {'$avg': '$amount'}
                }},
                {'$sort': {'total': -1}}
            ]
            
            category_stats = list(self.expenses.aggregate(pipeline))
            
            # Calculate total
            total_spent = sum(stat['total'] for stat in category_stats)
            total_transactions = sum(stat['count'] for stat in category_stats)
            
            # Payment type breakdown
            payment_pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': '$payment_type',
                    'total': {'$sum': '$amount'},
                    'count': {'$sum': 1}
                }}
            ]
            
            payment_stats = list(self.expenses.aggregate(payment_pipeline))
            
            return {
                'success': True,
                'statistics': {
                    'total_spent': round(total_spent, 2),
                    'total_transactions': total_transactions,
                    'average_transaction': round(total_spent / total_transactions, 2) if total_transactions > 0 else 0,
                    'by_category': [
                        {
                            'category': stat['_id'],
                            'total': round(stat['total'], 2),
                            'count': stat['count'],
                            'average': round(stat['average'], 2),
                            'percentage': round((stat['total'] / total_spent) * 100, 2) if total_spent > 0 else 0
                        }
                        for stat in category_stats
                    ],
                    'by_payment_type': [
                        {
                            'payment_type': stat['_id'],
                            'total': round(stat['total'], 2),
                            'count': stat['count']
                        }
                        for stat in payment_stats
                    ],
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    }
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get statistics: {str(e)}'
            }
    
    def get_recent_expenses(self, user_id, limit=10):
        """
        Get user's most recent expenses
        
        Args:
            user_id: User's MongoDB ObjectId or string
            limit (int): Number of expenses to return
        
        Returns:
            dict: Recent expenses list
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            cursor = self.expenses.find({'user_id': user_id}).sort('date', -1).limit(limit)
            expenses_list = [Expense.from_mongo(doc).to_dict() for doc in cursor]
            
            return {
                'success': True,
                'expenses': expenses_list
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get recent expenses: {str(e)}',
                'expenses': []
            }
