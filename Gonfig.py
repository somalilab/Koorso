# 📄 config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME', '@SomalibotMasterBot')
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    
    # AI APIs
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    
    # Security
    DEBUG = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # File Settings
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Contact Information
    CONTACTS = {
        'telegram': '@Mfaratoon',
        'email': 'somalibotmaster@gmail.com',
        'website': 'Somalibotmaster.net'
    }

# Verify required keys
def verify_config():
    required_keys = ['TELEGRAM_TOKEN']
    for key in required_keys:
        if not getattr(Config, key):
            raise ValueError(f"❌ {key} ma lahan value. Hubi .env file-ka!")
    print("✅ Configuration waa sax!")

if __name__ == "__main__":
    verify_config()