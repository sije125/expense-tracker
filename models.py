#!/usr/bin/env python3
"""
Database models for the expense tracker application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import re

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    email_confirmation_token = db.Column(db.String(100), unique=True, nullable=True)
    email_confirmation_sent_at = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(100), unique=True, nullable=True)
    password_reset_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set password"""
        if not self.is_password_valid(password):
            raise ValueError("Password does not meet requirements")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def is_password_valid(password):
        """
        Validate password requirements:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one number
        - Contains at least one special character
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
    
    def generate_email_confirmation_token(self):
        """Generate a secure token for email confirmation"""
        self.email_confirmation_token = secrets.token_urlsafe(32)
        self.email_confirmation_sent_at = datetime.utcnow()
        return self.email_confirmation_token
    
    def generate_password_reset_token(self):
        """Generate a secure token for password reset"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_sent_at = datetime.utcnow()
        return self.password_reset_token
    
    def is_email_confirmation_valid(self):
        """Check if email confirmation token is still valid (24 hours)"""
        if not self.email_confirmation_sent_at:
            return False
        return datetime.utcnow() - self.email_confirmation_sent_at < timedelta(hours=24)
    
    def is_password_reset_valid(self):
        """Check if password reset token is still valid (1 hour)"""
        if not self.password_reset_sent_at:
            return False
        return datetime.utcnow() - self.password_reset_sent_at < timedelta(hours=1)
    
    def confirm_email(self):
        """Mark email as confirmed and clear token"""
        self.is_email_confirmed = True
        self.email_confirmation_token = None
        self.email_confirmation_sent_at = None
    
    def reset_password(self, new_password):
        """Reset password and clear reset token"""
        self.set_password(new_password)
        self.password_reset_token = None
        self.password_reset_sent_at = None
    
    def __repr__(self):
        return f'<User {self.email}>'