import re
import uuid
from datetime import date, datetime


def str_to_date(date: str) -> date:
    return datetime.strptime(date, "%Y-%m-%d").date()


def date_to_str(date: date) -> str:
    return date.strftime("%Y-%m-%d")


def str_to_snake(s: str) -> str:
    return re.sub("([A-Z]\w+$)", "_\\1", s).lower()


def dict_to_snake(d: list[str] | dict[str, str]) -> list[str] | dict[str, str]:
    if isinstance(d, list):
        return [dict_to_snake(i) if isinstance(i, (dict, list)) else i for i in d]
    return {str_to_snake(a): dict_to_snake(b) if isinstance(b, (dict, list)) else b for a, b in d.items()}


def string_uuid() -> str:  # pragma: no cover
    return str(uuid.uuid4())
