print("Importing modules")

import cv2
import onnxruntime as ort
import yolo_detect_postprocess
import yolo_preprocess
import recognition


config = {
    "yolo_cursive": "yolo11n_cursive_v6_5.onnx",
    "yolo_cursive_model_classes": ["cursive", "signature", "stamp"]
}


def find_cursives(image):
    # Load ONNX model
    session = ort.InferenceSession(config["yolo_cursive"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    input_shape = session.get_inputs()[0].shape

    # Preprocess the image
    input_blob = yolo_preprocess.preprocess_image(image, input_shape)

    # Run inference with ONNXRuntime
    results = session.run([output_name], {input_name: input_blob})

    # Post-process the output to extract detection results
    boxes, confidences, class_ids = yolo_detect_postprocess.postprocess(results[0], image.shape, input_shape, conf_threshold=0.1)
    
    # Draw the detections on the image
    
    #for box, conf, cls_id in zip(boxes, confidences, class_ids):
    #    left, top, right, bottom = map(int, box)
    #    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
    #    label = f"ID:{cls_id} {conf:.2f}"
    #    cv2.putText(image, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
#
    ## Display the result
    #cv2.imshow("YOLO11m Detection", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    output = []
    for box, conf, cls_id in zip(boxes, confidences, class_ids):
        output.append([box, conf, cls_id])
    
    return output

def crop_cursives(boxes, image, recognizer):
    out = []
    index = 0
    for i in boxes:
        box, conf, cls_id = i
        if cls_id != config["yolo_cursive_model_classes"].index("cursive"):
            out.append((box, conf, cls_id))
            continue
        croped = image[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
        if croped.shape[0] == 0 or croped.shape[1] == 0:
            pass
        word = recognizer.run(croped)
        print(f"{index}: {word}")
        #cv2.imwrite(f"{index}.png", croped)
        index += 1
        out.append((box, conf, cls_id, word))
    return out

def process_image(image_path, out_path):
    print("Finding cursives")
    cv_img = cv2.imread(image_path)
    boxes = find_cursives(cv_img)
    annot_img = cv_img.copy()
    for box in boxes:
        color = (255, 0, 0)
        if box[2] == 1:
            color = (255, 255, 0)
        elif box[2] == 2:
            color = (0, 255, 0)
        cv2.rectangle(annot_img, (int(box[0][0]), int(box[0][1])), (int(box[0][2]), int(box[0][3])), color, 2)
    cv2.imwrite(out_path, annot_img)
    print("Loading recognition model")
    rc = recognition.Recognizer()
    rc.load_model("models/ocr_transformer_4h2l_simple_conv_64x256.pt")
    print("Recognizing")
    return crop_cursives(boxes, cv_img, rc)
