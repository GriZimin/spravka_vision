from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from image_handler import is_spravka, tess_get, draw, process_handwritting, get_name
import shutil
import os
import uuid

try:
    os.mkdir("uploads")
    os.mkdir("processed")
    os.mkdir("processed/printed")
    os.mkdir("processed/handwriten")
except:
    pass

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed/printed", StaticFiles(directory="processed/printed"), name="processed/printed")
app.mount("/processed/handwriten", StaticFiles(directory="processed/handwriten"), name="processed/handwriten")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    file_ext = file.filename.split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{file_ext}"
    save_path = os.path.join("uploads", unique_name)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    spravka_detection = "Класс: "
    text = ""
    name = ""
    if is_spravka(save_path):
        spravka_detection += "справка"
        handwriten = process_handwritting(save_path, os.path.join("processed", "handwriten", unique_name)).replace('\n', "<br>") + "<br>"
        printed = tess_get(unique_name) + "<br>"
        text = handwriten + printed
        name = get_name(printed, handwriten)
        name = name[name.find("<name>"):name.find("</name>")]
        draw(unique_name)
    else:
        spravka_detection += "не справка"


    return JSONResponse(content={
        "result": spravka_detection,
        "name" : name,
        "text" : text,
        "image1_url": f"uploads/{unique_name}",
        "image2_url": f"/processed/printed/{unique_name}",
        "image3_url": f"/processed/handwriten/{unique_name}",
    })

@app.get("/how", response_class=HTMLResponse)
async def how(request: Request):
    return templates.TemplateResponse("how.html", {"request": request})
