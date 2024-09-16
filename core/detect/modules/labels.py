import os
import numpy as np


def load_place_labels():
    classes_url = (
        "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
    )
    io_places_url = (
        "https://raw.githubusercontent.com/csailvision/places365/master/IO_places365.txt"
    )
    file_name_attribute_url = (
        "https://raw.githubusercontent.com/csailvision/places365/master/labels_sunattribute.txt"
    )
    w_attribute_url = (
        "http://places2.csail.mit.edu/models_places365/W_sceneattribute_wideresnet18.npy"
    )

    if not os.access("categories_places365.txt", os.W_OK):
        os.system("curl " + classes_url + " --output categories_places365.txt")
    if not os.access("IO_places365.txt", os.W_OK):
        os.system("curl " + io_places_url + " --output IO_places365.txt")
    if not os.access("labels_sunattribute.txt", os.W_OK):
        os.system("curl " + file_name_attribute_url + " --output labels_sunattribute.txt")
    if not os.access("W_sceneattribute_wideresnet18.npy", os.W_OK):
        os.system("curl " + w_attribute_url + " --output W_sceneattribute_wideresnet18.npy")

    with open("categories_places365.txt") as class_file:
        lines = class_file.readlines()
        classes = [line.rstrip() for line in lines]

    with open("IO_places365.txt") as io_file:
        lines = io_file.readlines()
        io_classes = [line.rstrip() for line in lines]
        io_classes = [int(i[-1]) - 1 for i in io_classes]

    with open("labels_sunattribute.txt") as attribute_file:
        lines = attribute_file.readlines()
        attributes = [line.rstrip() for line in lines]

    w_attribute = np.load("W_sceneattribute_wideresnet18.npy")

    return classes, np.array(io_classes), attributes, w_attribute
