from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import logging
import base64

from api.fft_segmentation import load_image, gen_masks
from celery import Celery

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task
def process_masks(image_array, low_threshold, upper_threshold):
    return gen_masks(image_array, low_threshold, upper_threshold)

def mask_to_base64(mask: np.ndarray) -> str:
    # Convert bi111111nary mask (NumPy array) to a grayscale PIL image
    _, buffer = cv2.imencode('.png', mask)
    return base64.b64encode(buffer).decode("utf-8")

@app.post("/generate_masks/")
async def generate_masks(file: UploadFile = File(...), low_threshold: float = Body(...), upper_threshold: float = Body(...)):
    # Load the image using OpenCV and convert to grayscale
    logger.info(f"File received: {file.filename}, Low threshold: {low_threshold}, Upper threshold: {upper_threshold}")

    # Read the uploaded image file
    file_contents = await file.read()
    nparr = np.frombuffer(file_contents, np.uint8)

    # Decode the image to both color and grayscale formats
    original_image = mask_to_base64(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # Generate high-frequency and low-frequency masks
    high_freq_mask, low_freq_mask = gen_masks(image, low_threshold, upper_threshold)

    # Convert masks to base64 format for JSON response
    high_freq_mask_b64 = mask_to_base64(high_freq_mask * 255)
    low_freq_mask_b64 = mask_to_base64(low_freq_mask * 255)

    # Prepare and return JSON response
    result = {
        "filename": file.filename,
        "image_array": original_image,
        "high_frequency_mask": high_freq_mask_b64,
        "low_frequency_mask": low_freq_mask_b64
    }

    return JSONResponse(content=result)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())