from __future__ import annotations

from typing import Callable, TypeVar, Generic

import aiohttp

from slowapi import Limiter
from slowapi.util import get_remote_address

__all__ = ("session", "Lazy", "limiter", "expect_value")

# noinspection PyTypeChecker
session: aiohttp.ClientSession = ...
T = TypeVar("T")
limiter = Limiter(key_func=get_remote_address)


class Lazy(Generic[T]):
    def __init__(self, /, constructor: Callable[[], T]):
        self.__constructor = constructor
        self.__value: T = ...

    def __get__(self, instance, owner) -> T:
        if self.__value is ...:
            self.__value = self.__constructor()
        return self.__value


def expect_value(condition: bool, message: Callable[[], str]):
    if not condition:
        raise ValueError(message())
