"""
Authentication Service - Handles user authentication and authorization
"""

from models.user_model import User
from utils.db_connection import get_users_collection
from utils.jwt_utils import generate_tokens
from utils.validation import is_valid_email, is_valid_password
from bson import ObjectId
from datetime import datetime


class AuthService:
    """Service class for authentication operations"""
    
    def __init__(self):
        self.users = get_users_collection()
    
    def register_user(self, email, name, password):
        """
        Register a new user
        
        Args:
            email (str): User's email
            name (str): User's full name
            password (str): User's password
        
        Returns:
            dict: Success status and user data or error message
        """
        try:
            # Validate email
            if not is_valid_email(email):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Validate password
            is_valid, message = is_valid_password(password)
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            # Check if user already exists
            existing_user = self.users.find_one({'email': email.lower()})
            if existing_user:
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Create new user
            user = User(email=email, name=name)
            user.set_password(password)
            
            # Insert into database
            result = self.users.insert_one(user.to_mongo())
            
            # Generate tokens
            tokens = generate_tokens(result.inserted_id)
            
            # Get created user
            created_user = self.users.find_one({'_id': result.inserted_id})
            user_obj = User.from_mongo(created_user)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user_obj.to_dict(),
                'tokens': tokens
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
    
    def login_user(self, email, password):
        """
        Authenticate user and generate tokens
        
        Args:
            email (str): User's email
            password (str): User's password
        
        Returns:
            dict: Success status and tokens or error message
        """
        try:
            # Find user
            user_doc = self.users.find_one({'email': email.lower()})
            
            if not user_doc:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Create user object
            user = User.from_mongo(user_doc)
            
            # Verify password
            if not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Generate tokens
            tokens = generate_tokens(user._id)
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'tokens': tokens
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: User data or None
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user_doc = self.users.find_one({'_id': user_id})
            
            if user_doc:
                user = User.from_mongo(user_doc)
                return user.to_dict()
            
            return None
        
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_profile(self, user_id, **kwargs):
        """
        Update user profile
        
        Args:
            user_id: User's MongoDB ObjectId or string
            **kwargs: Fields to update
        
        Returns:
            dict: Success status and updated user or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user_doc = self.users.find_one({'_id': user_id})
            
            if not user_doc:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            user = User.from_mongo(user_doc)
            
            # Update profile
            if 'profile' in kwargs:
                user.update_profile(**kwargs['profile'])
            
            # Update settings
            if 'settings' in kwargs:
                user.update_settings(**kwargs['settings'])
            
            # Update name
            if 'name' in kwargs:
                user.name = kwargs['name']
                user.updated_at = datetime.utcnow()
            
            # Save to database
            self.users.update_one(
                {'_id': user_id},
                {'$set': user.to_mongo()}
            )
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Update failed: {str(e)}'
            }
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User's MongoDB ObjectId or string
            old_password (str): Current password
            new_password (str): New password
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user_doc = self.users.find_one({'_id': user_id})
            
            if not user_doc:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            user = User.from_mongo(user_doc)
            
            # Verify old password
            if not user.check_password(old_password):
                return {
                    'success': False,
                    'message': 'Current password is incorrect'
                }
            
            # Validate new password
            is_valid, message = is_valid_password(new_password)
            if not is_valid:
                return {
                    'success': False,
                    'message': message
                }
            
            # Set new password
            user.set_password(new_password)
            
            # Save to database
            self.users.update_one(
                {'_id': user_id},
                {'$set': {
                    'password_hash': user.password_hash,
                    'updated_at': user.updated_at
                }}
            )
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Password change failed: {str(e)}'
            }
    
    def delete_user(self, user_id):
        """
        Delete user account
        
        Args:
            user_id: User's MongoDB ObjectId or string
        
        Returns:
            dict: Success status or error message
        """
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Delete user
            result = self.users.delete_one({'_id': user_id})
            
            if result.deleted_count > 0:
                # TODO: Also delete user's expenses, goals, etc.
                return {
                    'success': True,
                    'message': 'Account deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'User not found'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Account deletion failed: {str(e)}'
            }