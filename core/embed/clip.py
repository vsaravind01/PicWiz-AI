import os
import joblib
from PIL import Image

pickle_path = os.path.join(os.path.dirname(__file__), "clip.pkl")


def get_clip_embedding(image: str | Image.Image) -> list[float]:
    model = joblib.load(pickle_path)
    return model.encode(image).tolist()  # type: ignore
