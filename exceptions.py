from dataclasses import dataclass


@dataclass
class NotFoundError(Exception):
    '''
    Класс для обработки исключений в случае,
    если url недоступен.
    '''

    txt: str


class ResponseTypeError(TypeError):
    '''
    Класс для обработки исключений в случае,
    если объект response не является словарем.
    '''
    def __init__(self, text):
        super().__init__()
        self.text = text


@dataclass
class ResponseValueError(Exception):
    '''
    Класс для обработки исключений в случае,
    если response не содержит данных
    '''
    txt: str


@dataclass
class NotListResultError(Exception):
    '''
    Класс для обработки исключений в случае,
    если check_response не является списком.
    '''
    txt: str


class CustomKeyError(KeyError):
    '''
    Класс для обработки исключений в случае,
    если ключ отсутствует в словаре.
    '''
    def __init__(self, text):
        super().__init__()
        self.text = text


class StatusError(KeyError):
    '''
    Класс для обработки исключений в случае,
    если название домашней работы отсутствует
    в списке ключей словаря.
    '''
    def __init__(self, text):
        super().__init__()
        self.text = text


@dataclass
class UpdateError(Exception):
    '''
    Класс для обработки ошибки, возникающей
    при получении пустого списка в ответе
    '''
    txt: str
