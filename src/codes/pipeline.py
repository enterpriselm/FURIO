from src.codes.main import get_data, evaluation
import numpy as np
import matplotlib.pyplot as plt

img_file = '/home/yan/studies/elm/FURIO/src/data/failure.jpeg'

for i in range(1,10):
    KERNEL_SIZE: tuple[int, int] = (2**i,2**i)
    img, splitted_imgs = get_data(img_file)
    results = evaluation(splitted_imgs['splitted_imgs'])
    distance = np.array(results['distance_mag'])
    distance_dim = int(np.sqrt(distance.size))
    desired_shape = (distance_dim, distance_dim)
    required_size = np.prod(desired_shape)
    if distance.size < required_size:
        padded_array = np.pad(distance, (0, required_size - distance.size), 'constant')
    elif distance.size > required_size:
        padded_array = distance[:required_size]
    else:
        padded_array = distance

    reshaped_array = padded_array.reshape(desired_shape)
    plt.axis("off")
    plt.imshow(reshaped_array)
    plt.show()