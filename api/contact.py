from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

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

if not os.path.exists('form_submissions'):
    os.makedirs('form_submissions')

class ContactForm(BaseModel):
    name: str
    email: str
    company: str
    role: str

@app.post("/submit-form")
async def submit_form(form_data: ContactForm):
    try:
        # Save form data to a JSON file
        form_file_path = "form_submissions/submissions.json"
        
        # Check if the file exists and read the existing data
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

        return {"message": "Thank you for reaching out!"}

    except Exception as e:
        # If something goes wrong, raise an HTTP exception
        raise HTTPException(status_code=500, detail="Error saving form data")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))  # Use the PORT environment variable or fallback to 8000 for local testing
    uvicorn.run(app, host="0.0.0.0", port=port)