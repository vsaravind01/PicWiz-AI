from PIL import Image
from core.loader.image_loader import ImageLoader
from core.embed.face import FaceEmbedder
from core.detect.object import ObjectDetector
from core.detect.scene import SceneDetector

import multiprocessing
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class FaceEmbeddingPipeline:
    def __init__(self, images: str | list[str | Image.Image | bytes]):
        self.loader = ImageLoader(images, auto_load=True)
        self.embedder = FaceEmbedder()

    def run(self):
        event_loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            for img in self.loader.iter():
                # self.embedder.embed(img)
                event_loop.run_in_executor(executor, self.embedder.embed, img)

        return self.loader.image_data


class ObjectDetectionPipeline:
    def __init__(self, images: str | list[str | Image.Image | bytes]):
        self.loader = ImageLoader(images, auto_load=True)
        self.detector = ObjectDetector()

    def run(self):
        event_loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            for img in self.loader.iter():
                # self.detector.detect(img, with_return=True)
                event_loop.run_in_executor(executor, self.detector.detect, img, True)

        return self.loader.image_data


class SceneDetectionPipeline:
    def __init__(self, images: str | list[str | Image.Image | bytes]):
        self.loader = ImageLoader(images, auto_load=True)
        self.detector = SceneDetector()

    def run(self):
        event_loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            for img in self.loader.iter():
                # self.detector.detect(img)
                event_loop.run_in_executor(executor, self.detector.detect, img)

        return self.loader.image_data


def runner(func, return_dict):
    print(f"Running {func.__self__.__class__.__name__}")
    result = func()

    return_dict[func.__self__.__class__.__name__] = result
    print(f"Finished {func.__self__.__class__.__name__}")


if __name__ == "__main__":
    dataset = "./notebooks/datasets/people"
    loader = ImageLoader(dataset, auto_load=True)

    face_pipeline = FaceEmbeddingPipeline(dataset)
    object_pipeline = ObjectDetectionPipeline(dataset)
    scene_pipeline = SceneDetectionPipeline(dataset)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # process1 = multiprocessing.Process(target=runner, args=(face_pipeline.run, return_dict))
    # process1.start()
    # process2 = multiprocessing.Process(target=runner, args=(object_pipeline.run, return_dict))
    # process2.start()
    # process3 = multiprocessing.Process(target=runner, args=(scene_pipeline.run, return_dict))
    # process3.start()

    # process1.join()
    # process2.join()
    # process3.join()

    with ThreadPoolExecutor() as executor:
        for pipeline in [face_pipeline, object_pipeline, scene_pipeline]:
            executor.submit(runner, pipeline.run, return_dict)

    print(return_dict)
