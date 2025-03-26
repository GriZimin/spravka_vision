from ultralytics import YOLO 

model = YOLO("best.pt")

def is_spravka(img_filename):
    result = model.predict(source=f"./uploads/{img_filename}")[0]   
    return (result.probs.top1 == 1)
