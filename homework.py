import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (NotFoundError, ResponseTypeError,
                        ResponseValueError, NotListResultError,
                        CustomKeyError, StatusError, UpdateError)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# В переменной EXCEPTIONS будет содержаться информация об ошибках,
# возникающих во время работы бота.
EXCEPTIONS = {
    'NotFoundError': False,
    'ResponseTypeError': False,
    'ResponseValueError': False,
    'CustomKeyError': False,
    'NotListResultError': False,
    'KeyError': False,
    'UpdateError': False
}


def send_message(bot, message: str):
    """Отправляет пользователю текстовое сообщение."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                     text=message)


def get_api_answer(current_timestamp):
    """
    Функция обращается к API-сервису и возвращает информацию
    о статусе домашней работы.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT,
                            headers=HEADERS,
                            params=params
                            )
    if response.status_code != HTTPStatus.OK:
        raise NotFoundError('Не удалось подключиться к API.')
    # Сбрасываем ошибку подключения к API, если она была ранее:
    EXCEPTIONS['NotFoundError'] = False
    response = response.json()
    return response


def check_response(response):
    """
    Функция проверяет корректность ответа API и
    возвращает его для дальнейшей обработки.
    """
    # Проверяем, что в ответе API нам возвращается словарь:
    if not isinstance(response, dict):
        raise ResponseTypeError('Запрос к API вернул не то, что ожидалось')
    if not response.keys():
        raise ResponseValueError('Объект response не содержит данных')
    # Сбрасываем возможные ошибки, если они были ранее:
    EXCEPTIONS['ResponseTypeError'] = False
    EXCEPTIONS['ResponseValueError'] = False
    homework = response.get('homeworks',
                            KeyError('Ответ от API не содержит '
                                     'ключа "homeworks"'
                                     )
                            )
    if not isinstance(homework, list):
        raise NotListResultError('Объект "homework" не является списком')
    # Сбрасываем возможную ошибку несоответствия типа данных классу list:
    EXCEPTIONS['NotListResultError'] = False
    return homework


def parse_status(homework):
    """
    Функция достает из ответа API данные о названии и статусе
    домашнего задания
    """
    if not homework:
        raise UpdateError('На данный момент нет обновлений.')
    # Сбрасываем ошибку, если ранее статус отсутствовал в словаре:
    EXCEPTIONS['UpdateError'] = False
    homework_name = homework[0].get('homework_name')
    homework_status = homework[0].get('status')
    # Сбрасываем ошибку, если ранее статус отсутствовал в словаре:
    EXCEPTIONS['StatusError'] = False
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise StatusError('В словаре документированных статусов отсутствует '
                          f'статус {homework_status}')

    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """
    Функция проверяет доступность переменных окружения
    для корректной работы бота.
    """
    vars = {'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
            }
    for name, var in vars.items():
        if not var:
            logging.critical(f'Отсутствует переменная окружения {name}')
            return False
    return True


def main():
    """Основная логика работы бота."""

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        if check_tokens():
            try:
                response = get_api_answer(current_timestamp)
                homework = check_response(response)
                message = parse_status(homework)
                send_message(bot, message)
                current_timestamp = response.get('current_date')
                time.sleep(RETRY_TIME)

            except (NotFoundError, ResponseValueError,
                    NotListResultError, ResponseTypeError,
                    KeyError, CustomKeyError) as error:
                logging.error('В результате работы бота '
                              'возникла ошибка: '
                              f'{type(error).__name__}: {error}'
                              )
                if not EXCEPTIONS[type(error).__name__]:
                    message = ('В результате работы бота возникла '
                               f'ошибка: {error}')
                    send_message(bot, message)
                    EXCEPTIONS[type(error).__name__] = True
                time.sleep(RETRY_TIME)

            except UpdateError as error:
                logging.info(f'{type(error).__name__}: {error}')
                if not EXCEPTIONS[type(error).__name__]:
                    message = (f'{error}')
                    send_message(bot, message)
                    EXCEPTIONS[type(error).__name__] = True
                time.sleep(RETRY_TIME)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logging.error('В результате работы бота возникла '
                              f'ошибка: {type(error).__name__}: {error}')
                time.sleep(RETRY_TIME)
        else:
            break


if __name__ == '__main__':
    main()
