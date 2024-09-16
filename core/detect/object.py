from typing import Optional
import cv2
import numpy as np

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg, CfgNode
from detectron2.data import MetadataCatalog

from core.types import ImageData
from core.detect.base import BaseDetector


def _get_cfg() -> CfgNode:
    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cpu"
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")

    return cfg


IGNORE_CLASSES = [0]  # 0 - person


class ObjectDetector(BaseDetector):
    cfg = _get_cfg()
    metadata_catalog = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
    predictor = DefaultPredictor(cfg)

    def detect(
        self, image: ImageData, with_return: bool = False
    ) -> Optional[list[tuple[str, float]]]:
        cv2_im = cv2.cvtColor(np.array(image.image), cv2.COLOR_RGB2BGR)
        outputs = self.predictor(cv2_im)

        ids = outputs["instances"].to("cpu").pred_classes.numpy()
        probs = outputs["instances"].to("cpu").scores.numpy()

        ids, probs = self.filter_classes(ids, probs)
        classes = self.map_classes(ids, probs)

        image.set_objects(classes)

        image.update_meta(
            {
                "objects_bbox": outputs.get("instances")
                .to("cpu")
                .pred_boxes.tensor.numpy()
                .tolist(),
            }
        )

        if with_return:
            return classes

    @classmethod
    def filter_classes(cls, ids: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        mask = np.isin(ids, IGNORE_CLASSES, invert=True)
        return ids[mask], scores[mask]

    @classmethod
    def map_classes(cls, ids: np.ndarray, scores: np.ndarray) -> list[tuple[str, float]]:
        return [
            (cls.metadata_catalog.thing_classes[id], float(score)) for id, score in zip(ids, scores)
        ]
