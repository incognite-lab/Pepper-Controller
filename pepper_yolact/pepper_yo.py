import pybullet as p
import gym
import sys
import os
from ciircgym import envs
import torch
import cv2
import numpy as np
import pkg_resources
import subprocess
import os
import threading
import json
from copy import copy
from PIL import Image
import matplotlib.pyplot as plt
import scipy.misc

sys.path.append(pkg_resources.resource_filename("ciircgym", "yolact_vision"))
#sys.path.append(pkg_resources.resource_filename("ciircgym", "pepper_controller"))

from inference_tool import InfTool
# from ciircyolact_vision import eval
from yolact import Yolact
from data import cfg, set_cfg, set_dataset
import eval as ev
from utils.augmentations import FastBaseTransform
from utils.functions import SavePath
from ciircgym.yolact_vision import yolact
from ciircgym.envs.wrappers import RandomizedEnvWrapper

isFinished = False


def assignDirections(class_names, centroids):
    if not centroids:
        return {}
    xCentroids = [row[0] for row in centroids]
    center = max(xCentroids) - min(xCentroids)
    directions = {}
    for i in range(0, len(centroids)):
        if xCentroids[i] < center:
            directions[class_names[i]] = "left"
        else:
            directions[class_names[i]] = "right"
    return directions


def dumpData(data):
    with open('classes.json', 'w') as f:
        try:
            json.dump(data, f)
        except:
            dumpData(data)


def getData():
    with open("classes.json") as f:
        try:
            return json.load(f)
        except:
            return getData()


def assignAndDumpData(init, class_names, class_names_upd,
                      directions, directions_upd):
    data = {'init': init, 'class_names': class_names, 'directions': directions,
            'class_names_upd': class_names_upd,
            'directions_upd': directions_upd}
    dumpData(data)


def firstJsonUpdate(class_names, directions):
    assignAndDumpData("true", class_names,
                      class_names, directions, directions)


def normalJsonUpdate(class_names, directions):
    oldData = getData()
    assignAndDumpData("false", copy(oldData['class_names']), class_names,
                      copy(oldData['directions']), directions)


def updateInfo(class_names, directions):
    data = getData()
    if data["init"] == "true":
        firstJsonUpdate(class_names, directions)
    else:
        normalJsonUpdate(class_names, directions)


def streamPepperCamera():
    subprocess.run(["python2", fileName, '--speak_constantly=True'])
    global isFinished
    isFinished = True


def clean(image):
    os.remove(image)
    data = {"init": "true"}
    dumpData(data)


if __name__ == "__main__":
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    fileName = os.path.join(fileDir, "../yolactDemo.py")
    fileName = os.path.abspath(os.path.realpath(fileName))
    name = "camera.jpg"
    #weights = pkg_resources.resource_filename("ciircgym",
                                              #"yolact_vision/data/yolact/weights/weights_yolact_25/crow_base_25_133333.pth")
    # path to saved config obj or name of an existing one in the Config script (e.g. 'yolact_base_config') or None for autodetection
    weights = pkg_resources.resource_filename("ciircgym",
                                               "yolact_vision/data/yolact/weights/yolact_base_54_800000.pth")
    model_path = SavePath.from_str(weights)
    config = model_path.model_name + '_config'
    #config = pkg_resources.resource_filename("ciircgym",
                                    #"yolact_vision/data/yolact/weights/weights_yolact_25/config_train.obj")
    cnn = InfTool(weights=weights, config=config, score_threshold=0.35)

    pepperThread = threading.Thread(target=streamPepperCamera)
    pepperThread.start()

    while not isFinished:
        img = cv2.imread(name)
        if img is None:
            continue
        else:
            preds, frame = cnn.process_batch(img)
            classes, class_names, scores, boxes, masks, centroids = cnn.raw_inference(img, preds=preds,frame=frame)
            updateInfo(class_names, assignDirections(class_names, centroids))
            img_numpy = cnn.label_image(img, preds=preds)
            cv2.imshow('img_yolact', img_numpy)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    clean(name)  # correct this
