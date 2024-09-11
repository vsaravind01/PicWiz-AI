from typing import Any, Optional
from numpy import ndarray
from PIL.Image import Image
from torch import Tensor

from pydantic import BaseModel


BoxType = tuple[float, float, float, float] | tuple[int, int, int, int]
ImageType = ndarray | Tensor | Image


class ImageData(BaseModel):
    image: Image
    id: str
    meta: dict = dict()
