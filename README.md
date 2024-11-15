# FURIO API

FURIO API is a web service that provides functionality for processing images to generate frequency masks and supports an upload form for handling image thresholding. The project includes an endpoint for mask generation, as well as a simple HTML front-end with forms to interact with the backend.

## Features

Image Upload: Upload an image and set threshold values for mask generation.

Frequency Masks Generation: Generates high and low-frequency masks for uploaded images.

Form Submission: Submit additional contact information to the API via an endpoint.

HTML Documentation: Accessible API documentation available at /documentation.


Project Structure

FURIO/
├── api.py                # Main FastAPI app
├── templates/
│   └── documentation.html  # HTML documentation file
├── static/                # Static assets (CSS, JavaScript, images)
│   ├── style.css
│   ├── script.js
│   └── logo.png
└── README.md              # Project README

Requirements

Python 3.7+

FastAPI

Uvicorn (for running the app)


Install dependencies using:

pip install -r requirements.txt

Endpoints

1. /generate_masks/ (POST)

Description: Generates high and low-frequency masks for an uploaded image based on provided threshold values.

Parameters:

file: (File) The image file to process.

low_threshold: (Float) Lower threshold for mask generation.

upper_threshold: (Float) Upper threshold for mask generation.


Response: JSON with base64-encoded strings for original, high-frequency, and low-frequency masks.


2. /submit-form (POST)

Description: Collects user contact information.

Parameters:

name: (String) Name of the user.

email: (String) Email address of the user.

company: (String) Company name of the user.

role: (String) User's role in the company.


Response: JSON message confirming form submission.


3. /documentation (GET)

Description: Serves an HTML page with API documentation.

Response: HTML response displaying documentation details.


Front-End Usage

To interact with the API, you can use the HTML interface provided. The HTML file includes a form for image upload and threshold input and is designed to send requests to the generate_masks API.

Ensure that:

apiUrl in the JavaScript is correctly set to your API endpoint.


Running the App

Start the application with Uvicorn:

uvicorn main:app --reload

By default, the app will run on http://127.0.0.1:8000.

Deployment

This application is configured to run on Render. To deploy:

1. Connect your GitHub repository to Render.


2. Set up the following environment variables:

API_URL: URL for the deployed API.



3. Configure the build and start commands in the Render dashboard:

Build Command: npm run setup

Start Command: venv/bin/uvicorn api.api:app --host 0.0.0.0 --port $PORT




Usage

Upload an Image: Navigate to / in your browser, upload an image, set thresholds, and submit to receive frequency masks.

View Documentation: Access /documentation for the HTML documentation.


License

This project is licensed under the MIT License.