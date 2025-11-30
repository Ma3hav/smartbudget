"""
Savings Goal Model - Track savings goals
"""

from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate, validates, ValidationError


class SavingsGoal:
    """
    Savings goal model for tracking financial goals
    """

    STATUS_OPTIONS = ['active', 'completed', 'paused', 'cancelled']

    def __init__(self, user_id, title, target_amount, saved_amount=0,
                 deadline=None, description='', priority='medium',
                 status='active', created_at=None, updated_at=None,
                 completed_at=None, _id=None):

        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.title = title.strip()
        self.target_amount = float(target_amount)
        self.saved_amount = float(saved_amount)
        self.deadline = deadline
        self.description = description.strip() if description else ''
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.completed_at = completed_at

    def to_dict(self):
        """Convert savings goal to dictionary"""
        progress = (self.saved_amount / self.target_amount * 100) if self.target_amount > 0 else 0

        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'title': self.title,
            'target_amount': self.target_amount,
            'saved_amount': self.saved_amount,
            'remaining_amount': self.target_amount - self.saved_amount,
            'progress_percent': round(progress, 2),
            'deadline': self.deadline.isoformat() if isinstance(self.deadline, datetime) else self.deadline,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'is_overdue': self.is_overdue(),
            'days_remaining': self.days_remaining(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def to_mongo(self):
        """Convert savings goal to MongoDB document"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'title': self.title,
            'target_amount': self.target_amount,
            'saved_amount': self.saved_amount,
            'deadline': self.deadline if isinstance(self.deadline, datetime)
                        else datetime.fromisoformat(self.deadline) if self.deadline else None,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }

    @staticmethod
    def from_mongo(doc):
        """Create SavingsGoal instance from MongoDB document"""
        if not doc:
            return None

        return SavingsGoal(
            _id=doc.get('_id'),
            user_id=doc.get('user_id'),
            title=doc.get('title'),
            target_amount=doc.get('target_amount'),
            saved_amount=doc.get('saved_amount', 0),
            deadline=doc.get('deadline'),
            description=doc.get('description', ''),
            priority=doc.get('priority', 'medium'),
            status=doc.get('status', 'active'),
            created_at=doc.get('created_at'),
            updated_at=doc.get('updated_at'),
            completed_at=doc.get('completed_at')
        )

    def add_savings(self, amount):
        """Add amount to saved total"""
        self.saved_amount += float(amount)
        self.updated_at = datetime.utcnow()

        # Check if goal is completed
        if self.saved_amount >= self.target_amount and self.status == 'active':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()

        return self.saved_amount

    def withdraw_savings(self, amount):
        """Withdraw amount from savings"""
        if amount > self.saved_amount:
            raise ValueError("Cannot withdraw more than saved amount")

        self.saved_amount -= float(amount)
        self.updated_at = datetime.utcnow()

        # Reactivate if was completed
        if self.status == 'completed' and self.saved_amount < self.target_amount:
            self.status = 'active'
            self.completed_at = None

        return self.saved_amount

    def update(self, **kwargs):
        """Update goal fields"""
        allowed_fields = ['title', 'target_amount', 'saved_amount', 'deadline',
                          'description', 'priority', 'status']

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key in ['target_amount', 'saved_amount']:
                    setattr(self, key, float(value))
                elif key == 'deadline' and isinstance(value, str):
                    setattr(self, key, datetime.fromisoformat(value))
                else:
                    setattr(self, key, value)

        self.updated_at = datetime.utcnow()

        # Check completion status
        if self.saved_amount >= self.target_amount and self.status == 'active':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()

    def is_overdue(self):
        """Check if goal is past deadline"""
        if not self.deadline or self.status == 'completed':
            return False

        deadline_dt = self.deadline if isinstance(self.deadline, datetime) else datetime.fromisoformat(self.deadline)
        return datetime.utcnow() > deadline_dt and self.saved_amount < self.target_amount

    def days_remaining(self):
        """Calculate days remaining until deadline"""
        if not self.deadline or self.status == 'completed':
            return None

        deadline_dt = self.deadline if isinstance(self.deadline, datetime) else datetime.fromisoformat(self.deadline)
        delta = deadline_dt - datetime.utcnow()
        return max(0, delta.days)

    def get_progress_percentage(self):
        """Get completion percentage"""
        if self.target_amount <= 0:
            return 0
        return min(100, (self.saved_amount / self.target_amount) * 100)


# ---------------------------- SCHEMAS ---------------------------- #

class SavingsGoalSchema(Schema):
    """
    Marshmallow schema for SavingsGoal validation
    """
    _id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    target_amount = fields.Float(required=True, validate=validate.Range(min=1))
    saved_amount = fields.Float(validate=validate.Range(min=0))
    remaining_amount = fields.Float(dump_only=True)
    progress_percent = fields.Float(dump_only=True)
    deadline = fields.DateTime()
    description = fields.Str(validate=validate.Length(max=500))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    status = fields.Str(validate=validate.OneOf(SavingsGoal.STATUS_OPTIONS))
    is_overdue = fields.Bool(dump_only=True)
    days_remaining = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)

    @validates('saved_amount')
    def validate_saved_amount(self, value):
        if value < 0:
            raise ValidationError("Saved amount cannot be negative")


class SavingsGoalUpdateSchema(Schema):
    """Schema for updating savings goals"""
    title = fields.Str(validate=validate.Length(min=3, max=100))
    target_amount = fields.Float(validate=validate.Range(min=1))
    saved_amount = fields.Float(validate=validate.Range(min=0))
    deadline = fields.DateTime()
    description = fields.Str(validate=validate.Length(max=500))
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high']))
    status = fields.Str(validate=validate.OneOf(SavingsGoal.STATUS_OPTIONS))


class SavingsTransactionSchema(Schema):
    """Schema for adding/withdrawing savings"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    action = fields.Str(required=True, validate=validate.OneOf(['add', 'withdraw']))
    notes = fields.Str(validate=validate.Length(max=200))
