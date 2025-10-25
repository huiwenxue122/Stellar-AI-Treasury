#!/usr/bin/env python3
"""
Setup script for Stellar AI Treasury System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        env_content = """# Stellar Testnet Configuration
# Get your testnet keys from: https://laboratory.stellar.org/#account-creator
STELLAR_SECRET=your_stellar_secret_key_here
STELLAR_PUBLIC=your_stellar_public_key_here

# OpenAI Configuration (optional, for future AI features)
OPENAI_API_KEY=your_openai_api_key_here
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env file with your actual Stellar testnet keys")
    else:
        print("✅ .env file already exists")

def check_stellar_keys():
    """Check if Stellar keys are configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    secret = os.getenv("STELLAR_SECRET")
    public = os.getenv("STELLAR_PUBLIC")
    
    if not secret or secret == "your_stellar_secret_key_here":
        print("⚠️  STELLAR_SECRET not configured in .env file")
        return False
    
    if not public or public == "your_stellar_public_key_here":
        print("⚠️  STELLAR_PUBLIC not configured in .env file")
        return False
    
    print("✅ Stellar keys are configured")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Stellar AI Treasury System")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create .env file
    create_env_file()
    
    # Check Stellar keys
    keys_configured = check_stellar_keys()
    
    print("\n" + "=" * 50)
    if keys_configured:
        print("🎉 Setup completed successfully!")
        print("You can now run: python test_system.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please configure your Stellar testnet keys in .env file")
        print("Get testnet keys from: https://laboratory.stellar.org/#account-creator")
    
    return True

if __name__ == "__main__":
    main()
