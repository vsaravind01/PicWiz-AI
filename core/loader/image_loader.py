from uuid import uuid4

import os
import uuid
from PIL import Image, ExifTags
from typing import Generator
from core.types import EmbeddingData, ImageData


class ImageLoader:

    def __init__(self, images: str | list[str], auto_load: bool = False):
        if isinstance(images, str):
            if os.path.isdir(images):
                for root, _, files in os.walk(images):
                    self.images = [os.path.join(root, file) for file in files]
        else:
            self.images = images
        self.image_data: dict[uuid.UUID, ImageData] = {}
        self.faces: dict[tuple[uuid.UUID, str], EmbeddingData] = {}
        self._is_faces_detected = False

        if auto_load:
            self.load()

    def __del__(self):
        for _, img in self.image_data.items():
            img.image.close()

    def __enter__(self):
        self.load()
        return self.image_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        for _, img in self.image_data.items():
            img.image.close()

    def update_face_index(self):
        for _, img in self.image_data.items():
            for face_key, face in img.faces.items():
                self.faces[(img.id, face_key)] = face

    def get_face(self, img_id: uuid.UUID, face_key: str):
        return self.faces[(img_id, face_key)]

    def get_faces(self, img_id: uuid.UUID):
        return self.image_data[img_id].faces

    def iter(self) -> Generator[tuple[uuid.UUID, ImageData], None, None]:
        for key, img in self.image_data.items():
            yield key, img

    def _open_image(self, image: str | Image.Image | bytes) -> Image.Image:
        if isinstance(image, str):
            return Image.open(image)
        elif isinstance(image, Image.Image):
            return image
        elif isinstance(image, bytes):
            return Image.open(image)
        else:
            raise ValueError("Image must be a path or PIL.Image.Image or bytes")

    def load(self):
        if self.image_data:
            for key, img in self.image_data.items():
                self.image_data[key].image = self._open_image(img.image)
                return

        for img in self.images:
            _img = self._open_image(img)
            exif = {ExifTags.TAGS[k]: v for k, v in _img.getexif().items() if k in ExifTags.TAGS}

            metadata = {
                "exif": exif,
                "size": _img.size,
                "mode": _img.mode,
            }

            id = img.split("/")[-1].split(".")[0]

            self.image_data[uuid.UUID(id)] = ImageData(
                id=uuid.UUID(id),
                image=_img,
                meta=metadata,
            )

    def get_embeddings(self):
        embeddings = []
        for _, img in self.image_data.items():
            for face in img.faces:
                embeddings.append(face["embedding"])
        return embeddings
