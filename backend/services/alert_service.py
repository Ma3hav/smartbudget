"""
Alert Service - Handles budget alerts and notifications
"""

from backend.models.alert_model import Alert
from backend.utils.db_connection import get_alerts_collection, get_expenses_collection
from bson import ObjectId
from datetime import datetime, timedelta


class AlertService:
    """Service class for alert operations"""
    
    def __init__(self):
        self.alerts = get_alerts_collection()
        self.expenses = get_expenses_collection()
    
    def create_alert(self, user_id, alert_data):
        """
        Create a new alert
        
        Args:
            user_id: User's MongoDB ObjectId or string
            alert_data (dict): Alert details
        
        Returns:
            dict: Success status and created alert or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Create alert
            alert = Alert(
                user_id=user_id,
                alert_type=alert_data.get('alert_type'),
                title=alert_data.get('title'),
                message=alert_data.get('message'),
                priority=alert_data.get('priority', 'medium'),
                metadata=alert_data.get('metadata', {})
            )
            
            # Insert into database
            result = self.alerts.insert_one(alert.to_mongo())
            
            # Get created alert
            created_alert = self.alerts.find_one({'_id': result.inserted_id})
            alert_obj = Alert.from_mongo(created_alert)
            
            return {
                'success': True,
                'message': 'Alert created successfully',
                'alert': alert_obj.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to create alert: {str(e)}'
            }
    
    def get_user_alerts(self, user_id, filters=None, page=1, limit=20):
        """
        Get user's alerts with optional filters
        
        Args:
            user_id: User's MongoDB ObjectId or string
            filters (dict, optional): Filter parameters
            page (int): Page number
            limit (int): Items per page
        
        Returns:
            dict: Alerts list and metadata
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Build query
            query = {'user_id': user_id}
            
            if filters:
                # Alert type filter
                if 'alert_type' in filters:
                    query['alert_type'] = filters['alert_type']
                
                # Priority filter
                if 'priority' in filters:
                    query['priority'] = filters['priority']
                
                # Read status filter
                if 'is_read' in filters:
                    query['is_read'] = filters['is_read']
                
                # Date range filter
                if 'start_date' in filters:
                    start_date = datetime.fromisoformat(filters['start_date'])
                    query['created_at'] = {'$gte': start_date}
                
                if 'end_date' in filters:
                    end_date = datetime.fromisoformat(filters['end_date'])
                    if 'created_at' in query:
                        query['created_at']['$lte'] = end_date
                    else:
                        query['created_at'] = {'$lte': end_date}
            
            # Calculate pagination
            skip = (page - 1) * limit
            
            # Get alerts
            cursor = self.alerts.find(query).sort('created_at', -1).skip(skip).limit(limit)
            alerts_list = [Alert.from_mongo(doc).to_dict() for doc in cursor]
            
            # Get total count
            total_count = self.alerts.count_documents(query)
            
            # Count unread alerts
            unread_count = self.alerts.count_documents({
                'user_id': user_id,
                'is_read': False
            })
            
            return {
                'success': True,
                'alerts': alerts_list,
                'unread_count': unread_count,
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
                'message': f'Failed to get alerts: {str(e)}',
                'alerts': []
            }
    
    def get_alert_by_id(self, alert_id, user_id):
        """
        Get single alert by ID
        
        Args:
            alert_id: Alert's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Alert data or error message
        """
        try:
            if isinstance(alert_id, str):
                alert_id = ObjectId(alert_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            alert_doc = self.alerts.find_one({
                '_id': alert_id,
                'user_id': user_id
            })
            
            if not alert_doc:
                return {
                    'success': False,
                    'message': 'Alert not found'
                }
            
            alert = Alert.from_mongo(alert_doc)
            
            return {
                'success': True,
                'alert': alert.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get alert: {str(e)}'
            }
    
    def mark_alert_as_read(self, alert_id, user_id):
        """
        Mark an alert as read
        
        Args:
            alert_id: Alert's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(alert_id, str):
                alert_id = ObjectId(alert_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            alert_doc = self.alerts.find_one({
                '_id': alert_id,
                'user_id': user_id
            })
            
            if not alert_doc:
                return {
                    'success': False,
                    'message': 'Alert not found'
                }
            
            alert = Alert.from_mongo(alert_doc)
            alert.mark_as_read()
            
            # Update in database
            self.alerts.update_one(
                {'_id': alert_id},
                {'$set': {
                    'is_read': alert.is_read,
                    'read_at': alert.read_at
                }}
            )
            
            return {
                'success': True,
                'message': 'Alert marked as read',
                'alert': alert.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to mark alert as read: {str(e)}'
            }
    
    def mark_all_as_read(self, user_id):
        """
        Mark all user's alerts as read
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.alerts.update_many(
                {'user_id': user_id, 'is_read': False},
                {'$set': {
                    'is_read': True,
                    'read_at': datetime.utcnow()
                }}
            )
            
            return {
                'success': True,
                'message': f'{result.modified_count} alerts marked as read',
                'count': result.modified_count
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to mark alerts as read: {str(e)}'
            }
    
    def delete_alert(self, alert_id, user_id):
        """
        Delete an alert
        
        Args:
            alert_id: Alert's MongoDB ObjectId or string
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(alert_id, str):
                alert_id = ObjectId(alert_id)
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            result = self.alerts.delete_one({
                '_id': alert_id,
                'user_id': user_id
            })
            
            if result.deleted_count > 0:
                return {
                    'success': True,
                    'message': 'Alert deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Alert not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to delete alert: {str(e)}'
            }
    
    def check_budget_alerts(self, user_id, category_budgets):
        """
        Check and create budget warning alerts
        
        Args:
            user_id: User's MongoDB ObjectId or string
            category_budgets (dict): Category budget limits
        
        Returns:
            dict: Created alerts
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Get current month expenses
            start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            created_alerts = []
            
            for category, budget_limit in category_budgets.items():
                # Calculate current spending
                pipeline = [
                    {
                        '$match': {
                            'user_id': user_id,
                            'category': category,
                            'date': {'$gte': start_of_month}
                        }
                    },
                    {
                        '$group': {
                            '_id': None,
                            'total': {'$sum': '$amount'}
                        }
                    }
                ]
                
                result = list(self.expenses.aggregate(pipeline))
                current_spending = result[0]['total'] if result else 0
                
                # Check if alert is needed (80% or more of budget used)
                percent_used = (current_spending / budget_limit) * 100 if budget_limit > 0 else 0
                
                if percent_used >= 80:
                    # Check if similar alert already exists today
                    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_alert = self.alerts.find_one({
                        'user_id': user_id,
                        'alert_type': 'budget_warning',
                        'metadata.category': category,
                        'created_at': {'$gte': today_start}
                    })
                    
                    if not existing_alert:
                        # Create budget warning alert
                        alert = Alert.create_budget_warning(
                            user_id=user_id,
                            category=category,
                            current_spending=current_spending,
                            budget_limit=budget_limit
                        )
                        
                        result = self.alerts.insert_one(alert.to_mongo())
                        created_alert = self.alerts.find_one({'_id': result.inserted_id})
                        created_alerts.append(Alert.from_mongo(created_alert).to_dict())
            
            return {
                'success': True,
                'alerts_created': len(created_alerts),
                'alerts': created_alerts
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to check budget alerts: {str(e)}'
            }
    
    def get_unread_count(self, user_id):
        """
        Get count of unread alerts
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Unread count
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            count = self.alerts.count_documents({
                'user_id': user_id,
                'is_read': False
            })
            
            return {
                'success': True,
                'unread_count': count
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get unread count: {str(e)}',
                'unread_count': 0
            }
