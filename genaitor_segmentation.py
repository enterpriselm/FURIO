import requests
import cv2

LLAMA_API_URL = 'http://localhost:8080/v1/chat/completions'
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer no-key"
}

SYSTEM_MESSAGE = """You're an expert in image segmentation. The user will pass you an array of an image and you should segmentate the image and generate a new array with the data segmentated 
(for example, if you think there are two patterns, you should return an array of 0s and 1s).
You should only return the array as the answer. Nothing less, nothing more. Just the array of segmentated image you have done."""

image_path = '/home/yan/studies/elm/FURIO/src/data/normal.jpeg'
img = cv2.imread(image_path)

payload = {
    "model": "LLaMA_CPP",
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE
        },
        {
            "role": "user",
            "content": f"{img}"
        }
    ]
}

response = requests.post(LLAMA_API_URL, headers=HEADERS, json=payload)
furio_array_str = response.json()["choices"][0]["message"]["content"]