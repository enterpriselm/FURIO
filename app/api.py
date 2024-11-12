from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from io import BytesIO
import base64

from src.codes.fft_segmentation import load_image, gen_masks
from celery import Celery

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task
def process_masks(image_array, low_threshold, upper_threshold):
    return gen_masks(image_array, low_threshold, upper_threshold)

def mask_to_base64(mask: np.ndarray) -> str:
    # Convert binary mask (NumPy array) to a grayscale PIL image
    _, buffer = cv2.imencode('.png', mask)
    return base64.b64encode(buffer).decode("utf-8")

@app.post("/generate_masks/")
async def generate_masks(files: list[UploadFile] = File(...), low_threshold: float = 0.15, upper_threshold: float = 0.6):
    results = []
    for file in files:
        file_contents = await file.read()
        # Load the image using OpenCV and convert to grayscale
        nparr = np.frombuffer(file_contents, np.uint8)
        original_image = mask_to_base64(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Generate high-frequency and low-frequency masks
        high_freq_mask, low_freq_mask = gen_masks(image, low_threshold, upper_threshold)
        
        # Convert the masks to base64 for response
        high_freq_mask_b64 = mask_to_base64(high_freq_mask * 255)
        low_freq_mask_b64 = mask_to_base64(low_freq_mask * 255)
        
        results.append({
            "filename": file.filename,
            "image_array": original_image,
            "high_frequency_mask": high_freq_mask_b64,
            "low_frequency_mask": low_freq_mask_b64
        })

    return JSONResponse(content=results)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())