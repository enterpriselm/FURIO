from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
from io import BytesIO
import base64

from src.codes.fft_segmentation import load_image, gen_masks

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def mask_to_base64(mask: np.ndarray) -> str:
    # Convert binary mask (NumPy array) to a grayscale PIL image
    img = Image.fromarray((mask * 255).astype(np.uint8))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.post("/generate_masks/")
async def generate_masks(file: UploadFile = File(...), low_threshold: float = 0.15, upper_threshold: float = 0.6):
    file_contents = await file.read()
    image = Image.open(BytesIO(file_contents)).convert("L")
    image_array = np.array(image)
    high_freq_mask, low_freq_mask = gen_masks(image_array, low_threshold, upper_threshold)
    high_freq_mask_b64 = mask_to_base64(high_freq_mask)
    low_freq_mask_b64 = mask_to_base64(low_freq_mask)
    return JSONResponse(content={
        "high_frequency_mask": high_freq_mask_b64,
        "low_frequency_mask": low_freq_mask_b64
    })

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())