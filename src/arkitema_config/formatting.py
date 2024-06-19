import re
import uuid
from datetime import date, datetime


def str_to_date(date: str):
    return datetime.strptime(date, "%Y-%m-%d").date()


def date_to_str(date: date):
    return date.strftime("%Y-%m-%d")


def str_to_snake(s):
    return re.sub("([A-Z]\w+$)", "_\\1", s).lower()


def dict_to_snake(d):
    if isinstance(d, list):
        return [dict_to_snake(i) if isinstance(i, (dict, list)) else i for i in d]
    return {str_to_snake(a): dict_to_snake(b) if isinstance(b, (dict, list)) else b for a, b in d.items()}


def string_uuid():  # pragma: no cover
    return str(uuid.uuid4())
