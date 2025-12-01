"""
Logging Configuration
Centralized logging setup for the application
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path
from flask import jsonify


def setup_logger(app):
    """
    Setup application logger with file and console handlers
    
    Args:
        app: Flask application instance
    """
    # Create logs directory
    log_dir = Path(__file__).resolve().parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Log file paths
    log_file = log_dir / 'smartbudget.log'
    error_log_file = log_dir / 'error.log'
    access_log_file = log_dir / 'access.log'
    
    # Determine log level
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # Configure formatter
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation (10MB max, keep 10 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.INFO)
    
    # Error file handler (only errors and above)
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Remove default Flask logger
    app.logger.handlers = [file_handler, error_handler, console_handler]
    
    app.logger.info('=' * 60)
    app.logger.info('SmartBudget Application Started')
    app.logger.info(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    app.logger.info(f'Debug Mode: {app.debug}')
    app.logger.info(f'Log Level: {logging.getLevelName(log_level)}')
    app.logger.info('=' * 60)


def setup_request_logging(app):
    """
    Setup request/response logging
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def log_request():
        """Log incoming requests"""
        from flask import request
        app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        from flask import request
        app.logger.info(f'Response: {request.method} {request.path} - {response.status_code}')
        return response


def setup_error_logging(app):
    """
    Setup error logging and handlers
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log unhandled exceptions"""
        app.logger.error(f'Unhandled Exception: {str(e)}', exc_info=True)
        
        # Return error response
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e) if app.debug else 'An error occurred'
        }), 500
    
    @app.errorhandler(404)
    def handle_404(e):
        """Log 404 errors"""
        from flask import request, jsonify
        app.logger.warning(f'404 Not Found: {request.method} {request.path}')
        return jsonify({
            'success': False,
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_500(e):
        """Log 500 errors"""
        app.logger.error(f'500 Internal Server Error: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An internal error occurred'
        }), 500


def get_logger(name):
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Use the same configuration as app logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


class RequestLogger:
    """
    Context manager for detailed request logging
    """
    def __init__(self, logger, request_type):
        self.logger = logger
        self.request_type = request_type
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f'Starting {self.request_type}')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f'Completed {self.request_type} in {duration:.2f}s')
        else:
            self.logger.error(
                f'Failed {self.request_type} after {duration:.2f}s: {exc_val}',
                exc_info=True
            )


def log_function_call(func):
    """
    Decorator to log function calls
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f'Calling {func.__name__} with args={args}, kwargs={kwargs}')
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f'{func.__name__} completed successfully')
            return result
        except Exception as e:
            logger.error(f'{func.__name__} failed: {str(e)}', exc_info=True)
            raise
    
    return wrapper


def log_performance(threshold_seconds=1.0):
    """
    Decorator to log slow function calls
    
    Args:
        threshold_seconds: Log warning if function takes longer than this
    
    Usage:
        @log_performance(threshold_seconds=0.5)
        def slow_function():
            pass
    """
    from functools import wraps
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            duration = time.time() - start_time
            if duration > threshold_seconds:
                logger.warning(
                    f'{func.__name__} took {duration:.2f}s (threshold: {threshold_seconds}s)'
                )
            
            return result
        
        return wrapper
    return decorator


# Export all functions
__all__ = [
    'setup_logger',
    'setup_request_logging',
    'setup_error_logging',
    'get_logger',
    'RequestLogger',
    'log_function_call',
    'log_performance'
]