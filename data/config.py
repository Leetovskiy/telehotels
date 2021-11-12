import os
from sys import argv

from dotenv import load as load_dotenv

load_dotenv('../.env')

if 'TG_BOT_TOKEN' not in os.environ:
    raise Exception('TG_TOKEN_BOT environment variable is missing')
if 'RAPID_API_KEY' not in os.environ:
    raise Exception('RAPID_API_KEY environment variable is missing')
if ('WEBHOOK_HOST' not in os.environ) and ('--webhook' in argv):
    raise Exception('WEBHOOK_HOST environment variable is missing')

BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
API_KEY = os.getenv('RAPID_API_KEY')
DATABASE_PATH = os.getenv('DATABASE_PATH')

URL_SECRET = BOT_TOKEN
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_URL = f'https://{WEBHOOK_HOST}/{URL_SECRET}'
