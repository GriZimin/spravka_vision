import cv2
import numpy as np

def preprocess_image(image, input_shape):
    """
    Resize and reshape the image to the network's expected input.
    Assumes input_shape is [N, C, H, W].
    """
    if not(isinstance(image, np.ndarray)):
        image = np.array(image)
    _, _, h, w = input_shape
    # Resize image to (w, h)
    shape = image.shape
    r = min(h / shape[0], w / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = w - new_unpad[0], h - new_unpad[1]  # wh padding
    dw /= 2
    dh /= 2
    resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    resized = cv2.copyMakeBorder(
        resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
    )  # add border
    # Change data layout from HWC to CHW and add batch dimension
    input_blob = resized.transpose(2, 0, 1).astype(np.float32)  # (H, W, C) -> (C, H, W)
    input_blob = np.expand_dims(input_blob, axis=0)
    # Optionally, add normalization/scaling here if required by your model.
    input_blob /= np.float32(255)
    return input_blob