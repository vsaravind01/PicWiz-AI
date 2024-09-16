import numpy as np
import torch


def recursion_change_bn(module):
    if isinstance(module, torch.nn.BatchNorm2d):
        module.track_running_stats = True
    else:
        for _, module1 in module._modules.items():
            module1 = recursion_change_bn(module1)
    return module


features_blobs = []


def hook_feature(module, input, output):
    features_blobs.append(np.squeeze(output.data.cpu().numpy()))
