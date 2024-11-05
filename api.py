from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
from io import BytesIO
import base64

from src.codes.fft_segmentation import load_image, gen_masks

app = FastAPI()

def mask_to_base64(mask: np.ndarray) -> str:
    # Convert binary mask (NumPy array) to a grayscale PIL image
    img = Image.fromarray((mask * 255).astype(np.uint8))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.post("/generate_masks/")
async def generate_masks(file: UploadFile = File(...), low_threshold: float = 0.15, upper_threshold: float = 0.6):
    # Read the file asynchronously
    file_contents = await file.read()
    
    # Load the image from bytes
    image = Image.open(BytesIO(file_contents)).convert("L")
    image_array = np.array(image)
    
    # Generate the high and low frequency masks
    high_freq_mask, low_freq_mask = gen_masks(image_array, low_threshold, upper_threshold)
    
    # Convert masks to base64 to include in JSON response
    high_freq_mask_b64 = mask_to_base64(high_freq_mask)
    low_freq_mask_b64 = mask_to_base64(low_freq_mask)

    # Return the masks as base64-encoded strings
    return JSONResponse(content={
        "high_frequency_mask": high_freq_mask_b64,
        "low_frequency_mask": low_freq_mask_b64
    })
