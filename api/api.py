import os
import logging
import base64
from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
#from celery import Celery
import cv2
import numpy as np

from api.fft_segmentation import load_image, gen_masks

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# CORS settings from environment (for deployment flexibility)
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure Celery with Redis URL from environment
#redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Default to local Redis
#celery_app = Celery("tasks", broker=redis_url)

#@celery_app.task
#def process_masks(image_array, low_threshold, upper_threshold):
#    return gen_masks(image_array, low_threshold, upper_threshold)

def mask_to_base64(mask: np.ndarray) -> str:
    """Convert binary mask (NumPy array) to base64-encoded PNG string."""
    _, buffer = cv2.imencode('.png', mask)
    return base64.b64encode(buffer).decode("utf-8")

@app.post("/generate_masks/")
async def generate_masks(
    file: UploadFile = File(...), 
    low_threshold: float = Body(...), 
    upper_threshold: float = Body(...)
):
    logger.info(f"File received: {file.filename}, Low threshold: {low_threshold}, Upper threshold: {upper_threshold}")
    
    try:
        # Read and decode image file
        file_contents = await file.read()
        nparr = np.frombuffer(file_contents, np.uint8)
        original_image = mask_to_base64(cv2.imdecode(nparr, cv2.IMREAD_COLOR))
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Generate masks
        high_freq_mask, low_freq_mask = gen_masks(image, low_threshold, upper_threshold)

        # Convert masks to base64
        high_freq_mask_b64 = mask_to_base64(high_freq_mask * 255)
        low_freq_mask_b64 = mask_to_base64(low_freq_mask * 255)

        # Return JSON response
        result = {
            "filename": file.filename,
            "image_array": original_image,
            "high_frequency_mask": high_freq_mask_b64,
            "low_frequency_mask": low_freq_mask_b64
        }
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        return JSONResponse(content={"error": "Failed to process image"}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())

#if __name__ == "__main__":
#    import uvicorn
#    port = int(os.getenv("PORT", 8000))  # Bind to dynamic port or default to 8000 for local testing
#    uvicorn.run(app, host="0.0.0.0", port=port)
