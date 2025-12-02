"""
Savings Service - Handles savings goals
"""

from backend.models.savings_model import SavingsGoal
from backend.utils.db_connection import get_savings_goals_collection
from backend.utils.validation import validate_amount
from bson import ObjectId
from datetime import datetime


class SavingsService:
    """Service class for savings goal operations"""
    
    def __init__(self):
        self.savings_goals = get_savings_goals_collection()
    
    def create_goal(self, user_id, goal_data):
        """
        Create a new savings goal
        
        Args:
            user_id: User's MongoDB ObjectId or string
            goal_data (dict): Goal details
        
        Returns:
            dict: Success status and created goal or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Validate target amount
            is_valid, amount, message = validate_amount(goal_data.get('target_amount'))
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            # Create goal
            goal = SavingsGoal(
                user_id=user_id,
                title=goal_data.get('title'),
                target_amount=amount,
                saved_amount=goal_data.get('saved_amount', 0),
                deadline=goal_data.get('deadline'),
                description=goal_data.get('description', ''),
                priority=goal_data.get('priority', 'medium')
            )
            
            # Insert into database
            result = self.savings_goals.insert_one(goal.to_mongo())
            
            # Get created goal
            created_goal = self.savings_goals.find_one({'_id': result.inserted_id})
            goal_obj = SavingsGoal.from_mongo(created_goal)
            
            return {
                'success': True,
                'message': 'Savings goal created successfully',
                'goal': goal_obj.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to create goal: {str(e)}'
            }
    
    def get_user_goals(self, user_id, status=None):
        """
        Get user's savings goals
        
        Args:
            user_id: User's MongoDB ObjectId or string
            status (str, optional): Filter by status
        
        Returns:
            dict: Goals list
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Build query
            query = {'user_id': user_id}
            
            if status:
                query['status'] = status
            
            # Get goals
            cursor = self.savings_goals.find(query).sort('created_at', -1)
            goals_list = [SavingsGoal.from_mongo(doc).to_dict() for doc in cursor]
            
            # Calculate summary
            total_target = sum(goal['target_amount'] for goal in goals_list)
            total_saved = sum(goal['saved_amount'] for goal in goals_list)
            active_goals = len([g for g in goals_list if g['status'] == 'active'])
            completed_goals = len([g for g in goals_list if g['status'] == 'completed'])
            
            return {
                'success': True,
                'goals': goals_list,
                'summary': {
                    'total_goals': len(goals_list),
                    'active_goals': active_goals,
                    'completed_goals': completed_goals,
                    'total_target': round(total_target, 2),
                    'total_saved': round(total_saved, 2),
                    'overall_progress': round((total_saved / total_target * 100) if total_target > 0 else 0, 2)
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get goals: {str(e)}',
                'goals': []
            }
    
    def get_goal_by_id(self, goal_id, user_id):
        """
        Get single goal by ID
        
        Args:
            goal_id: Goal's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Goal data or error message
        """
        try:
            if isinstance(goal_id, str):
                goal_id = ObjectId(goal_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            goal_doc = self.savings_goals.find_one({
                '_id': goal_id,
                'user_id': user_id
            })
            
            if not goal_doc:
                return {
                    'success': False,
                    'message': 'Goal not found'
                }
            
            goal = SavingsGoal.from_mongo(goal_doc)
            
            return {
                'success': True,
                'goal': goal.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get goal: {str(e)}'
            }
    
    def update_goal(self, goal_id, user_id, update_data):
        """
        Update a savings goal
        
        Args:
            goal_id: Goal's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
            update_data (dict): Fields to update
        
        Returns:
            dict: Success status and updated goal or error message
        """
        try:
            if isinstance(goal_id, str):
                goal_id = ObjectId(goal_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            goal_doc = self.savings_goals.find_one({
                '_id': goal_id,
                'user_id': user_id
            })
            
            if not goal_doc:
                return {
                    'success': False,
                    'message': 'Goal not found'
                }
            
            goal = SavingsGoal.from_mongo(goal_doc)
            
            # Validate amounts if provided
            if 'target_amount' in update_data:
                is_valid, amount, message = validate_amount(update_data['target_amount'])
                if not is_valid:
                    return {
                        'success': False,
                        'message': message
                    }
                update_data['target_amount'] = amount
            
            if 'saved_amount' in update_data:
                is_valid, amount, message = validate_amount(update_data['saved_amount'])
                if not is_valid:
                    return {
                        'success': False,
                        'message': message
                    }
                update_data['saved_amount'] = amount
            
            # Update goal
            goal.update(**update_data)
            
            # Save to database
            self.savings_goals.update_one(
                {'_id': goal_id},
                {'$set': goal.to_mongo()}
            )
            
            return {
                'success': True,
                'message': 'Goal updated successfully',
                'goal': goal.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to update goal: {str(e)}'
            }
    
    def add_savings(self, goal_id, user_id, amount, notes=''):
        """
        Add money to a savings goal
        
        Args:
            goal_id: Goal's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
            amount (float): Amount to add
            notes (str): Optional notes
        
        Returns:
            dict: Success status and updated goal or error message
        """
        try:
            if isinstance(goal_id, str):
                goal_id = ObjectId(goal_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Validate amount
            is_valid, amount, message = validate_amount(amount)
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            goal_doc = self.savings_goals.find_one({
                '_id': goal_id,
                'user_id': user_id
            })
            
            if not goal_doc:
                return {
                    'success': False,
                    'message': 'Goal not found'
                }
            
            goal = SavingsGoal.from_mongo(goal_doc)
            
            # Add savings
            new_total = goal.add_savings(amount)
            
            # Save to database
            self.savings_goals.update_one(
                {'_id': goal_id},
                {'$set': goal.to_mongo()}
            )
            
            return {
                'success': True,
                'message': f'Added ${amount:.2f} to savings',
                'goal': goal.to_dict(),
                'new_total': new_total
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to add savings: {str(e)}'
            }
    
    def withdraw_savings(self, goal_id, user_id, amount, notes=''):
        """
        Withdraw money from a savings goal
        
        Args:
            goal_id: Goal's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
            amount (float): Amount to withdraw
            notes (str): Optional notes
        
        Returns:
            dict: Success status and updated goal or error message
        """
        try:
            if isinstance(goal_id, str):
                goal_id = ObjectId(goal_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Validate amount
            is_valid, amount, message = validate_amount(amount)
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            goal_doc = self.savings_goals.find_one({
                '_id': goal_id,
                'user_id': user_id
            })
            
            if not goal_doc:
                return {
                    'success': False,
                    'message': 'Goal not found'
                }
            
            goal = SavingsGoal.from_mongo(goal_doc)
            
            # Check if sufficient funds
            if amount > goal.saved_amount:
                return {
                    'success': False,
                    'message': 'Insufficient savings to withdraw'
                }
            
            # Withdraw savings
            new_total = goal.withdraw_savings(amount)
            
            # Save to database
            self.savings_goals.update_one(
                {'_id': goal_id},
                {'$set': goal.to_mongo()}
            )
            
            return {
                'success': True,
                'message': f'Withdrew ${amount:.2f} from savings',
                'goal': goal.to_dict(),
                'new_total': new_total
            }
        
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to withdraw savings: {str(e)}'
            }
    
    def delete_goal(self, goal_id, user_id):
        """
        Delete a savings goal
        
        Args:
            goal_id: Goal's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(goal_id, str):
                goal_id = ObjectId(goal_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.savings_goals.delete_one({
                '_id': goal_id,
                'user_id': user_id
            })
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': 'Goal deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Goal not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete goal: {str(e)}'
            }
    
    def get_overdue_goals(self, user_id):
        """
        Get goals that are past deadline and not completed
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Overdue goals list
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Find overdue goals
            cursor = self.savings_goals.find({
                'user_id': user_id,
                'status': 'active',
                'deadline': {'$lt': datetime.utcnow()}
            })
            
            overdue_goals = [SavingsGoal.from_mongo(doc).to_dict() for doc in cursor]
            
            return {
                'success': True,
                'goals': overdue_goals,
                'count': len(overdue_goals)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get overdue goals: {str(e)}',
                'goals': []
            }
