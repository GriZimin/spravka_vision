from PIL import Image
import pytesseract
import cv2
import os
import onnxruntime as ort
import yolo_classify_postprocess
import yolo_preprocess
import cursive_reader

model_path = "models/classifier.onnx"

# Load ONNX model
session = ort.InferenceSession(model_path)
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
input_shape = session.get_inputs()[0].shape  # e.g., [1, 3, 640, 640k

def tess_get(img_filename):
    img = Image.open(os.path.join("uploads", img_filename))
    return pytesseract.image_to_string(img, lang="rus")

def draw(img_filename):
    image = cv2.imread(os.path.join("uploads" , img_filename))  
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT, lang="rus")

    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 0 and data['text'][i].strip() != '':
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(os.path.join("processed", "printed", img_filename), image)


def process_handwritting(image_path, output_path):
    data = cursive_reader.process_image(image_path, output_path)
    outstr = ""
    detected_classes = [i[2] for i in data]
    if not(1 in detected_classes):
        outstr += "!!! На справке нет подписи !!!\n"
    else:
        outstr += "На справке есть подпись\n"
    if not(2 in detected_classes):
        outstr += "!!! На справке нет печати !!!\n"
    else:
        outstr += "На справке есть печать\n"
    for elem in data:
        if elem[2] == 0: # cursive
            outstr += f"Cлово ({elem[1]}): {elem[3]}\n"
    return outstr

def is_spravka(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image! :{image_pat}")
        return

    # Preprocess the image
    input_blob = yolo_preprocess.preprocess_image(image, input_shape)

    # Run inference with ONNXRuntime
    results = session.run([output_name], {input_name: input_blob})
    output_data = results[0]

    # Post-process the output to extract detection results
    detected_class, conf = yolo_classify_postprocess.postprocess(output_data)
    return (detected_class == "spravka")
