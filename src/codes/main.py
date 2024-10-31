import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_derivative(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dy = np.diff(img, axis=0, append=img[-1:, :])
    dx = np.diff(img, axis=1, append=img[:, -1:])
    return dx, dy

def get_fft(np_array: np.ndarray) -> np.ndarray:
    fft_array = np.fft.fft(np_array)
    fft_abs = np.abs(fft_array)
    return fft_abs[:,:,0]

def load_img(img_file: str) -> np.ndarray:
    return cv2.imread(img_file)

def split_imgs(img: np.ndarray) -> dict[np.ndarray, list, list, list]:
    X, Y = KERNEL_SIZE[0], KERNEL_SIZE[1]

    splitted_imgs, coords_x, coords_y = [], [], []
    for i in range(0, img.shape[0] - X, X):
        for j in range(0, img.shape[1] - Y, Y):
            splitted_imgs.append(img[i:i + X, j:j + Y])
            coords_x.append(i)
            coords_y.append(j)
    return {"splitted_imgs":splitted_imgs, "x":np.array(coords_x), "y": np.array(coords_y)}

def get_data(img_file) -> tuple[np.array, dict, float, float]:
    img = load_img(img_file)
    splitted_imgs_dict = split_imgs(img) # Returns a dictionary with the splitted images and their coordinates
    return img, splitted_imgs_dict

# The following methods are used to estimate the distance between lines and the number of lines from fft
def measure(fft_array: np.ndarray) -> tuple[list, list]:
    total_distances, number_lines = [], []

    for idx in range(0, len(fft_array)):
        fft_interval = fft_array[idx]
        threshold = 2 * np.mean(fft_interval)
        lines = np.nonzero(fft_interval < threshold)[0] # Get the values of fft that are not far from the mean
    
        if len(lines) <= 2:
            distances = [0.0]
        else:
            distances = []
    
            for i in range(0, len(lines) - 2, 2):
                distances.append(np.abs(lines[i + 1] - lines[i + 2])) # For each value in lines, get the difference for the next value
    
        distances = np.array(distances)[np.nonzero(distances)]
        distances = distances[distances>1]
        px_dist = np.mean(distances).item()
        total_distances.append(px_dist)
        number_lines.append(len(lines) // 4)
    total_distances = np.nan_to_num(np.array(total_distances), nan=0)
    return total_distances, number_lines            

def evaluation(splitted_imgs: dict):
    results = {"distance_mag": [], "distance_x": [], "distance_y": [], "theta": [], "number_lines": []}
    for splitted_img in splitted_imgs:
        dx, dy = get_derivative(splitted_img)
        fft_x, fft_y = get_fft(dx), get_fft(dy)
        
        distances_x, lines_x = measure(fft_x)
        distances_y, lines_y = measure(fft_y)
        
        distance_mag = np.sqrt(distances_x**2 + distances_y**2) # Get the magnitude of the distance by the Pythagorean theorem
        number_lines = np.sqrt(np.array(lines_x)**2 + np.array(lines_y)**2) # Get the number of lines by the Pythagorean theorem
        
        distances_x = np.nanmean(distances_x)
        distances_y = np.nanmean(distances_y)
        number_lines = np.nanmean(number_lines)
        distance_mag = np.nanmean(distance_mag)

        results['distance_mag'].append(distance_mag)
        results['distance_x'].append(distances_x)
        results['distance_y'].append(distances_y)
        results['number_lines'].append(number_lines)
        
    return results