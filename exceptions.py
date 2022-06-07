from dataclasses import dataclass


@dataclass
class NotFoundError(Exception):
    '''
    Класс для обработки исключений в случае,
    если url недоступен.
    '''

    txt: str


@dataclass
class ResponseTypeError(Exception):
    '''
    Класс для обработки исключений в случае,
    если объект response не является словарем.
    '''
    txt: str


@dataclass
class ResponseValueError(Exception):
    '''
    Класс для обработки исключений в случае,
    если response не содержит данных.
    '''
    txt: str


@dataclass
class NotListRsultError(Exception):
    '''
    Класс для обработки исключений в случае,
    если check_response не является списком.
    '''
    txt: str
