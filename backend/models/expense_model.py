"""
Expense Model - Handles expense transactions
"""

from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate, validates, ValidationError
from typing import Optional


class Expense:
    """
    Expense model for tracking user expenses
    """
    
    VALID_CATEGORIES = [
        'Food', 'Transport', 'Shopping', 'Bills', 
        'Entertainment', 'Healthcare', 'Other'
    ]
    
    VALID_PAYMENT_TYPES = [
        'Credit Card', 'Debit Card', 'Cash', 'UPI', 'Bank Transfer'
    ]
    
    def __init__(self, user_id, amount, category, payment_type, 
                date=None, notes='', tags=None, receipt_url=None,
                created_at=None, updated_at=None, _id=None):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.amount = float(amount)
        self.category = category
        self.payment_type = payment_type
        self.date = date or datetime.utcnow()
        self.notes = notes.strip() if notes else ''
        self.tags = tags or []
        self.receipt_url = receipt_url
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'amount': self.amount,
            'category': self.category,
            'payment_type': self.payment_type,
            'date': self.date.isoformat() if isinstance(self.date, datetime) else self.date,
            'notes': self.notes,
            'tags': self.tags,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_mongo(self):
        """Convert expense to MongoDB document"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'amount': self.amount,
            'category': self.category,
            'payment_type': self.payment_type,
            'date': self.date if isinstance(self.date, datetime) else datetime.fromisoformat(self.date),
            'notes': self.notes,
            'tags': self.tags,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_mongo(doc):
        """Create Expense instance from MongoDB document"""
        if not doc:
            return None
        
        return Expense(
            _id=doc.get('_id'),
            user_id=doc.get('user_id'),
            amount=doc.get('amount'),
            category=doc.get('category'),
            payment_type=doc.get('payment_type'),
            date=doc.get('date'),
            notes=doc.get('notes', ''),
            tags=doc.get('tags', []),
            receipt_url=doc.get('receipt_url'),
            created_at=doc.get('created_at'),
            updated_at=doc.get('updated_at')
        )
    
    def update(self, **kwargs):
        """Update expense fields"""
        allowed_fields = [
            'amount', 'category', 'payment_type', 'date', 
            'notes', 'tags', 'receipt_url'
        ]
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                if key == 'amount':
                    setattr(self, key, float(value))
                elif key == 'date' and isinstance(value, str):
                    setattr(self, key, datetime.fromisoformat(value))
                else:
                    setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def validate_category(category):
        """Validate expense category"""
        return category in Expense.VALID_CATEGORIES
    
    @staticmethod
    def validate_payment_type(payment_type):
        """Validate payment type"""
        return payment_type in Expense.VALID_PAYMENT_TYPES


class ExpenseSchema(Schema):
    """
    Marshmallow schema for Expense validation
    """
    _id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01, min_inclusive=True))
    category = fields.Str(required=True, validate=validate.OneOf(Expense.VALID_CATEGORIES))
    payment_type = fields.Str(required=True, validate=validate.OneOf(Expense.VALID_PAYMENT_TYPES))
    date = fields.DateTime(missing=datetime.utcnow)
    notes = fields.Str(validate=validate.Length(max=500))
    tags = fields.List(fields.Str(), missing=[])
    receipt_url = fields.Str(validate=validate.URL())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('amount')
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Amount must be greater than 0")
        if value > 1000000:
            raise ValidationError("Amount seems unreasonably high")


class ExpenseUpdateSchema(Schema):
    """Schema for updating expenses"""
    amount = fields.Float(validate=validate.Range(min=0.01))
    category = fields.Str(validate=validate.OneOf(Expense.VALID_CATEGORIES))
    payment_type = fields.Str(validate=validate.OneOf(Expense.VALID_PAYMENT_TYPES))
    date = fields.DateTime()
    notes = fields.Str(validate=validate.Length(max=500))
    tags = fields.List(fields.Str())
    receipt_url = fields.Str(validate=validate.URL())


class ExpenseFilterSchema(Schema):
    """Schema for filtering expenses"""
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    category = fields.Str(validate=validate.OneOf(Expense.VALID_CATEGORIES))
    payment_type = fields.Str(validate=validate.OneOf(Expense.VALID_PAYMENT_TYPES))
    min_amount = fields.Float(validate=validate.Range(min=0))
    max_amount = fields.Float(validate=validate.Range(min=0))
    tags = fields.List(fields.Str())