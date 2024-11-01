import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Applying FFT for segmentation
# Perform FFT on the grayscale image
fft_image = np.fft.fft2(gray)
fft_shift = np.fft.fftshift(fft_image)
# Create a mask for filtering - high-pass filter to keep only high frequencies (edges)
rows, cols = gray.shape
crow, ccol = rows // 2, cols // 2  # Center of the frequency image
mask = np.ones((rows, cols), np.uint8)
mask[crow-30:crow+30, ccol-30:ccol+30] = 0  # Block low frequencies
# Apply mask and inverse FFT
filtered_fft = fft_shift * mask
ifft_shift = np.fft.ifftshift(filtered_fft)
filtered_image = np.fft.ifft2(ifft_shift)
filtered_image = np.abs(filtered_image)
# Normalize and threshold the filtered image for segmentation
filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX)
_, binary_mask_fft = cv2.threshold(filtered_image, 60, 255, cv2.THRESH_BINARY)
# Display the result
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Filtered Image (Frequency Domain)")
plt.imshow(np.log(1 + np.abs(fft_shift)), cmap='gray')
plt.subplot(1, 2, 2)
plt.title("Segmented Mask (Using FFT)")
plt.imshow(binary_mask_fft, cmap='gray')
plt.show()