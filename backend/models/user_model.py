"""
User Model - Handles user data and authentication
"""

from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate, ValidationError, post_load
import re


class User:
    """
    User model for authentication and profile management
    """
    
    def __init__(self, email, name, password_hash=None, created_at=None, 
                updated_at=None, profile=None, settings=None, _id=None):
        self._id = _id or ObjectId()
        self.email = email.lower().strip()
        self.name = name.strip()
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.profile = profile or {
            'monthly_income': 0,
            'monthly_budget': 0,
            'currency': 'USD',
            'timezone': 'UTC'
        }
        self.settings = settings or {
            'email_notifications': True,
            'budget_alerts': True,
            'weekly_reports': True,
            'theme': 'light'
        }
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        user_dict = {
            '_id': str(self._id),
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'profile': self.profile,
            'settings': self.settings
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
        
        return user_dict
    
    def to_mongo(self):
        """Convert user to MongoDB document"""
        return {
            '_id': self._id,
            'email': self.email,
            'name': self.name,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'profile': self.profile,
            'settings': self.settings
        }
    
    @staticmethod
    def from_mongo(doc):
        """Create User instance from MongoDB document"""
        if not doc:
            return None
        
        return User(
            _id=doc.get('_id'),
            email=doc.get('email'),
            name=doc.get('name'),
            password_hash=doc.get('password_hash'),
            created_at=doc.get('created_at'),
            updated_at=doc.get('updated_at'),
            profile=doc.get('profile'),
            settings=doc.get('settings')
        )
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        - At least 8 characters
        - Contains uppercase and lowercase
        - Contains at least one digit
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain a digit"
        
        return True, "Password is valid"
    
    def update_profile(self, **kwargs):
        """Update user profile fields"""
        allowed_fields = ['monthly_income', 'monthly_budget', 'currency', 'timezone']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                self.profile[key] = value
        
        self.updated_at = datetime.utcnow()
    
    def update_settings(self, **kwargs):
        """Update user settings"""
        allowed_fields = ['email_notifications', 'budget_alerts', 'weekly_reports', 'theme']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                self.settings[key] = value
        
        self.updated_at = datetime.utcnow()


class UserSchema(Schema):
    """
    Marshmallow schema for User validation and serialization
    """
    _id = fields.Str(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(max=255))
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=8))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    profile = fields.Dict(keys=fields.Str(), values=fields.Raw())
    settings = fields.Dict(keys=fields.Str(), values=fields.Raw())
    
    @post_load
    def make_user(self, data, **kwargs):
        """Create User instance from validated data"""
        password = data.pop('password', None)
        user = User(**data)
        
        if password:
            user.set_password(password)
        
        return user


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserUpdateSchema(Schema):
    """Schema for updating user profile"""
    name = fields.Str(validate=validate.Length(min=2, max=100))
    profile = fields.Dict(keys=fields.Str(), values=fields.Raw())
    settings = fields.Dict(keys=fields.Str(), values=fields.Raw())