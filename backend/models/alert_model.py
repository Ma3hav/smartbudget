"""
Alert Model - Budget alerts and notifications
"""

from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate


class Alert:
    """
    Alert model for budget warnings and notifications
    """
    
    ALERT_TYPES = ['budget_warning', 'overspending', 'goal_achieved', 'anomaly', 'reminder']
    PRIORITY_LEVELS = ['low', 'medium', 'high', 'critical']
    
    def __init__(self, user_id, alert_type, title, message, 
                priority='medium', is_read=False, metadata=None,
                created_at=None, read_at=None, _id=None):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.alert_type = alert_type
        self.title = title.strip()
        self.message = message.strip()
        self.priority = priority
        self.is_read = is_read
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.read_at = read_at
    
    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_read': self.is_read,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def to_mongo(self):
        """Convert alert to MongoDB document"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'is_read': self.is_read,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'read_at': self.read_at
        }
    
    @staticmethod
    def from_mongo(doc):
        """Create Alert instance from MongoDB document"""
        if not doc:
            return None
        
        return Alert(
            _id=doc.get('_id'),
            user_id=doc.get('user_id'),
            alert_type=doc.get('alert_type'),
            title=doc.get('title'),
            message=doc.get('message'),
            priority=doc.get('priority', 'medium'),
            is_read=doc.get('is_read', False),
            metadata=doc.get('metadata', {}),
            created_at=doc.get('created_at'),
            read_at=doc.get('read_at')
        )
    
    def mark_as_read(self):
        """Mark alert as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    @staticmethod
    def create_budget_warning(user_id, category, current_spending, budget_limit):
        """Factory method for budget warning alerts"""
        percent_used = (current_spending / budget_limit) * 100
        
        return Alert(
            user_id=user_id,
            alert_type='budget_warning',
            title=f'{category} Budget Alert',
            message=f'You have used {percent_used:.0f}% of your {category} budget (${current_spending:.2f} of ${budget_limit:.2f})',
            priority='high' if percent_used >= 90 else 'medium',
            metadata={
                'category': category,
                'current_spending': current_spending,
                'budget_limit': budget_limit,
                'percent_used': percent_used
            }
        )
    
    @staticmethod
    def create_anomaly_alert(user_id, anomaly_data):
        """Factory method for anomaly alerts"""
        return Alert(
            user_id=user_id,
            alert_type='anomaly',
            title='Unusual Spending Detected',
            message=anomaly_data.get('message', 'Unusual spending pattern detected'),
            priority=anomaly_data.get('severity', 'medium'),
            metadata=anomaly_data
        )
    
    @staticmethod
    def create_goal_achieved(user_id, goal_name, target_amount):
        """Factory method for goal achievement alerts"""
        return Alert(
            user_id=user_id,
            alert_type='goal_achieved',
            title='Goal Achieved! 🎉',
            message=f'Congratulations! You have reached your "{goal_name}" goal of ${target_amount:.2f}',
            priority='low',
            metadata={
                'goal_name': goal_name,
                'target_amount': target_amount
            }
        )


class AlertSchema(Schema):
    """
    Marshmallow schema for Alert validation
    """
    _id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    alert_type = fields.Str(required=True, validate=validate.OneOf(Alert.ALERT_TYPES))
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    message = fields.Str(required=True, validate=validate.Length(min=5, max=1000))
    priority = fields.Str(validate=validate.OneOf(Alert.PRIORITY_LEVELS))
    is_read = fields.Bool(dump_only=True)
    metadata = fields.Dict(keys=fields.Str(), values=fields.Raw())
    created_at = fields.DateTime(dump_only=True)
    read_at = fields.DateTime(dump_only=True)


class AlertFilterSchema(Schema):
    """Schema for filtering alerts"""
    alert_type = fields.Str(validate=validate.OneOf(Alert.ALERT_TYPES))
    priority = fields.Str(validate=validate.OneOf(Alert.PRIORITY_LEVELS))
    is_read = fields.Bool()
    start_date = fields.DateTime()
    end_date = fields.DateTime()