from ultralytics import YOLO 
from PIL import Image
import pytesseract
import cv2
import os

model = YOLO("best.pt")

def is_spravka(img_filename):
    result = model.predict(source=os.path.join("uploads", img_filename))[0]   
    return (result.probs.top1 == 1)

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

    #cv2.imshow('Words', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cv2.imwrite(os.path.join("processed", "printed", img_filename), image)

    # boxes_uploads/img_filename
    # uploads/boxes_img_filename
