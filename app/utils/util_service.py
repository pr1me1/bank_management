from typing import Any, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T', )


class BaseUtilService(ABC):
    @abstractmethod
    def validate(self, text: str) -> Any:
        pass

    @abstractmethod
    def extract(self, text: str) -> Any:
        pass


class UtilService:
    """Collected method set of utils to make project more clean"""
