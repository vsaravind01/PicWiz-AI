import torch
import numpy as np
from torchvision import transforms
from torch.nn import functional as F
from typing import Optional
from core.detect.base import BaseDetector
from wavemix.classification import WaveMix
from core.detect.modules import labels
from core.types import ImageData


tf = transforms.Compose(
    [
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class SceneDetector(BaseDetector):
    model = WaveMix(
        num_classes=365,
        depth=12,
        mult=2,
        ff_channel=256,
        final_dim=256,
        dropout=0.5,
        level=2,
        initial_conv="pachify",
        patch_size=8,
    )
    classes, labels_IO, labels_attribute, W_attribute = labels.load_place_labels()

    def __init__(self) -> None:
        super().__init__()
        url = "https://huggingface.co/cloudwalker/wavemix/resolve/main/Saved_Models_Weights/Places365/places365_54.94.pth"
        self.model.eval()
        self.model.load_state_dict(torch.hub.load_state_dict_from_url(url, map_location="cpu"))

    def detect(
        self, image: ImageData, with_return: bool = False
    ) -> Optional[list[tuple[str, float]]]:
        image.image.seek(0)
        input_img = tf(image.image).unsqueeze(0).to("cpu")

        with torch.no_grad():
            logits = self.model(input_img)
            h_x = F.softmax(logits, 1).data.squeeze()
            scores, idx = h_x.sort(0, True)
            scores = scores.numpy()
            idx = idx.numpy()

        classes = self.get_top_classes(idx, scores)

        image.set_scenes(classes)

        if with_return:
            return classes

    def get_top_classes(
        self, idx: np.ndarray, scores: np.ndarray, top_n: int = 5, threshold: float = 0.075
    ) -> list[tuple[str, float]]:
        io_image = np.mean(self.labels_IO[idx[:10]])
        if io_image < 0.5:
            io = ("indoor", io_image)
        else:
            io = ("outdoor", io_image)

        out = []
        for i in range(0, 10):
            if scores[i] > threshold:
                class_name = self.classes[idx[i]].split(" ")[0].split("/")[-1]
                out.append((class_name, scores[i].item()))
        out.append(io)

        n = min(top_n, len(out))
        out.sort(key=lambda x: x[1], reverse=True)

        return out[:n]
