from skimage import measure
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft2, fftshift, ifft2

def load_image(src: str = "/home/usuario/elm/FURIO/src/data/failure.jpeg") -> tuple[np.ndarray, np.ndarray]:
    # Load the image and convert it to grayscale
    image = Image.open(src)
    original_image = Image.open(src).convert("L")
    image_array = np.array(original_image)
    return image, image_array

def fft_transform(image_array: np.array) -> np.ndarray:
    # Perform the Fourier transform and shift the zero frequency to the center
    fft_image = fft2(image_array)
    return fftshift(fft_image)

def gen_masks(image_array: np.array, low_threshold: float=0.15, upper_threshold: float=0.6) -> tuple[np.ndarray, np.ndarray]:
    fft_shifted = fft_transform(image_array)
    # Get the image dimensions and center
    rows, cols = fft_shifted.shape
    crow, ccol = rows // 2, cols // 2
    # Define radius for low and high frequency components
    radius_low = min(rows, cols) // 10   # Larger radius for broad features
    radius_high = min(rows, cols) // 40  # Smaller radius for fine details
    # Low-frequency mask
    low_freq_mask = np.zeros((rows, cols), dtype=bool)
    for i in range(rows):
        for j in range(cols):
            if np.sqrt((i - crow) ** 2 + (j - ccol) ** 2) < radius_low:
                low_freq_mask[i, j] = True

    # High-frequency mask
    high_freq_mask = np.ones((rows, cols), dtype=bool)
    for i in range(rows):
        for j in range(cols):
            if np.sqrt((i - crow) ** 2 + (j - ccol) ** 2) < radius_high:
                high_freq_mask[i, j] = False
    # Apply low-frequency mask
    low_freq_fft = fft_shifted * low_freq_mask
    low_freq_image = np.abs(ifft2(low_freq_fft))
    # Apply high-frequency mask
    high_freq_fft = fft_shifted * high_freq_mask
    high_freq_image = np.abs(ifft2(high_freq_fft))

    low_freq_image_normalized = low_freq_image - low_freq_image.min()
    low_freq_image_normalized /= low_freq_image_normalized.max()

    high_freq_image_normalized = high_freq_image - high_freq_image.min()
    high_freq_image_normalized /= high_freq_image_normalized.max()

    # Set threshold for binary mask (e.g., 0.5)
    high_freq_mask = high_freq_image_normalized >= low_threshold
    low_freq_mask = low_freq_image_normalized > upper_threshold

    return high_freq_mask, low_freq_mask

def visualize_results(image: np.ndarray, high_freq_mask: np.ndarray, low_freq_mask: np.ndarray):
    # Plot probability map and binary mask
    fig, axs = plt.subplots(1, 3, figsize=(4 * 3, 6))
    # Original Image
    axs[0].imshow(image)
    axs[0].set_title("Original Image")
    # Binary mask (0 or 1 values)
    axs[1].imshow(high_freq_mask, cmap='gray')
    axs[1].set_title("High-Frequency Mask")
    axs[1].axis("off")
    axs[2].imshow(low_freq_mask, cmap='gray')
    axs[2].set_title("Low-Frequency Mask")
    axs[2].axis("off")

    plt.tight_layout()
    plt.show()