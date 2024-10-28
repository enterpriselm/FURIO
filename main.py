import cv2
import matplotlib.pyplot as plt
import numpy as np


class FurioPipeline():
    
    N_SAMPLES = 10

    @staticmethod
    def load_img(img_file: str) -> np.ndarray:
        return cv2.imread(img_file)

    @classmethod
    def get_data(cls, img_file: str) -> tuple[dict, float, float]:
        img = cls.load_img(img_file)
        splitted_imgs = cls.split_imgs(img)
        return splitted_imgs

    @staticmethod
    def get_derivative(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        dy = np.diff(img, axis=0, append=img[-1:, :])
        dx = np.diff(img, axis=1, append=img[:, -1:])
        return dx, dy

    @staticmethod
    def get_fft(img: np.ndarray) -> np.ndarray:
        fft_img = np.fft.fft(img)
        fft_abs = np.abs(fft_img)
        return fft_abs[:,:,0]

    @classmethod
    def split_imgs(cls, img: np.ndarray) -> dict[np.ndarray, list, list, list]:
        splitted_imgs = []
        coords_x = []
        coords_j = []
        X, Y = img.shape[0] // cls.N_SAMPLES, img.shape[1] // cls.N_SAMPLES
        for i in range(0, img.shape[0] - X, X):
            for j in range(0, img.shape[1] - Y, Y):
                splitted_imgs.append(img[i:i + X, j:j + Y])
                coords_x.append((i, i + X))
                coords_j.append((j, j + Y))
        return {"original_img": img, "splitted_imgs": splitted_imgs, "x": coords_x, "y": coords_j}

    @staticmethod
    def measure(fft_array: np.ndarray) -> tuple[list, list]:
        total_distances = []
        number_lines = []
        for idx in range(0, len(fft_array)):
            fft_interval = fft_array[idx]
            threshold = 2 * np.mean(fft_interval)
            lines = np.nonzero(fft_interval < threshold)[0]
            if len(lines) <= 2:
                distances = [0.0]
            else:
                distances = []
                for i in range(0, len(lines) - 2, 2):
                    distances.append(np.abs(lines[i + 1] - lines[i + 2]))

            distances = np.array(distances)[np.nonzero(distances)]
            px_dist = np.mean(distances).item()

            total_distances.append(px_dist)
            number_lines.append(len(lines) // 4)
        return total_distances, number_lines

    @staticmethod
    def get_distance(distances_x: list, distances_y: list) -> tuple[float, float]:
        mean_dx = np.mean(distances_x).item()
        mean_dy = np.mean(distances_y).item()
        if float(mean_dy) == 0.0:
            theta = 0.0
        else:
            theta = np.arctan(mean_dx / mean_dy).item()
        return ((np.sqrt(mean_dx**2 + mean_dy**2)) * np.sin(theta)).item(), theta

    @staticmethod
    def get_number_lines(lines_x: list, lines_y: list) -> int:
        mean_xlines = np.mean(lines_x).item()
        mean_ylines = np.mean(lines_y).item()
        if float(mean_ylines) == 0.0:
            theta = 0.0
        else:
            theta = np.arctan(mean_xlines / mean_ylines).item()
        return int(((np.sqrt(mean_xlines**2 + mean_ylines**2)) * np.sin(theta)).item())

    @classmethod
    def evaluation(cls, splitted_imgs: dict):
        results = {"original_img": splitted_imgs["original_img"], "idx": [],
                    "distance_mag": [], "distance_u": [], "distance_v": [],
                    "theta": [], "number_lines": [],
                    "x": splitted_imgs["x"], "y": splitted_imgs["y"]}

        for count, splitted_img in enumerate(splitted_imgs["splitted_imgs"]):
            dx, dy = cls.get_derivative(splitted_img)
            fft_x, fft_y = cls.get_fft(dx), cls.get_fft(dy)

            distances_x, lines_x = cls.measure(fft_x)
            distances_y, lines_y = cls.measure(fft_y)

            distances_x = np.nan_to_num(np.array(distances_x), nan=0)
            distances_y = np.nan_to_num(np.array(distances_y), nan=0)

            distance, theta = cls.get_distance(distances_x, distances_y)
            number_lines = cls.get_number_lines(lines_x, lines_y)
            
            indexes = ["idx", "distance_mag", "distance_u", "distance_v", "theta", "number_lines"]
            values = [count, distance, np.mean(distances_x).item(),
                        -np.mean(distances_y).item(), theta, number_lines]
            for i in range(len(values)):
                results[indexes[i]].append(values[i])
            count+=1
        return results

    @staticmethod
    def get_plot_data(results):
        distances = results["distance_mag"]
        img = results["original_img"]
        heatmap_dim = [int(np.sqrt(len(distances))), int(np.sqrt(len(distances)))]
        x_quiver, y_quiver = np.meshgrid(np.linspace(0, img.shape[1], heatmap_dim[0]),
                                            np.linspace(0, img.shape[0], heatmap_dim[1]))
        y_quiver = img.shape[0] - y_quiver
        u = np.array(results["distance_u"])
        v = np.array(results["distance_v"])
        return img, x_quiver, y_quiver, u, v, distances

    @classmethod
    def gen_carousel(cls, results):
        
        img,x_quiver,y_quiver,u,v,distances = cls.get_plot_data(results)

        plt.style.use("dark_background")
        fig, ax = plt.subplots(1, 3, figsize=(10, 4), gridspec_kw={"width_ratios": [10, 10, 1]})

        ax[0].imshow(img)
        ax[0].set_title("Original Image")
        ax[0].axis("off")

        quiv = ax[1].quiver(x_quiver, y_quiver, u, v, distances, width=0.015, cmap='hot', scale=60, alpha=0.8)
        ax[1].set_title("Distance Map")
        ax[1].axis("off")

        plt.colorbar(quiv, cax=ax[2])
        plt.show()
        return fig

    @classmethod
    def gen_heatmap(cls, results):

        img,x_quiver,y_quiver,u,v,distances = cls.get_plot_data(results)

        plt.style.use("dark_background")
        fig, ax = plt.subplots(1, 2, figsize=(16, 12), gridspec_kw={"width_ratios": [10, 1]})

        quiv = ax[0].imshow(img, aspect='auto')
        quiv = ax[0].quiver(x_quiver, y_quiver, u, v, distances, width=0.015, cmap='hot', scale=60, alpha=0.8)
        ax[0].axis("off")

        plt.colorbar(quiv, cax=ax[1])
        plt.show()
        return fig

    @classmethod
    def plot_results(cls, results: dict):

        fig1 = cls.gen_carousel(results)
        fig2 = cls.gen_heatmap(results)

        return fig1, fig2