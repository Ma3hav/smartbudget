"""
Category Model - Custom expense categories
"""

from datetime import datetime
from bson import ObjectId
from marshmallow import Schema, fields, validate


class Category:
    """
    Custom category model for organizing expenses
    """
    
    def __init__(self, user_id, name, icon=None, color=None, 
                budget_limit=None, is_default=False, 
                created_at=None, updated_at=None, _id=None):
        self._id = _id or ObjectId()
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.name = name.strip()
        self.icon = icon or 'tag'
        self.color = color or '#D2042D'
        self.budget_limit = budget_limit
        self.is_default = is_default
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            '_id': str(self._id),
            'user_id': str(self.user_id),
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'budget_limit': self.budget_limit,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_mongo(self):
        """Convert category to MongoDB document"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'budget_limit': self.budget_limit,
            'is_default': self.is_default,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_mongo(doc):
        """Create Category instance from MongoDB document"""
        if not doc:
            return None
        
        return Category(
            _id=doc.get('_id'),
            user_id=doc.get('user_id'),
            name=doc.get('name'),
            icon=doc.get('icon'),
            color=doc.get('color'),
            budget_limit=doc.get('budget_limit'),
            is_default=doc.get('is_default', False),
            created_at=doc.get('created_at'),
            updated_at=doc.get('updated_at')
        )
    
    def update(self, **kwargs):
        """Update category fields"""
        allowed_fields = ['name', 'icon', 'color', 'budget_limit']
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()


class CategorySchema(Schema):
    """
    Marshmallow schema for Category validation
    """
    _id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    icon = fields.Str(validate=validate.Length(max=50))
    color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    budget_limit = fields.Float(validate=validate.Range(min=0))
    is_default = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CategoryUpdateSchema(Schema):
    """Schema for updating categories"""
    name = fields.Str(validate=validate.Length(min=2, max=50))
    icon = fields.Str(validate=validate.Length(max=50))
    color = fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'))
    budget_limit = fields.Float(validate=validate.Range(min=0))