from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from image_handler import is_spravka, tess_get, draw
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
    
    text = ""
    if is_spravka(unique_name):
        text = "СПРАВОЧКА\n"
    else:
        text = "не справка(((((\n"

    text += tess_get(unique_name)
    draw(unique_name)

    return JSONResponse(content={
        "text": text,
        "image_url": f"/processed/printed/{unique_name}"
    })

@app.get("/how", response_class=HTMLResponse)
async def how(request: Request):
    return templates.TemplateResponse("how.html", {"request": request})
