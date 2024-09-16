from abc import ABC, abstractmethod
from typing import Any

from core.types import ImageData


class BaseDetector(ABC):
    @abstractmethod
    def detect(self, image_data: ImageData, with_return: bool = False) -> Any:
        raise NotImplementedError
