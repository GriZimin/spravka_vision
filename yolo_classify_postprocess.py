import cv2
import numpy as np

mapping = ["ne_spravka","spravka"]

def postprocess(outputs):
    outputs = outputs[0]
    m = np.argmax(outputs)
    return (mapping[m], outputs[m])
