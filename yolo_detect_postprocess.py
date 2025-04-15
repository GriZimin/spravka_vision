import cv2
import numpy as np

def postprocess(outputs, image_shape, input_shape, conf_threshold=0.25, iou_threshold=0.4):
    detections = outputs[0]
    boxes = []
    confidences = []
    class_ids = []
    img_h, img_w, _ = image_shape
    nc = 1 # number of classes
    mi = 4 + nc

    detections = detections.transpose(-1, -2)  # shape(1,84,6300) to shape(1,6300,84)

    for detection in detections:
        # Format: [cx, cy, bw, bh,, class_score1, class_score2, ...]
        cx, cy, bw, bh, *obj_confs = detection
        # Get the best class and its score
        cls_id = np.argmax(obj_confs) 
        conf = obj_confs[cls_id]
        
        if conf < conf_threshold:
            continue

        # Convert from center coordinates to top-left coordinates
        left = (cx - bw / 2)
        top = (cy - bh / 2)
        right = (cx + bw / 2)
        bottom = (cy + bh / 2)
        boxes.append([left, top, right, bottom])
        confidences.append(float(conf))
        class_ids.append(int(cls_id))

    # Apply Non-Maximum Suppression to remove overlapping boxes
    indices = cv2.dnn.NMSBoxes([(i[0], i[1], i[2] - i[0], i[3] - i[1]) for i in boxes], confidences, 0, iou_threshold)

    final_boxes, final_confidences, final_class_ids = [], [], []
    if len(indices) > 0:
        for i in indices.flatten():
        #for i in range(len(boxes)):
            final_boxes.append(boxes[i])
            final_confidences.append(confidences[i])
            final_class_ids.append(class_ids[i])
    final_boxes = list(scale_boxes(input_shape[2:], np.array(final_boxes), image_shape))
    return final_boxes, final_confidences, final_class_ids



def scale_boxes(img1_shape, boxes, img0_shape, ratio_pad=None, padding=True, xywh=False):
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (
            round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1),
            round((img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1),
        )  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]
    
    #pad = (pad[0], pad[1])

    if padding:
        boxes[..., 0] -= pad[0]  # x padding
        boxes[..., 1] -= pad[1]  # y padding
        if not xywh:
            boxes[..., 2] -= pad[0]  # x padding
            boxes[..., 3] -= pad[1]  # y padding
    boxes[..., :4] /= gain
    return clip_boxes(boxes, img0_shape)
    #return boxes


def clip_boxes(boxes, shape):
    boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
    boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2
    return boxes