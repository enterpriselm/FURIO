import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
import cv2
from sklearn.cluster import DBSCAN

def adaptive_threshold(image):
    _, binary_mask = cv2.threshold(image, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary_mask

def fft_segmentation_adaptive(image, percentile=0.5):
    if len(image.shape) == 3:
        h, w, z = image.shape
    else:
        h, w = image.shape
        z = 1

    combined_mask = np.zeros((h, w), dtype=np.uint32)
    
    for band in range(z):
        band_data = image[:, :, band] if z > 1 else image

        F = fftpack.fftshift(fftpack.fft2(band_data))
        spectrum = np.abs(F)
        
        highpass_radius = int(np.percentile(spectrum, percentile))

        y, x = np.ogrid[:h, :w]
        center_y, center_x = h // 2, w // 2
        mask = (x - center_x)**2 + (y - center_y)**2 > highpass_radius**2
        F_filtered = F * mask

        filtered_image = np.abs(fftpack.ifft2(fftpack.ifftshift(F_filtered)))

        prob_map = (filtered_image - filtered_image.min()) / (filtered_image.max() - filtered_image.min())
        combined_mask = np.maximum(combined_mask, prob_map)

    return combined_mask

def apply_clustering(prob_mask, eps=0.1, min_samples=10):
    h, w = prob_mask.shape
    prob_mask_1d = prob_mask.reshape(-1, 1)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(prob_mask_1d)
    
    cluster_image = clusters.reshape(h, w)

    return cluster_image

images_path = ['src/data/Screenshot from 2024-11-01 08-24-58.png', 'src/data/failure.jpeg', 'src/data/normal.jpeg']
for image_path in images_path:
    img = cv2.imread(image_path)

    segmented_mask = fft_segmentation_adaptive(img)

    clustered_image = apply_clustering(segmented_mask, eps=0.05, min_samples=50)

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    plt.title("Original Image")
    plt.imshow(img)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Probability Map")
    plt.imshow(segmented_mask, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Clusters")
    plt.imshow(clustered_image, cmap="tab10")
    plt.axis("off")

    plt.show()