import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# CORS settings from environment (for deployment flexibility)
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")  # Allow all by default or use comma-separated list

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure form submissions directory exists
submissions_dir = "form_submissions"
os.makedirs(submissions_dir, exist_ok=True)
form_file_path = os.path.join(submissions_dir, "submissions.json")

class ContactForm(BaseModel):
    name: str
    email: str
    company: str
    role: str

@app.post("/submit-form")
async def submit_form(form_data: ContactForm):
    try:
        # Load existing form data if the file exists, else initialize an empty list
        if os.path.exists(form_file_path):
            with open(form_file_path, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        # Add the new form submission
        existing_data.append(form_data.dict())
        
        # Save the updated data back to the file
        with open(form_file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)

        logger.info(f"Form submission received from {form_data.name} at {form_data.email}")
        return {"message": "Thank you for reaching out!"}

    except Exception as e:
        logger.error(f"Error saving form data: {e}")
        raise HTTPException(status_code=500, detail="Error saving form data")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))  # Bind to dynamic port or fallback to 8001 for local testing
    uvicorn.run(app, host="0.0.0.0", port=port)
