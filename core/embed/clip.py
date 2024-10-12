from __future__ import annotations

import os
import joblib
from PIL import Image

pickle_path = os.path.join(os.path.dirname(__file__), "clip.pkl")
model = None


def get_clip_embedding(image: str | Image.Image) -> list[float]:
    global model
    if model is None:
        model = joblib.load(pickle_path)
    return model.encode(image).tolist()  # type: ignore
