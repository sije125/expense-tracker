#!/usr/bin/env python3
"""
Setup script for Plaid integration

This script helps you set up Plaid credentials and test the connection.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file with Plaid configuration"""
    
    print("🔧 PLAID SETUP")
    print("=" * 50)
    print("To use Plaid integration, you need API credentials from Plaid.")
    print("📝 Get them at: https://dashboard.plaid.com/")
    print()
    
    # Check if .env already exists
    if Path('.env').exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    print("Enter your Plaid credentials:")
    client_id = input("Plaid Client ID: ").strip()
    secret_key = input("Plaid Secret Key: ").strip()
    
    if not client_id or not secret_key:
        print("❌ Client ID and Secret Key are required!")
        return False
    
    print("\nSelect environment:")
    print("1. Sandbox (testing)")
    print("2. Development (live data, limited to 100 items)")
    print("3. Production (live data, no limits)")
    
    env_choice = input("Environment (1-3): ").strip()
    
    env_map = {
        '1': 'sandbox',
        '2': 'development', 
        '3': 'production'
    }
    
    plaid_env = env_map.get(env_choice, 'sandbox')
    
    # Generate Flask secret key
    import secrets
    flask_secret = secrets.token_hex(32)
    
    # Create .env file
    env_content = f"""# Plaid API Configuration
PLAID_CLIENT_ID={client_id}
PLAID_SECRET={secret_key}
PLAID_ENV={plaid_env}

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}

# Optional: Webhook URL for real-time updates
# PLAID_WEBHOOK_URL=https://your-app.com/webhooks/plaid
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file with {plaid_env} environment")
    return True


def test_plaid_connection():
    """Test Plaid connection"""
    
    print("\n🧪 TESTING PLAID CONNECTION")
    print("=" * 50)
    
    try:
        from plaid_client import PlaidClient
        
        client = PlaidClient()
        print("✅ Plaid client initialized successfully")
        
        # Try to create a link token (this tests API connectivity)
        link_token = client.create_link_token()
        print("✅ Plaid API connection working")
        print(f"✅ Link token created: {link_token[:20]}...")
        
        return True
        
    except ImportError:
        print("❌ Plaid Python library not installed")
        print("💡 Install with: pip install plaid-python")
        return False
        
    except Exception as e:
        print(f"❌ Plaid connection failed: {e}")
        print("💡 Check your credentials in .env file")
        return False


def install_dependencies():
    """Install required dependencies"""
    
    print("\n📦 INSTALLING DEPENDENCIES")
    print("=" * 50)
    
    try:
        import subprocess
        import sys
        
        # Check if requirements.txt exists
        if not Path('requirements.txt').exists():
            print("❌ requirements.txt not found!")
            return False
        
        print("Installing Python packages...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def main():
    """Main setup flow"""
    
    print("🚀 EXPENSE TRACKER - PLAID SETUP")
    print("=" * 50)
    print("This script will help you set up Plaid integration for secure bank connections.")
    print()
    
    # Step 1: Install dependencies
    print("Step 1: Install Dependencies")
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Step 2: Create .env file
    print("\nStep 2: Configure Plaid Credentials")
    if not create_env_file():
        print("❌ Setup failed at credential configuration")
        sys.exit(1)
    
    # Step 3: Test connection
    print("\nStep 3: Test Connection")
    if not test_plaid_connection():
        print("❌ Setup failed at connection test")
        print("💡 Double-check your Plaid credentials and try again")
        sys.exit(1)
    
    # Success!
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("You can now use Plaid integration:")
    print()
    print("📊 Commands:")
    print("   python main.py web           # Start web interface")
    print("   python main.py plaid-connect # Connect bank accounts")
    print("   python main.py plaid-analyze # Analyze connected accounts")
    print("   python main.py interactive   # Interactive mode")
    print()
    print("🌐 Web Interface:")
    print("   python main.py web")
    print("   Open http://localhost:5000 in your browser")
    print()
    print("🔒 Security Notes:")
    print("   - Your .env file contains sensitive credentials")
    print("   - Never commit .env to version control")
    print("   - Bank credentials are handled securely by Plaid")


if __name__ == "__main__":
    main()