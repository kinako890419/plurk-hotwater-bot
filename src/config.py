from dotenv import load_dotenv
import os

def load_config():
    load_dotenv()
    config = {
        'PLURK': {
            'consumer_key': os.getenv('PLURK_CONSUMER_KEY'),
            'consumer_secret': os.getenv('PLURK_CONSUMER_SECRET'),
            'token': os.getenv('PLURK_ACCESS_TOKEN'),
            'token_secret': os.getenv('PLURK_ACCESS_TOKEN_SECRET')
        },
        'GEMINI': {
            'api_key': os.getenv('GEMINI_API_KEY')
        }
    }
    return config