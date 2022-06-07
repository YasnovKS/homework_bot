import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('PRACTICUM_TOKEN')

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {TOKEN}'}

params = {'from_date': 0}

response = requests.get(ENDPOINT,
                        headers=HEADERS,
                        params=params)
response = response.json()

print(response)
