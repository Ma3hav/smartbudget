"""
Routes Package - API endpoints for SmartBudget
"""

from . import auth_routes
from . import expense_routes
from . import category_routes
from . import alert_routes
from . import savings_routes
from . import ml_routes

__all__ = [
    'auth_routes',
    'expense_routes',
    'category_routes',
    'alert_routes',
    'savings_routes',
    'ml_routes'
]