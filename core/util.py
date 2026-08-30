from __future__ import annotations

from typing import Callable, TypeVar, Generic

import aiohttp

__all__ = ("session", "Lazy")

# noinspection PyTypeChecker
session: aiohttp.ClientSession = ...
T = TypeVar("T")


class Lazy(Generic[T]):
    def __init__(self, /, constructor: Callable[[], T]):
        self.__constructor = constructor
        self.__value: T = ...

    def __get__(self, instance, owner) -> T:
        if self.__value is ...:
            self.__value = self.__constructor()
        return self.__value
