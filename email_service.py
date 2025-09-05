#!/usr/bin/env python3
"""
Email service for sending confirmation and password reset emails
"""

from flask_mail import Mail, Message
from flask import current_app, url_for
import os

mail = Mail()


def init_mail(app):
    """Initialize mail with app configuration"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME'))
    
    mail.init_app(app)
    return mail


def send_confirmation_email(user):
    """Send email confirmation email to user"""
    token = user.generate_email_confirmation_token()
    
    subject = 'Confirm Your Email - Expense Tracker'
    
    confirm_url = url_for('confirm_email', token=token, _external=True)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                font-family: Arial, sans-serif; 
                padding: 20px;
            }}
            .header {{ 
                background-color: #0d6efd; 
                color: white; 
                padding: 20px; 
                text-align: center; 
                border-radius: 5px 5px 0 0;
            }}
            .content {{ 
                background-color: #f8f9fa; 
                padding: 30px; 
                border-radius: 0 0 5px 5px;
            }}
            .button {{ 
                background-color: #0d6efd; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 5px; 
                display: inline-block; 
                margin: 20px 0;
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 30px; 
                color: #6c757d; 
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>💰 Expense Tracker</h2>
                <h3>Confirm Your Email Address</h3>
            </div>
            <div class="content">
                <p>Hi there!</p>
                <p>Thank you for signing up for Expense Tracker. To complete your registration, please confirm your email address by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{confirm_url}" class="button">Confirm Email Address</a>
                </p>
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #0d6efd;">{confirm_url}</p>
                <p><strong>This link will expire in 24 hours.</strong></p>
                <p>If you didn't create an account with us, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>This email was sent from Expense Tracker</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Expense Tracker - Confirm Your Email Address
    
    Hi there!
    
    Thank you for signing up for Expense Tracker. To complete your registration, please confirm your email address by visiting this link:
    
    {confirm_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account with us, you can safely ignore this email.
    
    Best regards,
    The Expense Tracker Team
    """
    
    msg = Message(
        subject=subject,
        recipients=[user.email],
        html=html_body,
        body=text_body
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send confirmation email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user):
    """Send password reset email to user"""
    token = user.generate_password_reset_token()
    
    subject = 'Reset Your Password - Expense Tracker'
    
    reset_url = url_for('reset_password', token=token, _external=True)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ 
                max-width: 600px; 
                margin: 0 auto; 
                font-family: Arial, sans-serif; 
                padding: 20px;
            }}
            .header {{ 
                background-color: #dc3545; 
                color: white; 
                padding: 20px; 
                text-align: center; 
                border-radius: 5px 5px 0 0;
            }}
            .content {{ 
                background-color: #f8f9fa; 
                padding: 30px; 
                border-radius: 0 0 5px 5px;
            }}
            .button {{ 
                background-color: #dc3545; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 5px; 
                display: inline-block; 
                margin: 20px 0;
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 30px; 
                color: #6c757d; 
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>💰 Expense Tracker</h2>
                <h3>Reset Your Password</h3>
            </div>
            <div class="content">
                <p>Hi there!</p>
                <p>We received a request to reset your password for your Expense Tracker account. Click the button below to choose a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #dc3545;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
            </div>
            <div class="footer">
                <p>This email was sent from Expense Tracker</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Expense Tracker - Reset Your Password
    
    Hi there!
    
    We received a request to reset your password for your Expense Tracker account. Visit this link to choose a new password:
    
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.
    
    Best regards,
    The Expense Tracker Team
    """
    
    msg = Message(
        subject=subject,
        recipients=[user.email],
        html=html_body,
        body=text_body
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False