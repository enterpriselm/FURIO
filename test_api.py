import requests

# URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/generate_masks/"

# Path to the image you want to upload
image_path = "failure.jpeg"

# Threshold parameters
low_threshold = 0.15
upper_threshold = 0.6

# Open the image file in binary mode
with open(image_path, "rb") as image_file:
    # Define the files and data to be sent in the request
    files = {"file": image_file}
    data = {
        "low_threshold": low_threshold,
        "upper_threshold": upper_threshold,
    }

    # Send the POST request
    response = requests.post(url, files=files, data=data)

# Check the response status code
if response.status_code == 200:
    # Print the JSON response containing the base64 masks
    result = response.json()
    print("High Frequency Mask (Base64):", result["high_frequency_mask"])
    print("Low Frequency Mask (Base64):", result["low_frequency_mask"])
else:
    print("Error:", response.status_code)
    print(response.text)

import base64
with open("output.html", "w") as f:
    f.write(f'<html><body><h1>Base64 Image</h1><img src="data:image/png;base64,{result["high_frequency_mask"]}" alt="Base64 Image"/></body></html>')