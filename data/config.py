import os

from dotenv import load as load_dotenv

load_dotenv('../.env')

if 'TG_BOT_TOKEN' not in os.environ:
    raise Exception('TG_TOKEN_BOT environment variable is missing')
if 'RAPID_API_KEY' not in os.environ:
    raise Exception('RAPID_API_KEY environment variable is missing')

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
API_KEY = os.getenv('RAPID_API_KEY')
